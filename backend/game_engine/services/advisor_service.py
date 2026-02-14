"""
AI advisor triggers and contextual chatbot logic.

Handles: checking proactive advice triggers, chatbot character triggers,
and processing scam choices.
"""
import random
import logging

from ..models import RecurringExpense
from ..advisor import GROQ_AVAILABLE as GENAI_AVAILABLE, get_advisor, AdvisorPersona
from .config import GameEngineConfig

logger = logging.getLogger(__name__)


class AdvisorService:
    """Proactive AI advice and contextual chatbot characters."""

    @staticmethod
    def _check_advisor_triggers(session):
        """Check for events that warrant proactive advice (legacy fallback)."""
        advisor = get_advisor()
        msg = None

        if session.wealth < 5000:
            msg = advisor.get_proactive_message("CRISIS", "Wealth dropped below 5k", session.wealth, session.happiness, AdvisorPersona.STRICT)
        elif session.wealth > 100000 and session.current_month % 6 == 0:
            msg = advisor.get_proactive_message("MILESTONE", "Wealth over 100k", session.wealth, session.happiness, AdvisorPersona.SASSY)
        elif session.happiness < 30:
            msg = advisor.get_proactive_message("WARNING", "Happiness dangerously low", session.wealth, session.happiness, AdvisorPersona.FRIENDLY)
        elif session.recurring_expenses > (25000 * 0.6):
            msg = advisor.get_proactive_message("DANGER", "Expenses > 60% of income", session.wealth, session.happiness, AdvisorPersona.STRICT)

        return msg

    @staticmethod
    def _check_chatbot_triggers(session):
        """
        Check game state and trigger the appropriate contextual chatbot character.
        Returns a dict suitable for frontend ChatOverlay, or None.

        Trigger Priority:
        1. Vasooli Bhai: Debt crisis (EMI missed / Debt > 50% net worth)
        2. Sundar (Scamster): Random trigger (~10% chance per month)
        3. Harshad (Risk Taker): Cash > 50k and Portfolio empty
        4. Jetta Bhai (Business): Profile == Business OR sustained losses
        """
        CONFIG = GameEngineConfig.CONFIG
        advisor = get_advisor()

        # --- Calculate Net Worth ---
        portfolio_value = 0
        portfolio_empty = True
        if session.portfolio and session.market_prices:
            for sector, units in session.portfolio.items():
                if units > 0:
                    portfolio_empty = False
                price = session.market_prices.get(sector, 0)
                portfolio_value += int(units * price)
        net_worth = session.wealth + portfolio_value

        # --- Calculate Debt Ratio ---
        debt_expenses = RecurringExpense.objects.filter(
            session=session, category='DEBT', is_cancelled=False
        )
        total_debt_emi = sum(e.amount for e in debt_expenses)
        debt_ratio = total_debt_emi / max(net_worth, 1) if net_worth > 0 else 1.0

        # --- 1. VASOOLI BHAI: Debt Crisis ---
        if session.credit_score < 600 or debt_ratio > 0.5:
            msg = advisor.get_character_message(
                character='vasooli',
                trigger_reason=f"Debt EMI is ₹{total_debt_emi}/mo, which is {debt_ratio * 100:.0f}% of net worth",
                current_wealth=session.wealth,
                current_happiness=session.happiness,
            )
            return {
                'character': msg.character,
                'message': msg.message,
                'choices': msg.choices,
                'is_scam': msg.is_scam,
                'scam_loss_amount': msg.scam_loss_amount,
            }

        # --- 2. SUNDAR: Random Scam (10% chance, only if wealth > 10k) ---
        if session.wealth > 10000 and random.random() < 0.10:
            msg = advisor.get_character_message(
                character='sundar',
                trigger_reason=f"Player has ₹{session.wealth:,} cash — ripe for a scam",
                current_wealth=session.wealth,
                current_happiness=session.happiness,
            )
            return {
                'character': msg.character,
                'message': msg.message,
                'choices': msg.choices,
                'is_scam': msg.is_scam,
                'scam_loss_amount': msg.scam_loss_amount,
            }

        # --- 3. HARSHAD: Cash hoarding + no portfolio ---
        if session.wealth > 50000 and portfolio_empty:
            msg = advisor.get_character_message(
                character='harshad',
                trigger_reason=f"Cash ₹{session.wealth:,} sitting idle with zero portfolio",
                current_wealth=session.wealth,
                current_happiness=session.happiness,
            )
            return {
                'character': msg.character,
                'message': msg.message,
                'choices': msg.choices,
                'is_scam': msg.is_scam,
                'scam_loss_amount': msg.scam_loss_amount,
            }

        # --- 4. JETTA: Business profile or sustained losses ---
        is_business = False
        try:
            persona = session.persona_profile
            if persona and persona.career_stage == 'BUSINESS_OWNER':
                is_business = True
        except Exception:
            pass

        # Check Cash Flow (Expenses > Income)
        total_income = sum(src.amount_base for src in session.income_sources.all())
        # Fallback if no income sources yet (rare)
        if total_income == 0: 
            total_income = 1 # Prevent div by zero logical errors if needed, but here just comparison

        is_deficit = session.recurring_expenses > total_income

        if is_business or is_deficit:
            msg = advisor.get_character_message(
                character='jetta',
                trigger_reason=(
                    f"Expenses (₹{session.recurring_expenses}) > Income (₹{total_income})"
                    if not is_business
                    else "Business Owner profile — Jetta Bhai monitors your margins"
                ),
                current_wealth=session.wealth,
                current_happiness=session.happiness,
            )
            return {
                'character': msg.character,
                'message': msg.message,
                'choices': msg.choices,
                'is_scam': msg.is_scam,
                'scam_loss_amount': msg.scam_loss_amount,
            }

        return None

    @staticmethod
    def process_scam_choice(session, accepted: bool, scam_loss_amount: int):
        """
        Handle the player's response to Sundar's scam offer.
        """
        from .game_service import GameService

        if accepted:
            session.wealth -= scam_loss_amount
            session.happiness -= 15
            session.financial_literacy -= 5
            session.happiness = GameService._clamp(session.happiness, 0, 100)
            session.financial_literacy = max(0, session.financial_literacy)

            GameService._append_gameplay_log(
                session,
                f"Month {session.current_month}: FELL FOR SCAM! Lost ₹{scam_loss_amount} to Sundar's scheme.",
            )
            session.save()

            game_over, reason = GameService._check_game_over(session)
            if game_over:
                from . import GameEngine
                GameEngine._finalize_game(session, reason)

            return {
                'message': (
                    f"💀 SCAM ALERT! Sundar vanished with your ₹{scam_loss_amount:,}! "
                    f"This is how Ponzi schemes work — if it's too good to be true, it is!"
                ),
                'session': session,
                'game_over': game_over,
                'game_over_reason': reason,
            }
        else:
            session.financial_literacy += 5
            GameService._append_gameplay_log(
                session,
                f"Month {session.current_month}: Ignored Sundar's scam. Smart move!",
            )
            session.save()

            return {
                'message': (
                    '✅ Smart move! You avoided a scam. '
                    'Remember: guaranteed high returns = guaranteed fraud!'
                ),
                'session': session,
                'game_over': False,
                'game_over_reason': None,
            }
