""" AI Financial Advisor module for Arth-Neeti game.
Provides contextual financial advice using Groq API with intelligent fallback.

Features:
- Multi-language support (English, Hindi, Marathi)
- Retry logic with exponential backoff
- Structured advice categories
- Performance caching
- Comprehensive error handling
- Uses Groq's Llama 3.1 8B model (14,400 free requests/day) """

import os
import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
from dataclasses import dataclass
from enum import Enum
from core.ai.factory import get_ai_provider

logger = logging.getLogger(__name__)

GROQ_AVAILABLE = bool(os.getenv('GROQ_API_KEY'))

class Language(Enum):
    """Supported languages for advice."""
    ENGLISH = 'en'
    HINDI = 'hi'
    MARATHI = 'mr'


class AdviceCategory(Enum):
    """Categorization of financial scenarios."""
    SOCIAL = 'social'
    SHOPPING = 'shopping'
    INVESTMENT = 'investment'
    DEBT = 'debt'
    EMERGENCY = 'emergency'
    GADGETS = 'gadgets'
    INSURANCE = 'insurance'
    GENERAL = 'general'


class AdvisorPersona(Enum):
    """Distinct personalities for the AI advisor."""
    FRIENDLY = 'friendly'   # Default: Encouraging, polite
    STRICT = 'strict'       # Tough love, direct, risk-averse
    SASSY = 'sassy'         # Gen-Z humor, sarcastic, relatable
    HARSHAD = 'harshad'     # Risk Taker: "Risk hai toh ishq hai!"
    JETTA = 'jetta'         # Business Guru: "Profit margin matters!"
    VASOOLI = 'vasooli'     # Debt Collector: "Appun ka paisa kab dega?"
    SUNDAR = 'sundar'       # Scamster: "Double your money in 2 months!"



@dataclass
class AdviceResult:
    """Structured advice response."""
    advice: str
    source: str  # 'ai', 'curated', 'cached'
    success: bool
    language: str
    category: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0


@dataclass
class ChatbotMessage:
    """A message from one of the contextual chatbot characters."""
    character: str          # persona key: harshad, jetta, vasooli, sundar
    message: str
    choices: List[str]      # e.g. ['Ignore', 'Listen']
    is_scam: bool = False   # True only for Sundar's trap offers
    scam_loss_amount: int = 0


class AdviceCache:
    """Simple in-memory cache for advice to reduce API calls."""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl_seconds
    
    def _generate_key(self, title: str, wealth: int, happiness: int, language: str) -> str:
        """Generate cache key from scenario parameters."""
        # Bucket wealth and happiness to reduce cache misses
        wealth_bucket = (wealth // 10000) * 10000
        happiness_bucket = (happiness // 10) * 10
        return f"{title}:{wealth_bucket}:{happiness_bucket}:{language}"
    
    def get(self, title: str, wealth: int, happiness: int, language: str) -> Optional[str]:
        """Retrieve cached advice if valid."""
        key = self._generate_key(title, wealth, happiness, language)
        
        if key in self.cache:
            advice, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return advice
            else:
                # Expired
                del self.cache[key]
        
        return None
    
    def set(self, title: str, wealth: int, happiness: int, language: str, advice: str):
        """Store advice in cache."""
        key = self._generate_key(title, wealth, happiness, language)
        
        # Simple LRU: remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (advice, time.time())


class FinancialAdvisor:
    """AI-powered financial advisor with multi-language support and intelligent fallback."""

    # Category keywords mapping
    CATEGORY_KEYWORDS = {
        AdviceCategory.SOCIAL: ['friend', 'party', 'wedding', 'festival', 'celebration', 'birthday', 'relative'],
        AdviceCategory.SHOPPING: ['sale', 'discount', 'offer', 'deal', 'shopping', 'buy', 'purchase'],
        AdviceCategory.INVESTMENT: ['investment', 'mutual fund', 'stock', 'sip', 'fd', 'deposit', 'ppf', 'nps', 'elss'],
        AdviceCategory.DEBT: ['loan', 'emi', 'credit', 'borrow', 'debt', 'interest'],
        AdviceCategory.EMERGENCY: ['emergency', 'hospital', 'accident', 'repair', 'urgent', 'medical'],
        AdviceCategory.GADGETS: ['phone', 'gadget', 'laptop', 'electronics', 'upgrade', 'iphone', 'device'],
        AdviceCategory.INSURANCE: ['insurance', 'policy', 'term', 'health', 'cover', 'premium'],
    }

    def __init__(self, enable_cache: bool = True, max_retries: int = 3):
        """
        Initialize the Financial Advisor.
        
        Args:
            enable_cache: Whether to cache advice responses
            max_retries: Maximum retry attempts for API calls
        """
        self.max_retries = max_retries
        self.cache = AdviceCache() if enable_cache else None
        self.provider = get_ai_provider()
        
        if self.provider:
            logger.info(f"AI Provider initialized: {self.provider.__class__.__name__}")
        else:
            logger.info("No AI Provider available. Using fallback advice only.")

    def get_advice(
        self,
        scenario_title: str,
        scenario_description: str,
        choices: List[Dict],
        current_wealth: int,
        current_happiness: int,
        language: str = 'en',
        persona: AdvisorPersona = AdvisorPersona.FRIENDLY
    ) -> AdviceResult:
        """
        Get personalized financial advice for a given scenario.
        
        Args:
            scenario_title: Short title of the scenario
            scenario_description: Full description of the scenario
            current_wealth: Player's current wealth
            current_happiness: Player's current happiness level
            language: Language code ('en', 'hi', 'mr')
            persona: Advisor personality type
            
        Returns:
            AdviceResult containing advice and metadata
        """
        
        # Check cache first
        if self.cache:
            cached_advice = self.cache.get(scenario_title, current_wealth, current_happiness, language)
            if cached_advice:
                return AdviceResult(
                    advice=cached_advice,
                    source='cached',
                    success=True,
                    language=language,
                    confidence=0.9
                )
        
        # Determine category
        category = self._categorize_scenario(scenario_title, scenario_description)
        
        # Try AI generation first
        if self.client:
            for attempt in range(self.max_retries):
                try:
                    ai_advice = self._generate_ai_advice(
                        scenario_title=scenario_title,
                        scenario_description=scenario_description,
                        current_wealth=current_wealth,
                        current_happiness=current_happiness,
                        language=language,
                        category=category,
                        persona=persona
                    )
                    
                    if ai_advice:
                        # Cache successful advice
                        if self.cache:
                            self.cache.set(scenario_title, current_wealth, current_happiness, language, ai_advice)
                        
                        return AdviceResult(
                            advice=ai_advice,
                            source='ai',
                            success=True,
                            language=language,
                            category=category.value,
                            confidence=1.0
                        )
                
                except Exception as e:
                    logger.warning("AI advice generation failed (attempt %d/%d): %s", attempt + 1, self.max_retries, e)
                    if attempt < self.max_retries - 1:
                        # Exponential backoff
                        time.sleep(2 ** attempt)
                    continue
        
        # Fallback to curated advice
        fallback_advice = self._get_fallback_advice(category, language)
        return AdviceResult(
            advice=fallback_advice,
            source='curated',
            success=True,
            language=language,
            category=category.value,
            confidence=0.7
        )

    def _categorize_scenario(self, title: str, description: str) -> AdviceCategory:
        """Categorize scenario based on keywords."""
        combined_text = f"{title} {description}".lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return AdviceCategory.GENERAL

    def _generate_ai_advice(
        self,
        scenario_title: str,
        scenario_description: str,
        current_wealth: int,
        current_happiness: int,
        language: str,
        category: AdviceCategory,
        persona: AdvisorPersona
    ) -> Optional[str]:
        """Generate advice using the AI Provider."""
        
        if not self.provider:
            return None
        
        # Language names for prompt
        language_names = {
            'en': 'English',
            'hi': 'Hindi',
            'mr': 'Marathi'
        }
        
        # Persona descriptions
        persona_prompts = {
            AdvisorPersona.FRIENDLY: "You are a friendly, encouraging financial advisor. Be warm, supportive, and use emojis. Provide clear, actionable advice.",
            AdvisorPersona.STRICT: "You are a strict, no-nonsense financial advisor. Be direct, emphasize risks, and push for conservative choices. Use tough love.",
            AdvisorPersona.SASSY: "You are a Gen-Z financial advisor with a sassy, humorous tone. Use relatable language, memes references, and light sarcasm while still being helpful."
        }
        
        # Construct prompt
        prompt = f"""{persona_prompts[persona]}

The player is facing this financial scenario:

**Scenario**: {scenario_title}
**Details**: {scenario_description}
**Current Wealth**: ₹{current_wealth:,}
**Current Happiness**: {current_happiness}/100
**Category**: {category.value}

Provide practical financial advice in {language_names.get(language, 'English')} for this scenario. Consider:
1. The player's current financial situation
2. Short-term and long-term impacts
3. Emotional/happiness factors
4. Indian financial context (if relevant)

Keep your response:
- Concise (2-3 sentences max)
- Actionable and specific
- Culturally appropriate
- In the specified language ({language_names.get(language, 'English')})

Start with an emoji that fits the advice tone."""

        try:
            return self.provider.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=200,
                top_p=0.9
            )
        except Exception as e:
            logger.error(f"AI Provider error: {e}")
            return None

    def _get_fallback_advice(self, category: AdviceCategory, language: str) -> str:
        """
        Get curated fallback advice when AI is unavailable.
        
        Args:
            category: Advice category
            language: Language code
            
        Returns:
            Random advice from curated pool
        """
        advice_pool = self._get_advice_pool(category, language)
        return random.choice(advice_pool)

    @staticmethod
    def _get_advice_pool(category: AdviceCategory, language: str) -> List[str]:
        """Get curated advice pool for category and language."""
        
        # English advice pools
        advice_pools_en = {
            AdviceCategory.SOCIAL: [
                "💡 Social events are important, but set a budget before attending. It's okay to say 'I'll catch the next one' if your finances are tight!",
                "💡 Before spending on social events, ask yourself: 'Is this a need or a want?' Your future self will thank you for wise choices.",
                "💡 Consider the 50-30-20 rule: 50% for needs, 30% for wants (like social events), 20% for savings. Where does this fit?",
                "💡 True friends understand budget constraints. Suggest budget-friendly alternatives like potluck instead of expensive restaurants."
            ],
            AdviceCategory.SHOPPING: [
                "💡 A discount on something you don't need isn't a savings - it's still spending! Ask: 'Would I buy this at full price?'",
                "💡 Impulse buying often leads to regret. Try the 24-hour rule: wait a day before making non-essential purchases.",
                "💡 Just because something is on sale doesn't mean you can afford it. Check your budget first!",
                "💡 Calculate cost-per-use: A ₹5,000 jacket worn 100 times costs ₹50/use. Worth it?"
            ],
            AdviceCategory.INVESTMENT: [
                "💡 Start investing early, even small amounts! SIPs of ₹500/month can grow significantly over time thanks to compounding.",
                "💡 Don't put all eggs in one basket. Diversify between safe options (FD, PPF) and growth options (mutual funds, stocks).",
                "💡 Before investing, build an emergency fund first - 3-6 months of expenses. Then invest consistently.",
                "💡 Time in market > Timing the market. Start your SIP today, not when markets are 'low'."
            ],
            AdviceCategory.DEBT: [
                "💡 Avoid high-interest loans like credit cards (36-48% p.a.) and instant loan apps. They create a debt trap!",
                "💡 The EMI rule: Total EMIs shouldn't exceed 40% of your monthly income. Beyond this, you risk financial stress.",
                "💡 Good debt (education, home) vs bad debt (gadgets, vacations). Know the difference before borrowing.",
                "💡 Pay credit card bills IN FULL every month. Minimum payment = maximum interest (36-42% APR)!"
            ],
            AdviceCategory.EMERGENCY: [
                "💡 This is exactly why an emergency fund matters! Always keep 3-6 months of expenses saved for unexpected situations.",
                "💡 For true emergencies, prioritize health and safety. Money can be earned back, but time and health cannot.",
                "💡 Consider getting health insurance if you don't have one. ₹500-1000/month can save you lakhs later!",
                "💡 Keep emergency funds in liquid instruments (savings account, liquid mutual funds) - not locked FDs."
            ],
            AdviceCategory.GADGETS: [
                "💡 Gadgets depreciate fast! Ask yourself: Is this an upgrade I need, or just want? Last year's model often works just as well.",
                "💡 Before buying electronics on EMI, calculate the total cost with interest. That ₹50k phone might cost ₹60k!",
                "💡 The best phone is the one you can afford without stress. Function over fashion saves money.",
                "💡 One-year-old flagship > Latest mid-range phone. Better specs, lower price, proven reliability."
            ],
            AdviceCategory.INSURANCE: [
                "💡 Insurance is for protection, not investment! Buy Term Insurance for life cover (cheap and high coverage).",
                "💡 Health insurance is a must - medical inflation in India is 15% per year. Get covered before you need it.",
                "💡 Review insurance policies before buying. Traditional LIC policies often give poor returns compared to mutual funds.",
                "💡 Buy term, invest the rest. ₹50k in endowment gives ₹10L. Same in term (₹7k) + SIP (₹43k) gives ₹40L!"
            ],
            AdviceCategory.GENERAL: [
                "💡 Financial literacy tip: Track every rupee you spend for a month. You'll be surprised where your money goes!",
                "💡 Remember the 50-30-20 rule: 50% needs, 30% wants, 20% savings. Small discipline leads to big wealth!",
                "💡 Pay yourself first! Set up auto-transfers to savings as soon as salary arrives, before spending on anything else.",
                "💡 Your financial decisions today shape your tomorrow. Think long-term, but don't forget to enjoy life responsibly!",
                "💡 Before any purchase, ask: Is this a need, a want, or a 'nice to have'? Prioritize accordingly."
            ]
        }
        
        # Hindi advice pools
        advice_pools_hi = {
            AdviceCategory.SOCIAL: [
                "💡 सामाजिक कार्यक्रम महत्वपूर्ण हैं, लेकिन भाग लेने से पहले बजट तय करें। अगर वित्त तंग है तो 'अगली बार' कहना ठीक है!",
                "💡 सामाजिक खर्च से पहले खुद से पूछें: 'यह जरूरत है या चाह?' आपका भविष्य का खुद आपको धन्यवाद देगा।",
                "💡 50-30-20 नियम याद रखें: 50% जरूरतें, 30% इच्छाएं (जैसे सामाजिक कार्यक्रम), 20% बचत। यह कहां फिट होता है?",
                "💡 सच्चे दोस्त बजट की समस्याओं को समझते हैं। महंगे रेस्तरां की जगह पॉटलक जैसे किफायती विकल्प सुझाएं।"
            ],
            AdviceCategory.SHOPPING: [
                "💡 जिस चीज की जरूरत नहीं उस पर छूट भी बचत नहीं - यह खर्च है! पूछें: 'क्या मैं इसे पूरी कीमत पर खरीदता?'",
                "💡 आवेगपूर्ण खरीदारी अक्सर पछतावा देती है। 24 घंटे का नियम आजमाएं: गैर-जरूरी चीजों के लिए एक दिन रुकें।",
                "💡 सिर्फ इसलिए कि कुछ सेल पर है इसका मतलब नहीं कि आप इसे खरीद सकते हैं। पहले बजट चेक करें!",
                "💡 प्रति-उपयोग लागत गिनें: ₹5,000 की जैकेट 100 बार पहनी तो ₹50/उपयोग। सही है?"
            ],
            AdviceCategory.INVESTMENT: [
                "💡 जल्दी निवेश शुरू करें, छोटी रकम भी! ₹500/महीने का SIP चक्रवृद्धि से काफी बढ़ता है।",
                "💡 सभी अंडे एक टोकरी में न रखें। सुरक्षित (FD, PPF) और विकास विकल्पों (म्यूचुअल फंड, स्टॉक) में विविधता लाएं।",
                "💡 निवेश से पहले आपातकालीन फंड बनाएं - 3-6 महीने का खर्च। फिर लगातार निवेश करें।",
                "💡 बाजार में समय > बाजार का समय। आज SIP शुरू करें, बाजार 'नीचा' होने का इंतजार न करें।"
            ],
            AdviceCategory.DEBT: [
                "💡 उच्च ब्याज वाले कर्ज से बचें जैसे क्रेडिट कार्ड (36-48% प्रति वर्ष) और त्वरित ऋण ऐप। ये कर्ज का जाल बनाते हैं!",
                "💡 EMI नियम: कुल EMI आपकी मासिक आय के 40% से अधिक नहीं होनी चाहिए। इससे ज्यादा = वित्तीय तनाव।",
                "💡 अच्छा कर्ज (शिक्षा, घर) vs बुरा कर्ज (गैजेट, छुट्टियां)। उधार लेने से पहले फर्क जानें।",
                "💡 क्रेडिट कार्ड बिल हर महीने पूरा भरें। न्यूनतम भुगतान = अधिकतम ब्याज (36-42% APR)!"
            ],
            AdviceCategory.EMERGENCY: [
                "💡 यही कारण है कि आपातकालीन फंड मायने रखता है! अप्रत्याशित स्थितियों के लिए हमेशा 3-6 महीने का खर्च बचाएं।",
                "💡 सच्ची आपात स्थितियों में स्वास्थ्य और सुरक्षा को प्राथमिकता दें। पैसा वापस कमाया जा सकता है, लेकिन समय और स्वास्थ्य नहीं।",
                "💡 अगर आपके पास स्वास्थ्य बीमा नहीं है तो लें। ₹500-1000/महीना लाखों बचा सकता है!",
                "💡 आपातकालीन फंड को तरल साधनों में रखें (बचत खाता, लिक्विड म्यूचुअल फंड) - लॉक FD में नहीं।"
            ],
            AdviceCategory.GADGETS: [
                "💡 गैजेट तेजी से सस्ते होते हैं! खुद से पूछें: यह अपग्रेड जरूरत है या चाह? पिछले साल का मॉडल अक्सर उतना ही अच्छा होता है।",
                "💡 EMI पर इलेक्ट्रॉनिक्स खरीदने से पहले ब्याज सहित कुल लागत गिनें। वह ₹50k फोन ₹60k हो सकता है!",
                "💡 सबसे अच्छा फोन वह है जिसे आप बिना तनाव के खरीद सकें। कार्यक्षमता > फैशन पैसे बचाता है।",
                "💡 एक साल पुराना फ्लैगशिप > नवीनतम मिड-रेंज फोन। बेहतर स्पेक्स, कम कीमत, सिद्ध विश्वसनीयता।"
            ],
            AdviceCategory.INSURANCE: [
                "💡 बीमा सुरक्षा के लिए है, निवेश नहीं! जीवन कवर के लिए टर्म इंश्योरेंस खरीदें (सस्ता और उच्च कवरेज)।",
                "💡स्वास्थ्य बीमा जरूरी है - भारत में चिकित्सा मुद्रास्फीति 15% प्रति वर्ष है। जरूरत से पहले कवर लें।",
                "💡खरीदने से पहले बीमा पॉलिसियों की समीक्षा करें। पारंपरिक LIC पॉलिसियां अक्सर म्यूचुअल फंड की तुलना में कम रिटर्न देती हैं।",
                "💡 टर्म खरीदें, बाकी निवेश करें। एंडोमेंट में ₹50k देता है ₹10L। टर्म (₹7k) + SIP (₹43k) में वही देता है ₹40L!"
            ],
            AdviceCategory.GENERAL: [
                "💡 वित्तीय साक्षरता टिप: एक महीने तक हर रुपये का हिसाब रखें। आप चौंक जाएंगे कि पैसा कहां जाता है!",
                "💡50-30-20 नियम याद रखें: 50% जरूरतें, 30% इच्छाएं, 20% बचत। छोटा अनुशासन बड़ी संपत्ति बनाता है!",
                "💡पहले खुद को भुगतान करें! वेतन आते ही कुछ भी खर्च करने से पहले बचत में ऑटो-ट्रांसफर सेट करें।",
                "💡आज के वित्तीय निर्णय आपके कल को आकार देते हैं। दीर्घकालिक सोचें, लेकिन जिम्मेदारी से जीवन का आनंद लेना न भूलें!",
                "💡किसी भी खरीदारी से पहले पूछें: यह जरूरत है, चाह है, या 'अच्छा होगा'? तदनुसार प्राथमिकता दें।"
            ]
        }
        
        # Marathi advice pools (sample - you'd need full translation)
        advice_pools_mr = {
            AdviceCategory.GENERAL: [
                "💡 आर्थिक साक्षरता टीप: एक महिन्यासाठी प्रत्येक रुपयाचा हिशोब ठेवा. तुम्हाला आश्चर्य वाटेल की पैसे कुठे जातात!",
                "💡 50-30-20 नियम लक्षात ठेवा: 50% गरजा, 30% इच्छा, 20% बचत. लहान शिस्त मोठी संपत्ती बनवते!"
            ]
        }
        
        # Select appropriate pool
        if language == 'hi':
            pools = advice_pools_hi
        elif language == 'mr':
            pools = advice_pools_mr
        else:
            pools = advice_pools_en
        
        # Return pool for category, fallback to GENERAL
        return pools.get(category, pools[AdviceCategory.GENERAL])

    # --- Character system prompts for contextual chatbots ---
    CHARACTER_SYSTEM_PROMPTS: Dict[str, str] = {
        'harshad': (
            "You are Harshad, a flamboyant risk-loving stock market bull from Mumbai. "
            "You speak in a mix of Hindi and English (Hinglish). Your catchphrase is 'Risk hai toh ishq hai!' "
            "You push the player to invest aggressively in stocks, options, and crypto. "
            "You are charismatic but reckless. Keep it to 2 sentences max."
        ),
        'jetta': (
            "You are Jetta Bhai, a shrewd South-Indian business mentor. "
            "You speak with a South-Indian accent in English with occasional Tamil/Telugu words. "
            "Your catchphrase is 'Ayyo! Profit margin matters!' "
            "You focus on cutting expenses and maximizing ROI. Keep it to 2 sentences max."
        ),
        'vasooli': (
            "You are Vasooli Bhai, a menacing but comedic debt collector from a Bollywood movie. "
            "You speak in Mumbai tapori style. Your catchphrase is 'Appun ka paisa kab dega?' "
            "You threaten the player (humorously) about unpaid debts and dropping happiness. "
            "Keep it to 2 sentences max."
        ),
        'sundar': (
            "You are Sundar, a smooth-talking online scamster. "
            "You speak in overly polished, too-good-to-be-true language. "
            "You offer schemes like 'Double your money in 2 months!' or 'Guaranteed 50% returns!' "
            "Make the offer sound tempting but subtly suspicious. Keep it to 2 sentences max."
        ),
    }

    # --- Curated fallback dialogues for when AI is unavailable ---
    CHARACTER_FALLBACKS: Dict[str, List[str]] = {
        'harshad': [
            "Risk hai toh ishq hai! Why is your money sleeping in the bank? Buy Calls!",
            "Arre yaar, the market is on fire! Put everything in tech stocks, trust me!",
            "Bhai, F&O mein paisa hi paisa hai. Just close your eyes and buy!",
            "Savings account? That's for losers! Real men buy options!",
        ],
        'jetta': [
            "Ayyo! Profit margin matters. Cut the expenses on lifestyle!",
            "Saar, why are you spending on wants when your needs are not covered? Very bad!",
            "Listen da, first save 50% of income, then only think about spending!",
            "Your expense ratio is worse than a bad mutual fund. Fix it!",
        ],
        'vasooli': [
            "Appun ka paisa kab dega? Pay now or lose Happiness!",
            "Aye! EMI miss kiya? Appun ko bahut gussa aata hai!",
            "Tere paas itna karz hai, aur tu shopping kar raha hai? Pagal hai kya!",
            "Chal chal, pehle loan chuka, phir masti kar!",
        ],
        'sundar': [
            "Sir/Madam, I have an exclusive opportunity! Double your money in just 2 months! 100% guaranteed!",
            "Congratulations! You've been selected for our VIP investment scheme. Just invest ₹10,000 and get ₹50,000 back!",
            "Hello dear, my uncle works at SEBI. I have insider info on a stock that will go 10x. Just send me ₹5,000 to join!",
            "Limited time offer! Our AI-powered crypto bot guarantees 50% monthly returns. No risk at all!",
        ],
    }

    def get_proactive_message(
        self,
        trigger_type: str,
        trigger_reason: str,
        current_wealth: int,
        current_happiness: int,
        persona: AdvisorPersona = AdvisorPersona.FRIENDLY
    ) -> str:
        """
        Generate proactive advice based on game state triggers.
        """
        prompt = f"""You are a {persona.value} financial advisor.
The player has triggered a {trigger_type} alert: {trigger_reason}.
Current Wealth: ₹{current_wealth}
Current Happiness: {current_happiness}

Give a short, punchy, 1-sentence reaction/advice."""

        if self.provider:
            try:
                msg = self.provider.generate_text(
                    prompt=prompt,
                    temperature=0.8,
                    max_tokens=60
                )
                return msg if msg else f"Warning: {trigger_reason}. Watch your finances!"
            except Exception:
                pass
        
        # Fallback
        return f"Warning: {trigger_reason}. Watch your finances!"

    def get_character_message(
        self,
        character: str,
        trigger_reason: str,
        current_wealth: int,
        current_happiness: int,
    ) -> ChatbotMessage:
        """
        Generate a contextual message from one of the game's chatbot characters.

        Args:
            character: One of 'harshad', 'jetta', 'vasooli', 'sundar'.
            trigger_reason: Why this character was triggered.
            current_wealth: Player's current wealth.
            current_happiness: Player's current happiness.

        Returns:
            ChatbotMessage with character dialogue and interaction choices.
        """
        system_prompt = self.CHARACTER_SYSTEM_PROMPTS.get(character, '')
        is_scam = character == 'sundar'
        scam_loss = 0

        if is_scam:
            # Calculate scam loss: 20-50% of current wealth
            scam_loss = int(current_wealth * random.uniform(0.2, 0.5))

        # Build user prompt
        user_prompt = (
            f"The player currently has ₹{current_wealth:,} and happiness {current_happiness}/100. "
            f"Context: {trigger_reason}. "
            f"Generate your character's dialogue."
        )

        message = None
        if self.provider and system_prompt:
            try:
                message = self.provider.generate_text(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    temperature=0.9,
                    max_tokens=100
                )
            except Exception as e:
                logger.warning(f"Character AI failed for {character}: {e}")

        # Fallback to curated dialogue
        if not message:
            fallbacks = self.CHARACTER_FALLBACKS.get(character, ["Watch your finances!"])
            message = random.choice(fallbacks)

        # Determine choices based on character
        if is_scam:
            choices = [f'Invest ₹{scam_loss:,}', 'Ignore (Smart Move)']
        elif character == 'vasooli':
            choices = ['Pay EMI Now', 'Ignore (Risk Happiness)']
        else:
            choices = ['Listen', 'Ignore']

        return ChatbotMessage(
            character=character,
            message=message,
            choices=choices,
            is_scam=is_scam,
            scam_loss_amount=scam_loss,
        )


# Singleton instance
_advisor: Optional[FinancialAdvisor] = None


def get_advisor() -> FinancialAdvisor:
    """Get or create the singleton advisor instance."""
    global _advisor
    if _advisor is None:
        _advisor = FinancialAdvisor(enable_cache=True, max_retries=3)
    return _advisor


def reset_advisor():
    """Reset the singleton (useful for testing)."""
    global _advisor
    _advisor = None