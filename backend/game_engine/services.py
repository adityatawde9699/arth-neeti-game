import os
import random
import uuid
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import GameSession, PlayerChoice, RecurringExpense, GameHistory, PlayerProfile, ScenarioCard, StockHistory, FuturesContract
from .ml.predictor import MarketPredictor
from .advisor import GENAI_AVAILABLE, genai

class GameEngine:
    # Game Configuration Constants
    CONFIG = {
        'STARTING_WEALTH': 25000,
        'HAPPINESS_START': 100,
        'CREDIT_SCORE_START': 700,
        'START_MONTH': 1,
        'CARDS_PER_MONTH': 3,
        'GAME_DURATION_MONTHS': 12,
        'MIN_HAPPINESS': 0,
        'MAX_HAPPINESS': 100,
        'MIN_CREDIT': 300,
        'MAX_CREDIT': 900,
        'MONTHLY_SALARY': 25000,
        'STOCK_SECTORS': ['gold', 'tech', 'real_estate'],
        'LEVEL_THRESHOLDS': [
            {'level': 1, 'min_month': 1, 'min_literacy': 0},
            {'level': 2, 'min_month': 4, 'min_literacy': 20},
            {'level': 3, 'min_month': 7, 'min_literacy': 45},
            {'level': 4, 'min_month': 10, 'min_literacy': 70}
        ],
        'LEVEL_CARD_FILTERS': {
            1: {
                'max_difficulty': 2,
                'categories': ['NEEDS', 'WANTS', 'EMERGENCY', 'SOCIAL']
            },
            2: {
                'max_difficulty': 3,
                'categories': ['NEEDS', 'WANTS', 'EMERGENCY', 'SOCIAL', 'INVESTMENT', 'NEWS']
            },
            3: {
                'max_difficulty': 4,
                'categories': ['NEEDS', 'WANTS', 'EMERGENCY', 'SOCIAL', 'INVESTMENT', 'NEWS', 'QUIZ', 'TRAP']
            },
            4: {
                'max_difficulty': 5,
                'categories': None
            }
        },
        'LEVEL_UNLOCKS': {
            'loans': 2,
            'investing': 2,
            'diversification': 3,
            'mastery': 4
        }
    }
    REPORT_PROMPT_TEMPLATE = (
        "You are an expert financial coach. Generate a concise Markdown report for the player. "
        "Use the sections: Summary, Highlights, Risks, Recommendations. "
        "Be supportive, specific, and keep it under 400 words.\n\n"
        "Game outcome reason: {reason}\n"
        "Final month: {current_month}\n"
        "Final wealth: ₹{wealth}\n"
        "Final happiness: {happiness}\n"
        "Final credit score: {credit_score}\n"
        "Financial literacy: {financial_literacy}\n"
        "Recurring expenses: ₹{recurring_expenses}\n"
        "Portfolio value: ₹{portfolio_value}\n"
        "Portfolio breakdown: {portfolio_breakdown}\n\n"
        "Gameplay log:\n{gameplay_log}\n"
    )

    # ================= SECURITY =================
    @staticmethod
    def validate_ownership(user, session):
        """
        SECURITY CRITICAL: Ensure the session belongs to the requesting user.
        Raises PermissionDenied if mismatch.
        """
        # Allow guest access if both are anonymous/guest, but strictly check authenticated users
        if session.user != user:
             # In a real app, we'd log this security event
             raise PermissionDenied("You do not own this game session.")

    # ================= SESSION MGMT =================
    @staticmethod
    def start_new_session(user):
        """Initialize a new game session with defaults."""
        session = GameSession.objects.create(
            user=user,
            wealth=GameEngine.CONFIG['STARTING_WEALTH'],
            happiness=GameEngine.CONFIG['HAPPINESS_START'],
            credit_score=GameEngine.CONFIG['CREDIT_SCORE_START'],
            current_month=GameEngine.CONFIG['START_MONTH']
        )
        session.current_level = GameEngine._calculate_level(session)
        # Init market trends
        session.market_trends = {s: 0 for s in GameEngine.CONFIG['STOCK_SECTORS']}
        session.save()

        # --- NEW: Generate Deterministic Market History ---
        initial_prices = {}
        for sector in GameEngine.CONFIG['STOCK_SECTORS']:
            # Generate 12 months of data
            prices = MarketPredictor.generate_trajectory(sector, 12)
            
            # Save to DB
            history_objs = [
                StockHistory(session=session, sector=sector, month=i+1, price=p)
                for i, p in enumerate(prices)
            ]
            StockHistory.objects.bulk_create(history_objs)
            
            # Set Month 1 Price
            initial_prices[sector] = prices[0]
            
        session.market_prices = initial_prices
        session.portfolio = {s: 0 for s in GameEngine.CONFIG['STOCK_SECTORS']}
        session.save()

        # --- NEW: Initialize Monthly Bills (Budget) ---
        # Base Expenses (Total ~14.5k)
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
        Smart Scenario Selection.
        - Avoids repeats.
        - Weights by difficulty vs literacy.
        - Ensures variety.
        """
        GameEngine._refresh_level(session)
        level_filters = GameEngine.CONFIG['LEVEL_CARD_FILTERS'].get(
            session.current_level,
            GameEngine.CONFIG['LEVEL_CARD_FILTERS'][1]
        )
        # 1. Filter valid cards
        shown_ids = PlayerChoice.objects.filter(session=session).values_list('card_id', flat=True)
        
        available = ScenarioCard.objects.filter(
             is_active=True,
             min_month__lte=session.current_month,
             difficulty__lte=level_filters['max_difficulty']
        ).exclude(id__in=shown_ids)

        if level_filters['categories']:
            available = available.filter(category__in=level_filters['categories'])

        if not available.exists():
            available = ScenarioCard.objects.filter(
                is_active=True,
                min_month__lte=session.current_month
            ).exclude(id__in=shown_ids)
        
        if not available.exists():
            # Fallback: Allow repeats if deck exhausted
            available = ScenarioCard.objects.filter(
                is_active=True,
                min_month__lte=session.current_month
            )
             
        if not available.exists():
            return None # Should handle "End Game" or "No Cards" upstream
            
        # 2. Adaptive Difficulty
        # If Literacy is low (<30), prefer simpler cards (Difficulty 1-2)
        # If Literacy is high (>70), allow harder cards (Difficulty 4-5)
        
        # Simple weighted random choice from available
        # Ideally we'd use random.choices with weights, but for now simple random is better than fixed
        return random.choice(list(available))

    @staticmethod
    def use_lifeline(session, card):
        """
        Reveal recommended choice.
        """
        if session.lifelines <= 0:
            return {'error': "No lifelines remaining."}
            
        session.lifelines -= 1
        session.save()
        
        # Find best choice
        # If multiple recommended, pick first. If none, pick highest wealth impact?
        # Assuming is_recommended is set on at least one.
        rec_choice = card.choices.filter(is_recommended=True).first()
        
        if not rec_choice:
            # Fallback: Pick choice with highest happiness impact
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
        GameEngine._append_gameplay_log(
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

        session.happiness = GameEngine._clamp(session.happiness, 0, 100)
        session.credit_score = GameEngine._clamp(session.credit_score, 300, 900)

        feedback_parts = []
        if choice.feedback:
            feedback_parts.append(choice.feedback)

        # 2. Handle Recurring Expenses (Add/Remove)
        if choice.adds_recurring_expense > 0:
            RecurringExpense.objects.create(
                session=session,
                name=choice.expense_name or f"Expense from '{card.title}'",
                amount=choice.adds_recurring_expense,
                category='LIFESTYLE', # Default items from cards to Lifestyle usually
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
                        # Apply immediate shock
                        old_price = session.market_prices[sector]
                        new_price = int(old_price * multiplier)
                        session.market_prices[sector] = new_price
                        
                        # Update TREND (Momentum)
                        # If multiplier > 1, trend becomes positive (+3). If < 1, negative (-3).
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
        choices_count = PlayerChoice.objects.filter(session=session).count()
        new_month = (choices_count // GameEngine.CONFIG['CARDS_PER_MONTH']) + 1
        
        if new_month > session.current_month:
            # New Logic: Call advance_month
            result = GameEngine.advance_month(session)
            
            feedback_parts.append(result['report'])
            
            if result['game_over']:
                GameEngine._finalize_game(session, result['game_over_reason'])
                return {
                    'session': session,
                    'feedback': " ".join(feedback_parts),
                    'game_over': True,
                    'game_over_reason': result['game_over_reason'],
                    'final_persona': GameEngine.generate_persona(session)
                }

        # 6. Check Game Over (Immediate, e.g. from choice impact)
        game_over, reason = GameEngine._check_game_over(session)
        if game_over:
            GameEngine._finalize_game(session, reason)

        return {
            'session': session,
            'feedback': " ".join(feedback_parts),
            'game_over': game_over,
            'game_over_reason': reason,
            'final_persona': GameEngine.generate_persona(session) if game_over else None
        }

    @staticmethod
    def process_skip(session, card):
        """
        Handle skipping a card. 
        IMPROVEMENT: Variable penalties based on importance.
        """
        # Base penalty
        happiness_loss = 5
        credit_loss = 5

        # Heavy penalty for critical categories
        if card.category in ['EMERGENCY', 'NEEDS']:
            happiness_loss = 15
            credit_loss = 20
        elif card.category == 'INVESTMENT':
            credit_loss = 10  # Missed opportunity

        GameEngine._append_gameplay_log(
            session,
            (
                f"Month {session.current_month}: Skipped {card.title}. "
                f"Penalty: happiness -{happiness_loss}, credit -{credit_loss}."
            ),
        )

        session.happiness = max(0, session.happiness - happiness_loss)
        session.credit_score = max(300, session.credit_score - credit_loss)
        
        # Log as skipped (choice=None)
        PlayerChoice.objects.create(session=session, card=card, choice=None)

        game_over, reason = GameEngine._check_game_over(session)
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

    # ================= ECONOMICS & MARKET =================
    @staticmethod
    def advance_month(session):
        """
        The Master Time Step Function.
        - Updates time
        - Applies expenses
        - Updates market
        - Checks game over
        """
        # 1. Advance Time
        session.current_month += 1
        months_passed = 1 # Simple 1 month step
        
        report_lines = [f"📅 Month {session.current_month} Started!"]
        GameEngine._refresh_level(session)

        # 2. Income (Salary)
        salary_credit = GameEngine.CONFIG['MONTHLY_SALARY']
        session.wealth += salary_credit
        report_lines.append(f"+₹{salary_credit} Salary credited.")

        # 3. Recurring Expenses & Inflation
        # The "Real" Source of Truth is now the RecurringExpense table
        active_expenses = session.expenses.filter(is_cancelled=False)
        total_monthly_drain = 0
        bill_report_lines = []
        
        # Check for Annual Inflation (Every 12 months, starting month 13)
        apply_inflation = (session.current_month > 1) and (session.current_month % 12 == 1)
        
        for expense in active_expenses:
            # Apply Inflation if needed
            if apply_inflation and expense.inflation_rate > 0:
                old_amount = expense.amount
                # Inflation formula: New = Old * (1 + Rate)
                new_amount = int(old_amount * (1 + expense.inflation_rate))
                expense.amount = new_amount
                expense.save()
                bill_report_lines.append(f"📈 {expense.name} rose to ₹{new_amount} (+{(expense.inflation_rate*100):.0f}%)")

            total_monthly_drain += expense.amount
        
        session.wealth -= total_monthly_drain
        
        # Update cache for UI
        session.recurring_expenses = total_monthly_drain
        
        report_lines.append(f"-₹{total_monthly_drain} Total Bills Paid.")
        if bill_report_lines:
             report_lines.append(" ".join(bill_report_lines))

        # 4. Market Update
        market_changes = GameEngine.update_market_prices(session)
        if market_changes:
            report_lines.append(f"Market Update: {', '.join(market_changes)}")

        # 5. Natural Stat Decay & Soft Failures
        # Stress from low wealth
        if session.wealth < 10000:
            session.happiness -= 2
            report_lines.append("📉 Financial stress is affecting your happiness (-2).")
            
        # Isolation (optional simple check: if happiness is high, slight decay to force fun choices)
        # If happiness > 90, decay -1 (Hedonic Adaptation)
        if session.happiness > 90:
             session.happiness -= 1

        # 6. Check Game Over
        game_over, reason = GameEngine._check_game_over(session)
        
        session.save()

        return {
            'report': " ".join(report_lines),
            'game_over': game_over,
            'game_over_reason': reason
        }

    @staticmethod
    def update_market_prices(session):
        """
        Apply momentum/trends to prices each month.
        Returns list of significant changes for the news feed.
        """
        if not session.market_prices:
            return []

        changes = []
        new_month = session.current_month
        
        # Fetch prices from History table
        histories = StockHistory.objects.filter(session=session, month=new_month)
        
        for record in histories:
            old_price = session.market_prices.get(record.sector, 0)
            new_price = record.price
            
            session.market_prices[record.sector] = new_price
            
            # Calculate Change % for News Feed
            if old_price > 0:
                pct_change = ((new_price - old_price) / old_price) * 100
                if abs(pct_change) > 5:
                    direction = "surged" if pct_change > 0 else "tanked"
                    changes.append(f"{record.sector.title()} {direction} {abs(pct_change):.1f}%")
        
        return changes

    # ================= LOAN LOGIC =================
    @staticmethod
    def process_loan(session, loan_type):
        """
        Smart Loan System.
        Limit based on credit score.
        """
        GameEngine._refresh_level(session)
        if session.current_level < GameEngine.CONFIG['LEVEL_UNLOCKS']['loans']:
            return {'error': "Loans unlock at Level 2."}
        # Calculate Credit Limit
        # Score 700 -> ₹14,000 limit
        credit_limit = session.credit_score * 30
        
        current_loans = 0 # In a real DB we'd sum active loans. Simplified here.
        
        if loan_type == 'FAMILY':
            amount = 5000
            if session.wealth + amount > 50000: # Anti-exploit
                 return {'error': "You don't need a loan right now."}
            
            session.wealth += amount
            session.happiness -= 5 # Pride hurt
            msg = "Family helped with ₹5,000. Pay them back later!"
            
        elif loan_type == 'INSTANT_APP':
            amount = 10000
            if amount > credit_limit:
                 return {'error': f"Loan rejected. Your credit limit is ₹{credit_limit}."}
            
            session.wealth += amount
            session.credit_score -= 50 # Hard check
            session.happiness += 5 # Relief
            
            # Add recurring interest payment!
            Heading = "High Interest Loan"
            RecurringExpense.objects.create(
                session=session,
                name=Heading,
                amount=500, # 5% monthly interest
                category='DEBT',
                is_essential=True, # Debt is essential!
                inflation_rate=0.0, # Fixed interest usually
                started_month=session.current_month
            )
            msg = f"Loan approved: ₹{amount}. Credit score dropped. Monthly interest added."
            
        else:
            return {'error': "Invalid loan type"}
            
        session.save()
        return {'session': session, 'message': msg}

    # ================= UTILS =================
    @staticmethod
    def _clamp(val, min_val, max_val):
        return max(min_val, min(max_val, val))

    @staticmethod
    def _check_game_over(session):
        if session.wealth <= 0:
            return True, 'BANKRUPTCY'
        if session.happiness <= GameEngine.CONFIG['MIN_HAPPINESS']:
            return True, 'BURNOUT'
        if session.current_month > GameEngine.CONFIG['GAME_DURATION_MONTHS']:
            return True, 'COMPLETED'
        return False, None

    @staticmethod
    def _finalize_game(session, reason):
        session.is_active = False
        if not session.final_report:
            session.final_report = GameEngine._generate_final_report(session, reason)
        session.save()
        GameEngine._save_history(session, reason)

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
    def _generate_final_report(session, reason):
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

        prompt = GameEngine.REPORT_PROMPT_TEMPLATE.format(
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
                genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                if response and getattr(response, 'text', None):
                    return response.text.strip()
            except Exception:
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
        persona_data = GameEngine.generate_persona(session)
        if session.user:
            # Calculate stock profit (portfolio value - initial investment)
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

    # ================= STOCK MARKET TRADING =================
    @staticmethod
    def buy_stock(session, sector, amount):
        """
        Buy stocks in a specific sector.
        """
        GameEngine._refresh_level(session)
        if session.current_level < GameEngine.CONFIG['LEVEL_UNLOCKS']['investing']:
            return {'error': "Investing unlocks at Level 2."}
        if (
            session.current_level < GameEngine.CONFIG['LEVEL_UNLOCKS']['diversification']
            and session.portfolio
            and any(units > 0 for s, units in session.portfolio.items() if s != sector)
        ):
            return {'error': "Diversification unlocks at Level 3. Stick to one sector for now."}
        if sector not in GameEngine.CONFIG['STOCK_SECTORS']:
            return {'error': "Invalid sector."}
            
        if amount <= 0:
            return {'error': "Amount must be positive."}
            
        if session.wealth < amount:
            return {'error': "Insufficient funds."}
            
        # Get current price
        current_price = session.market_prices.get(sector, 100)
        
        # Calculate units (allow fractional? No, let's stick to units for simplicity or just value tracking)
        # Re-reading models: portfolio is {"gold": 0, "tech": 0} -> imply units.
        # But previous logic in views.py (invest_in_stocks) just tracked raw value in 'stock_investment'.
        # The new front-end expects units. 
        
        # Let's simple: Units = Amount / Price
        units = amount / current_price
        
        # Update State
        session.wealth -= amount
        session.portfolio[sector] = session.portfolio.get(sector, 0) + units
        
        # Log purchase history for profit calculation
        session.purchase_history.append({
            "sector": sector,
            "units": units,
            "price": current_price,
            "month": session.current_month
        })
        
        session.save()
        
        return {
            'session': session,
            'message': f"Bought {units:.2f} units of {sector.title()} at ₹{current_price}."
        }

    @staticmethod
    def sell_stock(session, sector, amount):
        """
        Sell stocks. `amount` here refers to UNITS to sell, not cash value.
        Wait, frontend input says "Units to Sell" if action is Sell.
        """
        if sector not in GameEngine.CONFIG['STOCK_SECTORS']:
            return {'error': "Invalid sector."}
            
        units_to_sell = float(amount) # Front end sends number
        
        if units_to_sell <= 0:
            return {'error': "Invalid units."}
            
        current_owned = session.portfolio.get(sector, 0)
        if current_owned < units_to_sell:
             return {'error': f"You only have {current_owned:.2f} units."}
             
        # Calculate Value
        current_price = session.market_prices.get(sector, 100)
        cash_value = units_to_sell * current_price
        
        # Update State
        session.wealth += int(cash_value) # Round to nearest rupee
        session.portfolio[sector] = current_owned - units_to_sell
        session.save()
        
        return {
            'session': session,
            'message': f"Sold {units_to_sell:.2f} units for ₹{int(cash_value)}."
        }

    @staticmethod
    def sell_futures(session, sector, units, duration):
        """
        Executes a Futures Contract sale.
        """
        GameEngine._refresh_level(session)
        if session.current_level < GameEngine.CONFIG['LEVEL_UNLOCKS']['mastery']:
            return {'error': "Mastery futures unlock at Level 4."}
        if sector not in session.market_prices:
            return {'error': "Invalid sector"}
            
        current_price = session.market_prices[sector]
        current_owned = session.portfolio.get(sector, 0)
        
        if current_owned < units:
            return {'error': f"Insufficient units. You have {current_owned}."}
            
        # 1. Get Quote
        contract_price = MarketPredictor.get_futures_quote(current_price, sector, duration)
        total_payout = contract_price * units
        
        # 2. Execute Trade (Immediate Cash, Remove Stock)
        session.wealth += int(total_payout)
        session.portfolio[sector] = current_owned - units
        
        # 3. Record Contract
        FuturesContract.objects.create(
            session=session,
            sector=sector,
            units=units,
            strike_price=contract_price,
            spot_price_at_sale=current_price,
            duration_months=duration,
            created_month=session.current_month
        )
        
        session.save()
        
        return {
            'message': f"Contract Sold! {units} {sector} units @ ₹{contract_price}/unit. +₹{int(total_payout)}",
            'session': session
        }

    @staticmethod
    def generate_persona(session):
        """Generates the detailed end-game report."""
        # Note: logic copied from original views.py _generate_detailed_report
        # but cleaned up slightly.
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

    @staticmethod
    def _calculate_level(session):
        level = 1
        for threshold in GameEngine.CONFIG['LEVEL_THRESHOLDS']:
            if (
                session.current_month >= threshold['min_month']
                or session.financial_literacy >= threshold['min_literacy']
            ):
                level = threshold['level']
        return level

    @staticmethod
    def _refresh_level(session):
        next_level = GameEngine._calculate_level(session)
        if session.current_level != next_level:
            session.current_level = next_level
