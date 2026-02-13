"""
Persona generation, game-over finalization, and history recording.
"""
import os
import logging

from ..models import GameHistory, PlayerProfile
from ..advisor import GROQ_AVAILABLE as GENAI_AVAILABLE
from .config import GameEngineConfig, REPORT_PROMPT_TEMPLATE

# Optional: Google GenAI for final reports
try:
    from google import genai
except ImportError:
    genai = None

# ... (omitted lines)



logger = logging.getLogger(__name__)


class ReportService:
    """End-of-game persona, final report, and history persistence."""

    @staticmethod
    def _finalize_game(session, reason):
        """Mark session inactive, generate report, and persist history."""
        from . import GameEngine

        session.is_active = False
        if not session.final_report:
            session.final_report = ReportService._generate_final_report(session, reason)
        session.save()
        ReportService._save_history(session, reason)

    @staticmethod
    def _generate_final_report(session, reason):
        """Build an end-of-game report, optionally using Gemini."""
        portfolio_value = 0
        portfolio_lines = []
        if session.portfolio and session.market_prices:
            for sector, units in session.portfolio.items():
                price = session.market_prices.get(sector, 100)
                value = int(units * price)
                portfolio_value += value
                if units:
                    portfolio_lines.append(f"{sector.title()}: {units:.2f} units @ ₹{price} (₹{value})")
        portfolio_breakdown = "; ".join(portfolio_lines) if portfolio_lines else "No active holdings."
        gameplay_log = session.gameplay_log or "No gameplay log recorded."

        prompt = REPORT_PROMPT_TEMPLATE.format(
            reason=reason,
            current_month=session.current_month,
            wealth=session.wealth,
            happiness=session.happiness,
            credit_score=session.credit_score,
            financial_literacy=session.financial_literacy,
            recurring_expenses=session.recurring_expenses,
            portfolio_value=portfolio_value,
            portfolio_breakdown=portfolio_breakdown,
            gameplay_log=gameplay_log,
        )

        if GENAI_AVAILABLE and genai and os.environ.get('GEMINI_API_KEY'):
            try:
                client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt
                )
                if response and getattr(response, 'text', None):
                    return response.text.strip()
            except Exception as e:
                logger.error("GenAI report failed: %s", e)
                pass

        return (
            "## Summary\n"
            f"- Outcome: **{reason}** after month **{session.current_month}**.\n"
            f"- Final cash: **₹{session.wealth}**. Portfolio value: **₹{portfolio_value}**.\n"
            f"- Happiness: **{session.happiness}**. Credit score: **{session.credit_score}**.\n\n"
            "## Highlights\n"
            f"- Portfolio: {portfolio_breakdown}\n"
            f"- Recurring expenses: ₹{session.recurring_expenses}\n\n"
            "## Risks\n"
            "- Watch cash flow relative to recurring bills.\n"
            "- Keep credit score healthy by avoiding high-interest debt.\n\n"
            "## Recommendations\n"
            "- Build a 3–6 month emergency fund.\n"
            "- Automate savings with a monthly SIP.\n"
            "- Review recurring expenses and cancel low-value subscriptions.\n"
        )

    @staticmethod
    def _save_history(session, reason):
        """Persist a GameHistory record and update PlayerProfile stats."""
        from . import GameEngine

        persona_data = GameEngine.generate_persona(session)
        if session.user:
            portfolio_value = 0
            if session.portfolio and session.market_prices:
                for sector, units in session.portfolio.items():
                    price = session.market_prices.get(sector, 100)
                    portfolio_value += int(units * price)

            GameHistory.objects.create(
                user=session.user,
                final_wealth=session.wealth,
                final_happiness=session.happiness,
                final_credit_score=session.credit_score,
                financial_literacy_score=session.financial_literacy,
                persona=persona_data['persona'],
                end_reason=reason,
                months_played=session.current_month
            )
            profile, _ = PlayerProfile.objects.get_or_create(user=session.user)
            profile.total_games += 1
            profile.highest_wealth = max(profile.highest_wealth, session.wealth + portfolio_value)
            profile.highest_score = max(profile.highest_score, session.financial_literacy)
            profile.highest_credit_score = max(profile.highest_credit_score, session.credit_score)
            profile.highest_happiness = max(profile.highest_happiness, session.happiness)
            profile.highest_stock_profit = max(profile.highest_stock_profit, portfolio_value)
            profile.save()

    @staticmethod
    def generate_persona(session):
        """Generates the end-game player archetype."""
        w = session.wealth
        h = session.happiness
        s = session.financial_literacy

        if w > 100000 and h > 80:
            p, d = "The Financial Guru", "Mastered wealth AND happiness."
        elif w > 100000 and h < 40:
            p, d = "The Miser", "Rich but miserable."
        elif w < 10000 and h > 80:
            p, d = "The Happy-Go-Lucky", "Broke but smiling."
        elif s >= 80:
            p, d = "The Warren Buffett", "Strategic genius."
        elif s >= 50:
            p, d = "The Balanced Spender", "Good balance."
        else:
            p, d = "The FOMO Victim", "Driven by trends."

        return {
            'persona': p,
            'description': d,
            'final_score': s,
            'net_worth': w
        }
