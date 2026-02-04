import random
import uuid
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import GameSession, PlayerChoice, RecurringExpense, GameHistory, PlayerProfile, ScenarioCard

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
        'STOCK_SECTORS': ['gold', 'tech', 'real_estate']
    }

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
        # Init market trends
        session.market_trends = {s: 0 for s in GameEngine.CONFIG['STOCK_SECTORS']}
        session.save()
        return session

    # ================= CORE GAMEPLAY =================
    @staticmethod
    def process_choice(session, card, choice):
        """Main game loop step."""
        
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
            report = GameEngine._advance_month(session, new_month - session.current_month)
            session.current_month = new_month
            feedback_parts.append(report)

        # 6. Check Game Over
        game_over, reason = GameEngine._check_game_over(session)
        if game_over:
            session.is_active = False
            GameEngine._finalize_game(session, reason)

        session.save()

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

        session.happiness = max(0, session.happiness - happiness_loss)
        session.credit_score = max(300, session.credit_score - credit_loss)
        
        # Log as skipped (choice=None)
        PlayerChoice.objects.create(session=session, card=card, choice=None)

        session.save()
        
        return {
            'message': f"Skipped! Penalty: -{happiness_loss} Happiness, -{credit_loss} Credit Score.",
            'session': session
        }

    # ================= ECONOMICS & MARKET =================
    @staticmethod
    def _advance_month(session, months_passed=1):
        """Advanced Month End Logic: Salary, Dynamic Expenses, Market Trends."""
        
        # 1. Salary
        salary_credit = GameEngine.CONFIG['MONTHLY_SALARY'] * months_passed
        session.wealth += salary_credit

        # 2. Dynamic Monthly Drain (Lifestyle Creep)
        # Calculate base drain from active recurring expenses
        active_expenses = session.expenses.filter(is_cancelled=False)
        base_drain = sum(e.amount for e in active_expenses)
        
        # Add "Cost of Living" based on inflation/lifestyle
        # Implied cost of food/rent that increases slightly every month
        cost_of_living = 15000 + (session.current_month * 200) 
        
        total_monthly_drain = base_drain + cost_of_living
        total_drain = total_monthly_drain * months_passed
        
        session.wealth -= total_drain
        session.recurring_expenses = total_monthly_drain # Update for UI display

        # 3. Market Update (Trend Based)
        GameEngine._update_market(session)

        return (
            f"\n📅 Month {session.current_month + months_passed} Started! "
            f"+₹{salary_credit} Salary. "
            f"-₹{total_drain} Expenses (Living + Subs). "
            f"Market updated."
        )

    @staticmethod
    def _update_market(session):
        """
        Simulate market movements with MOMENTUM and MEAN REVERSION.
        """
        if not session.market_prices:
            return

        for sector in GameEngine.CONFIG['STOCK_SECTORS']:
            if sector not in session.market_prices:
                continue
            
            # Get current state
            price = session.market_prices[sector]
            trend = session.market_trends.get(sector, 0)
            
            # 1. Momentum Logic: Existing trend pushes price
            # 2. Mean Reversion: Extreme trends tend to decay to 0
            
            # Random noise (-2% to +2%)
            noise = random.uniform(-0.02, 0.02)
            
            # Trend impact (Trend 5 = +5% push)
            trend_factor = trend * 0.01 
            
            # Calculate total change
            change_pct = noise + trend_factor
            
            # Apply to price
            new_price = int(price * (1 + change_pct))
            session.market_prices[sector] = new_price
            
            # Decay trend (Pull towards 0)
            if trend > 0:
                session.market_trends[sector] = max(0, trend - 1)
            elif trend < 0:
                session.market_trends[sector] = min(0, trend + 1)
                
            # Random chance to flip trend (Market Correction)
            if random.random() < 0.1: # 10% chance
                 session.market_trends[sector] = random.randint(-4, 4)

    # ================= LOAN LOGIC =================
    @staticmethod
    def process_loan(session, loan_type):
        """
        Smart Loan System.
        Limit based on credit score.
        """
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
        # ... (Same as before) ...
        # Copied for completeness or import from existing logic
        GameEngine._save_history(session, reason)

    @staticmethod
    def _save_history(session, reason):
        persona_data = GameEngine.generate_persona(session)
        if session.user:
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
            profile.highest_wealth = max(profile.highest_wealth, session.wealth)
            profile.highest_score = max(profile.highest_score, session.financial_literacy)
            profile.save()

    # ================= STOCK MARKET TRADING =================
    @staticmethod
    def buy_stock(session, sector, amount):
        """
        Buy stocks in a specific sector.
        """
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
