"""
Core game session management and gameplay logic.

Handles: session creation, card selection, choice processing,
skip penalties, month advancement, and utility helpers.
"""
import os
import random
import logging
import uuid

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from ..models import (
    GameSession, PlayerChoice, RecurringExpense, ScenarioCard,
    StockHistory, IncomeSource, MarketTickerData, PersonaProfile
)
from ..ml.predictor import AIStockPredictor
from ..advisor import GROQ_AVAILABLE as GENAI_AVAILABLE, get_advisor, AdvisorPersona
from ..ai_engine import get_ai_master

from .config import GameEngineConfig

logger = logging.getLogger(__name__)


class GameService:
    """Session management and core gameplay loop."""

    # ================= SECURITY =================
    @staticmethod
    def validate_ownership(user, session):
        """
        SECURITY CRITICAL: Ensure the session belongs to the requesting user.
        Raises PermissionDenied if mismatch.
        """
        if session.user != user:
            raise PermissionDenied("You do not own this game session.")

    # ================= SESSION MANAGEMENT =================
    @staticmethod
    def start_new_session(user):
        """Initialize a new game session with defaults."""
        from django.db import transaction
        CONFIG = GameEngineConfig.CONFIG

        with transaction.atomic():
            session = GameSession.objects.create(
                user=user,
                wealth=CONFIG['STARTING_WEALTH'],
                happiness=CONFIG['HAPPINESS_START'],
                credit_score=CONFIG['CREDIT_SCORE_START'],
                current_month=CONFIG['START_MONTH']
            )
        
        # --- Generate Persona & Income ---
        # Randomly assign a career stage for variety, or could be user-selected in future
        career_stage = random.choice(PersonaProfile.CareerStage.values)
        
        # Adjust starting stats based on Career
        if career_stage == 'STUDENT_FULLY_FUNDED':
            session.wealth = 5000
            session.credit_score = 650
            income_amount = 5000
            income_source = 'ALLOWANCE'
        elif career_stage == 'STUDENT_PART_TIME':
            session.wealth = 10000
            session.credit_score = 680
            income_amount = 8000
            income_source = 'FREELANCE'
        elif career_stage == 'FRESHER':
            session.wealth = 20000
            session.credit_score = 700
            income_amount = 25000
            income_source = 'SALARY'
        elif career_stage == 'PROFESSIONAL':
            session.wealth = 100000
            session.credit_score = 750
            income_amount = 80000
            income_source = 'SALARY'
        elif career_stage == 'BUSINESS_OWNER':
            session.wealth = 50000
            session.credit_score = 720
            income_amount = 60000
            income_source = 'BUSINESS'
        elif career_stage == 'RETIRED':
            session.wealth = 500000
            session.credit_score = 800
            income_amount = 30000
            income_source = 'OTHER' # Pension
        
        session.current_level = GameService._calculate_level(session)
        session.market_trends = {s: 0 for s in CONFIG['STOCK_SECTORS']}
        session.save()
        
        # Create Persona Profile
        PersonaProfile.objects.create(
            session=session,
            career_stage=career_stage,
            responsibility_level=PersonaProfile.ResponsibilityLevel.MEDIUM, # Default
            risk_appetite=PersonaProfile.RiskAppetite.MEDIUM
        )
        
        # Create Primary Income Source
        IncomeSource.objects.create(
            session=session,
            source_type=income_source,
            amount_base=income_amount,
            variability=0.1 if income_source in ['BUSINESS', 'FREELANCE'] else 0.0,
            frequency='MONTHLY'
        )

        # --- Generate Deterministic Market History ---
        ticker = 'RELIANCE.NS'
        seed_qs = MarketTickerData.objects.filter(ticker=ticker).order_by('-date')[:60]

        initial_prices = {}

        if seed_qs.count() < 60:
            logger.warning("Insufficient seed data for AI. Using fallback simulation.")
            initial_prices = {"gold": 1800, "tech": 500, "real_estate": 300}

            for sector in CONFIG['STOCK_SECTORS']:
                prices = [initial_prices.get(sector, 100) for _ in range(12)]
                history_objs = [
                    StockHistory(session=session, sector=sector, month=i + 1, price=p)
                    for i, p in enumerate(prices)
                ]
                StockHistory.objects.bulk_create(history_objs)
        else:
            import pandas as pd
            seed_data = pd.DataFrame(list(seed_qs.values(
                'close', 'rsi', 'macd', 'signal', 'daily_return'
            )))
            seed_data = seed_data.iloc[::-1]

            predictor = AIStockPredictor(ticker='RELIANCE')
            tech_prices = predictor.generate_forecast(seed_data, months=12)

            history_objs = [
                StockHistory(session=session, sector='tech', month=i + 1, price=p)
                for i, p in enumerate(tech_prices)
            ]

            gold_prices = predictor._fallback_generator(1800, 12)
            history_objs += [
                StockHistory(session=session, sector='gold', month=i + 1, price=p)
                for i, p in enumerate(gold_prices)
            ]

            re_prices = predictor._fallback_generator(300, 12)
            history_objs += [
                StockHistory(session=session, sector='real_estate', month=i + 1, price=p)
                for i, p in enumerate(re_prices)
            ]

            StockHistory.objects.bulk_create(history_objs)

            initial_prices['tech'] = tech_prices[0]
            initial_prices['gold'] = gold_prices[0]
            initial_prices['real_estate'] = re_prices[0]

        # Initialize Mutual Fund NAVs
        for mf_key in CONFIG['MUTUAL_FUNDS']:
            initial_prices[f"MF_{mf_key}"] = 100

        session.market_prices = initial_prices
        session.portfolio = {s: 0 for s in CONFIG['STOCK_SECTORS']}
        session.save()

        # --- Initialize Monthly Bills ---
        default_expenses = [
            {'name': 'Rent (2BHK)', 'amount': 10000, 'category': 'HOUSING', 'is_essential': True, 'inflation': 0.05},
            {'name': 'Groceries', 'amount': 2500, 'category': 'FOOD', 'is_essential': True, 'inflation': 0.07},
            {'name': 'Utilities (Electricity/Water)', 'amount': 1000, 'category': 'UTILITIES', 'is_essential': True, 'inflation': 0.03},
            {'name': 'Transport (Metro/Bus)', 'amount': 1000, 'category': 'TRANSPORT', 'is_essential': True, 'inflation': 0.05}
        ]

        for exp in default_expenses:
            RecurringExpense.objects.create(
                session=session,
                name=exp['name'],
                amount=exp['amount'],
                category=exp['category'],
                is_essential=exp['is_essential'],
                inflation_rate=exp['inflation'],
                started_month=session.current_month
            )

        return session

    # ================= CORE GAMEPLAY =================
    @staticmethod
    def get_next_card(session):
        """
        Smart Scenario Selection with AI Integration.
        - 30% chance to generate a fresh AI scenario.
        - Fallback to DB deck if AI fails or skipped.
        - Avoids repeats.
        """
        CONFIG = GameEngineConfig.CONFIG
        GameService._refresh_level(session)

        # --- AI GENERATION ATTEMPT ---
        if random.random() < 0.3:
            try:
                profile = session.persona_profile
                if profile:
                    ai_master = get_ai_master()
                    level_categories = CONFIG['LEVEL_CARD_FILTERS'].get(
                        session.current_level,
                        CONFIG['LEVEL_CARD_FILTERS'][1]
                    )['categories']

                    category = random.choice(level_categories) if level_categories else "WANTS"

                    ai_card = ai_master.generate_scenario(
                        profile=profile,
                        wealth=session.wealth,
                        month=session.current_month,
                        category=category
                    )

                    if ai_card:
                        return ai_card
            except Exception as e:
                logger.warning("AI Generation failed: %s", e)

        # --- STANDARD DECK FALLBACK ---
        level_filters = CONFIG['LEVEL_CARD_FILTERS'].get(
            session.current_level,
            CONFIG['LEVEL_CARD_FILTERS'][1]
        )
        shown_ids = PlayerChoice.objects.filter(session=session).values_list('card_id', flat=True)

        available = ScenarioCard.objects.filter(
            is_active=True,
            is_generated=False,
            min_month__lte=session.current_month,
            difficulty__lte=level_filters['max_difficulty']
        ).exclude(id__in=shown_ids)

        if level_filters['categories']:
            available = available.filter(category__in=level_filters['categories'])

        if not available.exists():
            available = ScenarioCard.objects.filter(
                is_active=True,
                is_generated=False,
                min_month__lte=session.current_month
            ).exclude(id__in=shown_ids)

        if not available.exists():
            available = ScenarioCard.objects.filter(
                is_active=True,
                is_generated=False,
                min_month__lte=session.current_month
            )

        if not available.exists():
            return None

        return random.choice(list(available))

    @staticmethod
    def use_lifeline(session, card):
        """Reveal recommended choice."""
        if session.lifelines <= 0:
            return {'error': "No lifelines remaining."}

        session.lifelines -= 1
        session.save()

        rec_choice = card.choices.filter(is_recommended=True).first()

        if not rec_choice:
            rec_choice = card.choices.order_by('-happiness_impact').first()

        return {
            'success': True,
            'lifelines_remaining': session.lifelines,
            'hint': f"Advisor Suggests: {rec_choice.text}",
            'choice_id': rec_choice.id if rec_choice else None
        }

    @staticmethod
    def process_choice(session, card, choice):
        """Main game loop step."""
        # Late import to avoid circular dependency
        from . import GameEngine
        from django.db import transaction

        with transaction.atomic():
            GameService._append_gameplay_log(
                session,
                (
                    f"Month {session.current_month}: {card.title} — {choice.text}. "
                    f"Impact: wealth {choice.wealth_impact:+}, happiness {choice.happiness_impact:+}, "
                    f"credit {choice.credit_impact:+}, literacy {choice.literacy_impact:+}."
                ),
            )

            # 1. Apply Direct Impacts
            session.wealth += choice.wealth_impact
            session.happiness += choice.happiness_impact
            session.credit_score += choice.credit_impact
            session.financial_literacy += choice.literacy_impact

            session.happiness = GameService._clamp(session.happiness, 0, 100)
            session.credit_score = GameService._clamp(session.credit_score, 300, 900)

            feedback_parts = []
            if choice.feedback:
                feedback_parts.append(choice.feedback)

            # 2. Handle Recurring Expenses (Add/Remove)
            if choice.adds_recurring_expense > 0:
                RecurringExpense.objects.create(
                    session=session,
                    name=choice.expense_name or f"Expense from '{card.title}'",
                    amount=choice.adds_recurring_expense,
                    category='LIFESTYLE',
                    is_essential=False,
                    inflation_rate=0.04,
                    started_month=session.current_month
                )

            if choice.cancels_expense_name:
                expenses = session.expenses.filter(
                    name=choice.cancels_expense_name,
                    is_cancelled=False
                )
                count = expenses.update(
                    is_cancelled=True,
                    cancelled_month=session.current_month
                )
                if count > 0:
                    feedback_parts.append(f" (Cancelled {count} subscription(s)!)")

            # 3. Handle Market Events
            if card.market_event and card.market_event.is_active:
                event = card.market_event
                impacts = event.sector_impacts

                market_changes = []
                if session.market_prices:
                    for sector, multiplier in impacts.items():
                        if sector in session.market_prices:
                            old_price = session.market_prices[sector]
                            new_price = int(old_price * multiplier)
                            session.market_prices[sector] = new_price

                            trend_impact = 3 if multiplier > 1 else -3
                            session.market_trends[sector] = trend_impact

                            pct = int((multiplier - 1) * 100)
                            direction = "surged" if pct > 0 else "crashed"
                            market_changes.append(f"{sector.title()} {direction} {abs(pct)}%")

                if market_changes:
                    feedback_parts.append(f" 📉 MARKET NEWS: {', '.join(market_changes)}!")

            # 4. Log Choice
            PlayerChoice.objects.create(session=session, card=card, choice=choice)

            # 5. Advance Month Check
            CONFIG = GameEngineConfig.CONFIG
            choices_count = PlayerChoice.objects.filter(session=session).count()
            new_month = (choices_count // CONFIG['CARDS_PER_MONTH']) + 1

            if new_month > session.current_month:
                result = GameEngine.advance_month(session)

                feedback_parts.append(result['report'])

                if result['game_over']:
                    GameEngine._finalize_game(session, result['game_over_reason'])
                    return {
                        'session': session,
                        'feedback': " ".join(feedback_parts),
                        'game_over': True,
                        'game_over_reason': result['game_over_reason'],
                        'final_persona': GameEngine.generate_persona(session),
                        'chatbot': result.get('chatbot'),
                    }

            # 6. Check Game Over (Immediate)
            game_over, reason = GameService._check_game_over(session)
            if game_over:
                GameEngine._finalize_game(session, reason)

            return {
                'session': session,
                'feedback': " ".join(feedback_parts),
                'game_over': game_over,
                'game_over_reason': reason,
                'final_persona': GameEngine.generate_persona(session) if game_over else None,
                'chatbot': result.get('chatbot') if 'result' in locals() else None,
            }

    @staticmethod
    def process_skip(session, card):
        """
        Handle skipping a card.
        Variable penalties based on importance.
        """
        from . import GameEngine

        happiness_loss = 5
        credit_loss = 5

        if card.category in ['EMERGENCY', 'NEEDS']:
            happiness_loss = 15
            credit_loss = 20
        elif card.category == 'INVESTMENT':
            credit_loss = 10

        GameService._append_gameplay_log(
            session,
            (
                f"Month {session.current_month}: Skipped {card.title}. "
                f"Penalty: happiness -{happiness_loss}, credit -{credit_loss}."
            ),
        )

        session.happiness = max(0, session.happiness - happiness_loss)
        session.credit_score = max(300, session.credit_score - credit_loss)

        PlayerChoice.objects.create(session=session, card=card, choice=None)

        game_over, reason = GameService._check_game_over(session)
        if game_over:
            GameEngine._finalize_game(session, reason)
        else:
            session.save()

        return {
            'message': f"Skipped! Penalty: -{happiness_loss} Happiness, -{credit_loss} Credit Score.",
            'session': session,
            'game_over': game_over,
            'game_over_reason': reason
        }

    # ================= ECONOMICS & MONTH ADVANCEMENT =================
    @staticmethod
    def advance_month(session):
        """
        The Master Time Step Function.
        - Updates time
        - Applies expenses
        - Updates market
        - Checks game over
        """
        from . import GameEngine
        CONFIG = GameEngineConfig.CONFIG

        # 1. Advance Time
        session.current_month += 1
        report_lines = [f"📅 Month {session.current_month} Started!"]
        GameService._refresh_level(session)

        # 2. Income Processing
        total_income = 0
        income_report_lines = []

        income_sources = IncomeSource.objects.filter(session=session)

        for source in income_sources:
            amount = source.amount_base

            if source.source_type == IncomeSource.SourceType.FREELANCE:
                chance = random.random()
                if chance < 0.3:
                    amount = 0
                    income_report_lines.append("⚠️ No Freelance gig this month.")
                else:
                    amount = int(source.amount_base * random.uniform(0.8, 1.2))

            if amount > 0:
                total_income += amount
                income_report_lines.append(f"+₹{amount} from {source.get_source_type_display()}")

        if not income_sources.exists():
            total_income = CONFIG['MONTHLY_SALARY']
            income_report_lines.append(f"+₹{total_income} Salary credited.")

        session.wealth += total_income
        report_lines.extend(income_report_lines)

        # 2.5. SCAM / DATA BREACH CHECK (Instant Loan Risk)
        # If user has an active INSTANT_APP loan, 15% chance of data breach
        active_instant_loans = RecurringExpense.objects.filter(
            session=session, 
            name="High Interest Loan", 
            is_cancelled=False
        )
        if active_instant_loans.exists():
            if random.random() < 0.15:
                # Trigger Data Breach
                session.happiness -= 15
                report_lines.append("⚠️ DATA BREACH! Your loan app leaked your contacts. Harassment calls caused stress (-15 Happiness).")

        # 3. Recurring Expenses & Inflation
        active_expenses = session.expenses.filter(is_cancelled=False)
        total_monthly_drain = 0
        bill_report_lines = []

        apply_inflation = (session.current_month > 1) and (session.current_month % 12 == 1)

        for expense in active_expenses:
            if apply_inflation and expense.inflation_rate > 0:
                old_amount = expense.amount
                new_amount = int(old_amount * (1 + expense.inflation_rate))
                expense.amount = new_amount
                expense.save()
                bill_report_lines.append(f"📈 {expense.name} rose to ₹{new_amount} (+{(expense.inflation_rate * 100):.0f}%)")

            total_monthly_drain += expense.amount

        session.wealth -= total_monthly_drain
        session.recurring_expenses = total_monthly_drain

        report_lines.append(f"-₹{total_monthly_drain} Total Bills Paid.")
        if bill_report_lines:
            report_lines.append(" ".join(bill_report_lines))

        # 4. Market Update
        market_changes = GameEngine.update_market_prices(session)
        if market_changes:
            report_lines.append(f"Market Update: {', '.join(market_changes)}")

        # 4.5. IPO Listings
        updated_ipos = []
        for ipo in session.active_ipos:
            if ipo['status'] == 'APPLIED' and ipo['month'] < session.current_month:
                ipo_details = next((v for k, v in CONFIG['IPO_SCHEDULE'].items() if v['name'] == ipo['name']), None)

                listing_gain_pct = 0
                if ipo_details:
                    if random.random() < ipo_details['listing_gain_prob']:
                        listing_gain_pct = random.uniform(0.1, 0.8)
                    else:
                        listing_gain_pct = random.uniform(-0.3, -0.05)
                else:
                    listing_gain_pct = 0.1

                allotment_ratio = random.choice([0.0, 0.5, 1.0])

                invested = ipo['amount']
                allotted_value = invested * allotment_ratio
                refund = invested - allotted_value

                final_value = allotted_value * (1 + listing_gain_pct)

                total_credit = refund + final_value
                profit = total_credit - invested

                session.wealth += int(total_credit)

                if allotment_ratio == 0:
                    status_msg = "No allotment (Refunded)."
                elif profit > 0:
                    status_msg = f"LISTED WITH GAINS! Profit: ₹{int(profit)}"
                else:
                    status_msg = f"DISCOUNT LISTING. Loss: ₹{int(abs(profit))}"

                report_lines.append(f"🔔 IPO {ipo['name']}: {status_msg}")
                ipo['status'] = 'PROCESSED'
            else:
                updated_ipos.append(ipo)

        session.active_ipos = updated_ipos

        # 5. Natural Stat Decay
        if session.wealth < 10000:
            session.happiness -= 2
            report_lines.append("📉 Financial stress is affecting your happiness (-2).")

        if session.happiness > 90:
            session.happiness -= 1

        # 6. Check Game Over
        game_over, reason = GameService._check_game_over(session)

        session.save()

        if game_over:
            report_lines.append(f"GAME OVER: {reason}")

        # 7. Chatbot Trigger
        chatbot_data = None
        if not game_over:
            chatbot_data = GameEngine._check_chatbot_triggers(session)
            if chatbot_data:
                report_lines.append(f"💬 {chatbot_data['character'].upper()}: {chatbot_data['message']}")
            elif GENAI_AVAILABLE:
                advisor_msg = GameEngine._check_advisor_triggers(session)
                if advisor_msg:
                    report_lines.append(f"💬 Advisor: {advisor_msg}")

        return {
            'report': " ".join(report_lines),
            'game_over': game_over,
            'game_over_reason': reason,
            'chatbot': chatbot_data,
        }

    # ================= LOAN LOGIC =================
    @staticmethod
    def process_loan(session, loan_type):
        """Smart Loan System. Limit based on credit score."""
        CONFIG = GameEngineConfig.CONFIG
        GameService._refresh_level(session)

        if session.current_level < CONFIG['LEVEL_UNLOCKS']['loans']:
            return {'error': "Loans unlock at Level 2."}

        credit_limit = session.credit_score * 30

        if loan_type == 'FAMILY':
            amount = 5000
            if session.wealth + amount > 50000:
                return {'error': "You don't need a loan right now."}

            session.wealth += amount
            session.happiness -= 5
            msg = "Family helped with ₹5,000. Pay them back later!"

        elif loan_type == 'INSTANT_APP':
            amount = 10000
            if amount > credit_limit:
                return {'error': f"Loan rejected. Your credit limit is ₹{credit_limit}."}

            session.wealth += amount
            session.credit_score -= 50
            session.happiness += 5

            RecurringExpense.objects.create(
                session=session,
                name="High Interest Loan",
                amount=500,
                category='DEBT',
                is_essential=True,
                inflation_rate=0.0,
                started_month=session.current_month
            )
            msg = f"Loan approved: ₹{amount}. Credit score dropped. Monthly interest added."
        
        elif loan_type == 'BANK':
            amount = 100000
            if session.credit_score < 750:
                return {'error': "Bank Loan rejected. Requires Credit Score > 750."}
            
            session.wealth += amount
            # Bank loan doesn't drop credit score immediately, but adds EMI
            
            # EMI Calculation (Simple rule roughly 1% per month for safety in game balance)
            emi = 1200 
            
            RecurringExpense.objects.create(
                session=session,
                name="Bank Personal Loan",
                amount=emi,
                category='DEBT',
                is_essential=True,
                inflation_rate=0.0,
                started_month=session.current_month
            )
            msg = f"Bank Loan approved: ₹{amount}. EMI ₹{emi}/mo started."

        else:
            return {'error': "Invalid loan type"}

        session.save()
        return {'session': session, 'message': msg}

    # ================= UTILITIES =================
    @staticmethod
    def _clamp(val, min_val, max_val):
        return max(min_val, min(max_val, val))

    @staticmethod
    def _check_game_over(session):
        CONFIG = GameEngineConfig.CONFIG
        if session.wealth <= 0:
            return True, 'BANKRUPTCY'
        if session.happiness <= CONFIG['MIN_HAPPINESS']:
            return True, 'BURNOUT'
        if session.current_month > CONFIG['GAME_DURATION_MONTHS']:
            return True, 'COMPLETED'
        return False, None

    @staticmethod
    def _append_gameplay_log(session, entry):
        entry = entry.strip()
        if not entry:
            return
        if session.gameplay_log:
            session.gameplay_log = f"{session.gameplay_log}\n{entry}"
        else:
            session.gameplay_log = entry

    @staticmethod
    def _calculate_level(session):
        CONFIG = GameEngineConfig.CONFIG
        level = 1
        for threshold in CONFIG['LEVEL_THRESHOLDS']:
            if (
                session.current_month >= threshold['min_month']
                or session.financial_literacy >= threshold['min_literacy']
            ):
                level = threshold['level']
        return level

    @staticmethod
    def _refresh_level(session):
        next_level = GameService._calculate_level(session)
        if session.current_level != next_level:
            session.current_level = next_level
