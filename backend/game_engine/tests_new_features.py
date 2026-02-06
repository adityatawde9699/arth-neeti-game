from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import GameSession, ScenarioCard, Choice, RecurringExpense, PlayerChoice
from .services import GameEngine

class AdvancedGameLoopTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.session = GameSession.objects.create(
            user=self.user,
            wealth=25000,
            happiness=100,
            current_month=1
        )
        self.session.market_prices = {'gold': 100, 'tech': 100, 'real_estate': 100}
        self.session.market_trends = {'gold': 5, 'tech': -5, 'real_estate': 0} # Strong trends
        self.session.save()

    def test_advance_month_deducts_expenses(self):
        """Test that advance_month correctly deducts living costs + recurring expenses."""
        # Add a recurring expense
        RecurringExpense.objects.create(
            session=self.session,
            name="Netflix",
            amount=500,
            started_month=1
        )
        
        # Advance month
        result = GameEngine.advance_month(self.session)
        
        # Reload session
        self.session.refresh_from_db()
        
        # Expected calculation:
        # Salary: +25000
        # Living Cost (Month 2): 15000 + (2 * 200) = 15400
        # Recurring: 500
        # Total Drain: 15900
        # Net Change: 25000 - 15900 = +9100
        # Initial Wealth: 25000
        # Expected Wealth: 34100
        
        self.assertEqual(self.session.current_month, 2)
        # Note: Logic in advance_month updates session.current_month BEFORE calculating cost of living
        # cost_of_living = 15000 + (session.current_month * 200) -> Month 2 * 200 = 400. 15400.
        
        self.assertEqual(self.session.wealth, 25000 + 25000 - (15400 + 500))
        self.assertIn("Expenses", result['report'])

    def test_market_updates_prices(self):
        """Test that market prices change based on trends."""
        initial_gold_price = self.session.market_prices['gold']
        initial_tech_price = self.session.market_prices['tech']
        
        GameEngine.update_market_prices(self.session)
        
        # Gold trend is +5 -> Should increase (approx +5% +/- 2%)
        # Tech trend is -5 -> Should decrease
        
        new_gold_price = self.session.market_prices['gold']
        new_tech_price = self.session.market_prices['tech']
        
        self.assertTrue(new_gold_price > initial_gold_price, f"Gold should rise (Trend 5). Old: {initial_gold_price}, New: {new_gold_price}")
        self.assertTrue(new_tech_price < initial_tech_price, f"Tech should fall (Trend -5). Old: {initial_tech_price}, New: {new_tech_price}")

    def test_purchase_history_tracking(self):
        """Test that buying stock adds to purchase_history."""
        GameEngine.buy_stock(self.session, 'tech', 1000) # Buy 1000 INR worth
        
        self.session.refresh_from_db()
        history = self.session.purchase_history
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['sector'], 'tech')
        self.assertEqual(history[0]['units'], 10.0) # 1000 / 100 = 10 units
        self.assertEqual(history[0]['month'], 1)

class ValidationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='player', password='password')
        self.session = GameSession.objects.create(user=self.user)
        self.card = ScenarioCard.objects.create(title="Card", difficulty=1)
        self.choice = Choice.objects.create(card=self.card, text="Choice")
        self.other_card = ScenarioCard.objects.create(title="Other", difficulty=1)
        self.other_choice = Choice.objects.create(card=self.other_card, text="Other Choice")

    def test_submit_valid_choice(self):
        payload = {
            'session_id': self.session.id,
            'card_id': self.card.id,
            'choice_id': self.choice.id
        }
        res = self.client.post('/api/submit-choice/', payload)
        self.assertEqual(res.status_code, 200)

    def test_submit_choice_mismatch(self):
        """Test submitting a choice that belongs to a different card."""
        payload = {
            'session_id': self.session.id,
            'card_id': self.card.id,
            'choice_id': self.other_choice.id # Belongs to other_card
        }
        res = self.client.post('/api/submit-choice/', payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Choice does not belong", str(res.data))
