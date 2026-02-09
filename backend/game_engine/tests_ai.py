from unittest.mock import patch, MagicMock
from django.test import TestCase
from .models import ScenarioCard, PersonaProfile, GameSession
from django.contrib.auth.models import User
from .ai_engine import AIGameMaster, get_ai_master

class AIGameMasterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ai_test_user')
        self.session = GameSession.objects.create(user=self.user)
        self.profile = PersonaProfile.objects.create(
            session=self.session,
            career_stage=PersonaProfile.CareerStage.FRESHER,
            risk_appetite=PersonaProfile.RiskAppetite.MEDIUM
        )

    @patch('game_engine.ai_engine.Groq')
    @patch('game_engine.ai_engine.GROQ_AVAILABLE', True)
    @patch.dict('os.environ', {'GROQ_API_KEY': 'fake-key'})
    def test_initialization_success(self, mock_groq):
        """Test that AIGameMaster initializes with valid key."""
        master = AIGameMaster()
        self.assertIsNotNone(master.client)

    @patch.dict('os.environ', {}, clear=True)
    def test_initialization_no_key(self, ):
        """Test that AIGameMaster handles missing key gracefully."""
        master = AIGameMaster()
        self.assertIsNone(master.client)

    @patch('game_engine.ai_engine.Groq')
    @patch('game_engine.ai_engine.GROQ_AVAILABLE', True)
    @patch.dict('os.environ', {'GROQ_API_KEY': 'fake-key'})
    def test_generate_scenario_success(self, mock_groq):
        """Test successful scenario generation."""
        # Mock Groq response
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "title": "AI Generated Test",
            "description": "This is a test scenario.",
            "category": "WANTS",
            "choices": [
                {
                    "text": "Buy it",
                    "wealth_impact": -100,
                    "happiness_impact": 5,
                    "credit_impact": 0,
                    "literacy_impact": 0,
                    "feedback": "Okay."
                }
            ]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response

        master = AIGameMaster()
        card = master.generate_scenario(self.profile, 10000, 1)

        self.assertIsNotNone(card)
        self.assertEqual(card.title, "AI Generated Test")
        self.assertTrue(card.is_generated)
        self.assertEqual(card.choices.count(), 1)
        self.assertEqual(card.choices.first().text, "Buy it")

    @patch('game_engine.ai_engine.Groq')
    @patch('game_engine.ai_engine.GROQ_AVAILABLE', True)
    @patch.dict('os.environ', {'GROQ_API_KEY': 'fake-key'})
    def test_generate_scenario_failure(self, mock_groq):
        """Test failure handling (invalid JSON)."""
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Invalid JSON"
        mock_client.chat.completions.create.return_value = mock_response

        master = AIGameMaster()
        card = master.generate_scenario(self.profile, 10000, 1)

        self.assertIsNone(card)
