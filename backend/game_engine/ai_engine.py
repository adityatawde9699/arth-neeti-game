import os
import random
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from .models import ScenarioCard, Choice, PersonaProfile

# Configure logging
logger = logging.getLogger(__name__)

# Try to import groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None
    logger.warning("Groq library not found. AI features will be disabled.")

@dataclass
class GeneratedScenario:
    title: str
    description: str
    category: str
    choices: List[Dict]

class AIGameMaster:
    """
    Handles dynamic scenario generation using LLMs (Groq/Llama 3.1 8B Instant).
    
    Uses llama-3.1-8b-instant for fast, efficient scenario generation.
    This model provides:
    - Ultra-fast inference (thanks to Groq's LPU)
    - 14,400 free requests per day
    - High-quality reasoning for financial scenarios
    """
    
    # Prompt Templates
    SYSTEM_PROMPT = (
        "You are the Game Master for a financial literacy RPG called 'Arth-Neeti' set in modern India. "
        "Your goal is to create realistic, engaging financial scenarios that test the player's money management skills. "
        "Scenarios should be culturally relevant to India (e.g., festivals, family expectations, local market trends). "
        "Output strictly in JSON format."
    )
    
    SCENARIO_PROMPT_TEMPLATE = (
        "Generate a financial scenario for a player with the following profile:\n"
        "- Career Stage: {career_stage}\n"
        "- Risk Appetite: {risk_appetite}\n"
        "- Responsibility Level: {responsibility_level}\n"
        "- Current Wealth: ₹{wealth}\n"
        "- Current Month: {month}\n\n"
        "{career_context}\n\n"
        "The scenario should fall into the category: {category}.\n"
        "Create 2-3 choices. Each choice must have:\n"
        "1. Text: The action the player takes.\n"
        "2. Impacts: Wealth (amount), Happiness (-10 to 10), Credit Score (-20 to 20), Financial Literacy (0 to 10).\n"
        "3. Feedback: A brief educational note on why this was a good or bad choice.\n\n"
        "Output JSON format:\n"
        "{{\n"
        "  \"title\": \"Scenario Title\",\n"
        "  \"description\": \"Brief situation description (2-3 sentences).\",\n"
        "  \"category\": \"{category}\",\n"
        "  \"choices\": [\n"
        "    {{\n"
        "      \"text\": \"Choice description\",\n"
        "      \"wealth_impact\": -5000,\n"
        "      \"happiness_impact\": 5,\n"
        "      \"credit_impact\": 0,\n"
        "      \"literacy_impact\": 2,\n"
        "      \"feedback\": \"Explanation...\"\n"
        "    }}\n"
        "  ]\n"
        "}}"
    )

    # Career-specific context injected into the prompt
    CAREER_CONTEXTS = {
        'Student (Fully Funded)': (
            "The player is a fully-funded student with a fixed allowance. "
            "Focus scenarios on: canteen expenses, group parties, buying online courses, "
            "peer pressure to buy gadgets, college fest contributions, and splitting bills."
        ),
        'Student (Part Time)': (
            "The player is a student with a part-time job and inconsistent income. "
            "Focus scenarios on: balancing studies and work, freelance gig decisions, "
            "textbook vs pirated copies, cheap food vs health, and saving for a laptop."
        ),
        'Fresher': (
            "The player just got their first job. "
            "Focus scenarios on: first salary splurge temptation, room rental decisions, "
            "office lunch vs home food, starting an SIP, handling peer lifestyle inflation."
        ),
        'Professional': (
            "The player is an experienced professional earning a stable salary. "
            "Focus scenarios on: car vs public transport EMI, home loan decisions, "
            "vacation planning, stock market timing, insurance policies, and tax saving."
        ),
        'Business Owner': (
            "The player runs their own business. "
            "Focus scenarios on: inventory purchase decisions, GST compliance costs, "
            "hiring vs outsourcing, business expansion loans, tax raids, "
            "client payment delays, and reinvesting profits vs personal withdrawal."
        ),
        'Retired': (
            "The player is retired and living on savings/pension. "
            "Focus scenarios on: medical expenses, fixed deposit renewals, "
            "gifting money to grandchildren, rising utility bills, and avoiding scams."
        ),
    }

    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY')
        self.client = None
        
        if GROQ_AVAILABLE and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("✅ Groq AI initialized successfully (llama-3.1-8b-instant)")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Groq: {e}")
        else:
            if not GROQ_AVAILABLE:
                logger.warning("⚠️ Groq library not installed.")
            elif not self.api_key:
                logger.warning("⚠️ GROQ_API_KEY not set.")

    def generate_scenario(self, 
                          profile: PersonaProfile, 
                          wealth: int, 
                          month: int,
                          category: str = 'WANTS') -> Optional[ScenarioCard]:
        """
        Generates a new ScenarioCard using AI.
        Returns None if AI fails or is unavailable.
        """
        if not self.client:
            return None

        # Resolve career-specific context
        career_display = profile.get_career_stage_display()
        career_context = self.CAREER_CONTEXTS.get(
            career_display,
            "Focus on general personal finance decisions relevant to the Indian context."
        )

        # construct prompt
        prompt = self.SCENARIO_PROMPT_TEMPLATE.format(
            career_stage=career_display,
            risk_appetite=profile.get_risk_appetite_display(),
            responsibility_level=profile.get_responsibility_level_display(),
            wealth=wealth,
            month=month,
            category=category,
            career_context=career_context,
        )

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",  # Fast, efficient model with 14,400 free requests/day
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
                response_format={"type": "json_object"}
            )
            
            response_content = chat_completion.choices[0].message.content
            data = json.loads(response_content)
            
            # Create and Save objects (But maybe just return the object? No, we need to save to DB to use existing View logic)
            # Actually, `services.py` expects a model object.
            
            # Validation
            if not all(k in data for k in ('title', 'description', 'choices')):
                 logger.error("Invalid JSON from AI")
                 return None

            # Create Card
            card = ScenarioCard.objects.create(
                title=data['title'],
                description=data['description'],
                category=category, # strict adherence to requested category
                difficulty=3, # Default average difficulty? Or AI could determine?
                min_month=month,
                is_active=True,
                is_generated=True
            )
            
            # Create Choices
            for c_data in data['choices']:
                Choice.objects.create(
                    card=card,
                    text=c_data.get('text', 'Unknown Choice'),
                    wealth_impact=c_data.get('wealth_impact', 0),
                    happiness_impact=c_data.get('happiness_impact', 0),
                    credit_impact=c_data.get('credit_impact', 0),
                    literacy_impact=c_data.get('literacy_impact', 0),
                    feedback=c_data.get('feedback', ''),
                    is_recommended=False # AI doesn't strictly flag this yet, could improve prompt
                )
            
            logger.info(f"✅ Generated scenario: {data['title']}")
            return card

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error generating scenario: {e}")
            return None

# Singleton
_ai_master: Optional[AIGameMaster] = None

def get_ai_master() -> AIGameMaster:
    global _ai_master
    if _ai_master is None:
        _ai_master = AIGameMaster()
    return _ai_master