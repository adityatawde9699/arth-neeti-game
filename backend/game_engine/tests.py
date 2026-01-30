"""
Unit tests for Arth-Neeti game engine.
Run with: python manage.py test game_engine
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import GameSession, ScenarioCard, Choice, PlayerChoice


class GameSessionModelTests(TestCase):
    """Tests for the GameSession model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_session_creation_with_defaults(self):
        """Test that a new session is created with correct default values."""
        session = GameSession.objects.create(user=self.user)
        
        self.assertEqual(session.wealth, 25000)
        self.assertEqual(session.happiness, 100)
        self.assertEqual(session.credit_score, 700)
        self.assertEqual(session.financial_literacy, 0)
        self.assertEqual(session.current_month, 1)
        self.assertTrue(session.is_active)
    
    def test_session_str_representation(self):
        """Test the string representation of a session."""
        session = GameSession.objects.create(user=self.user)
        expected = f"Session {session.id} - User: testuser - Month: 1"
        self.assertEqual(str(session), expected)


class ScenarioCardModelTests(TestCase):
    """Tests for ScenarioCard and Choice models."""
    
    def test_card_creation(self):
        """Test scenario card creation."""
        card = ScenarioCard.objects.create(
            title="Test Scenario",
            description="Test description",
            category="WANTS",
            difficulty=2,
            min_month=1
        )
        self.assertTrue(card.is_active)
        self.assertEqual(card.category, "WANTS")
    
    def test_choice_creation_with_impacts(self):
        """Test choice creation with impact values."""
        card = ScenarioCard.objects.create(
            title="Test Card",
            description="Test",
            category="NEEDS"
        )
        choice = Choice.objects.create(
            card=card,
            text="Test choice",
            wealth_impact=-1000,
            happiness_impact=10,
            credit_impact=-5,
            literacy_impact=15,
            feedback="Test feedback",
            is_recommended=True
        )
        self.assertEqual(choice.wealth_impact, -1000)
        self.assertTrue(choice.is_recommended)


class StartGameAPITests(APITestCase):
    """Tests for the start_game API endpoint."""
    
    def test_start_game_creates_unique_sessions(self):
        """Test that each start_game call creates a unique session."""
        response1 = self.client.post('/api/start-game/')
        response2 = self.client.post('/api/start-game/')
        
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        session1_id = response1.data['session']['id']
        session2_id = response2.data['session']['id']
        
        # Sessions should be different
        self.assertNotEqual(session1_id, session2_id)
    
    def test_start_game_creates_guest_user(self):
        """Test that start_game creates a unique guest user."""
        response = self.client.post('/api/start-game/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        session = GameSession.objects.get(id=response.data['session']['id'])
        self.assertTrue(session.user.username.startswith('Guest_'))
    
    def test_start_game_initial_values(self):
        """Test that new game has correct initial values."""
        response = self.client.post('/api/start-game/')
        
        session_data = response.data['session']
        self.assertEqual(session_data['wealth'], 25000)
        self.assertEqual(session_data['happiness'], 100)
        self.assertEqual(session_data['credit_score'], 700)
        self.assertEqual(session_data['current_month'], 1)


class SubmitChoiceAPITests(APITestCase):
    """Tests for the submit_choice API endpoint."""
    
    def setUp(self):
        # Create a test user and session
        self.user = User.objects.create_user(
            username='testplayer',
            password='testpass'
        )
        self.session = GameSession.objects.create(
            user=self.user,
            wealth=25000,
            happiness=100,
            credit_score=700
        )
        # Create a test card with choices
        self.card = ScenarioCard.objects.create(
            title="Test Card",
            description="Test scenario",
            category="WANTS",
            min_month=1
        )
        self.good_choice = Choice.objects.create(
            card=self.card,
            text="Good choice",
            wealth_impact=1000,
            happiness_impact=10,
            credit_impact=5,
            literacy_impact=10,
            feedback="Good job!",
            is_recommended=True
        )
        self.bad_choice = Choice.objects.create(
            card=self.card,
            text="Bad choice",
            wealth_impact=-5000,
            happiness_impact=-20,
            credit_impact=-10,
            literacy_impact=-10,
            feedback="Could do better",
            is_recommended=False
        )
    
    def test_submit_choice_updates_stats(self):
        """Test that submitting a choice updates session stats correctly."""
        response = self.client.post('/api/submit-choice/', {
            'session_id': self.session.id,
            'card_id': self.card.id,
            'choice_id': self.good_choice.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check updated values
        updated_session = response.data['session']
        self.assertEqual(updated_session['wealth'], 26000)  # 25000 + 1000
        self.assertEqual(updated_session['credit_score'], 705)  # 700 + 5
    
    def test_submit_choice_logs_player_choice(self):
        """Test that player choice is logged."""
        self.client.post('/api/submit-choice/', {
            'session_id': self.session.id,
            'card_id': self.card.id,
            'choice_id': self.good_choice.id
        })
        
        player_choices = PlayerChoice.objects.filter(session=self.session)
        self.assertEqual(player_choices.count(), 1)
    
    def test_happiness_clamped_to_bounds(self):
        """Test that happiness is clamped between 0 and 100."""
        # Set happiness to edge case
        self.session.happiness = 95
        self.session.save()
        
        # Make a choice that would push happiness over 100
        self.good_choice.happiness_impact = 20
        self.good_choice.save()
        
        response = self.client.post('/api/submit-choice/', {
            'session_id': self.session.id,
            'card_id': self.card.id,
            'choice_id': self.good_choice.id
        })
        
        # Happiness should be clamped at 100
        self.assertLessEqual(response.data['session']['happiness'], 100)
    
    def test_bankruptcy_ends_game(self):
        """Test that wealth <= 0 triggers game over."""
        self.session.wealth = 3000
        self.session.save()
        
        # Make bad choice that depletes wealth
        response = self.client.post('/api/submit-choice/', {
            'session_id': self.session.id,
            'card_id': self.card.id,
            'choice_id': self.bad_choice.id  # -5000 impact
        })
        
        self.assertTrue(response.data['game_over'])
        self.assertEqual(response.data['game_over_reason'], 'BANKRUPTCY')


class GameProgressionTests(APITestCase):
    """Tests for game progression and month advancement."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='progresstest',
            password='testpass'
        )
        self.session = GameSession.objects.create(
            user=self.user,
            wealth=100000,
            happiness=100,
            credit_score=700
        )
        # Create multiple cards
        for i in range(5):
            card = ScenarioCard.objects.create(
                title=f"Card {i}",
                description=f"Description {i}",
                category="WANTS",
                min_month=1
            )
            Choice.objects.create(
                card=card,
                text="Choice",
                wealth_impact=-100,
                happiness_impact=0,
                credit_impact=0,
                literacy_impact=0,
                feedback="Feedback",
                is_recommended=True
            )
    
    def test_month_advances_every_3_choices(self):
        """Test that month advances after every 3 choices (new logic)."""
        cards = ScenarioCard.objects.all()[:4]
        
        # Make 3 choices - should advance to month 2
        for i, card in enumerate(cards[:3]):
            choice = card.choices.first()
            self.client.post('/api/submit-choice/', {
                'session_id': self.session.id,
                'card_id': card.id,
                'choice_id': choice.id
            })
        
        session = GameSession.objects.get(id=self.session.id)
        self.assertEqual(session.current_month, 2)  # (3 // 3) + 1 = 2
    
    def test_game_completes_at_month_12(self):
        """Test that game ends after 12 months (new 1-year game logic)."""
        # Create enough cards for the test
        for i in range(40):
            card = ScenarioCard.objects.create(
                title=f"Extra Card {i}",
                description=f"Description {i}",
                category="INVESTMENT",
                min_month=1
            )
            Choice.objects.create(
                card=card,
                text="Choice",
                wealth_impact=0,
                happiness_impact=0,
                credit_impact=0,
                literacy_impact=0,
                feedback="Feedback",
                is_recommended=True
            )
        
        # Make 36 choices (12 months × 3 cards/month)
        cards = ScenarioCard.objects.all()[:36]
        game_over = False
        
        for card in cards:
            choice = card.choices.first()
            response = self.client.post('/api/submit-choice/', {
                'session_id': self.session.id,
                'card_id': card.id,
                'choice_id': choice.id
            })
            if response.data.get('game_over'):
                game_over = True
                game_over_reason = response.data.get('game_over_reason')
                break
        
        self.assertTrue(game_over)
        self.assertEqual(game_over_reason, 'COMPLETED')
