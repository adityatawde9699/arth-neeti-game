"""
AI Financial Advisor module for Arth-Neeti game.
Provides contextual financial advice using Gemini API with intelligent fallback.

Features:
- Multi-language support (English, Hindi, Marathi)
- Retry logic with exponential backoff
- Structured advice categories
- Performance caching
- Comprehensive error handling
"""

import os
import random
import time
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
from dataclasses import dataclass
from enum import Enum

# Try to import Google's Generative AI library
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


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


@dataclass
class AdviceResult:
    """Structured advice response."""
    advice: str
    source: str  # 'ai', 'curated', 'cached'
    success: bool
    language: str
    category: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0


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
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.model = None
        self.max_retries = max_retries
        self.cache = AdviceCache() if enable_cache else None

        if GENAI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
                self.model = None
        else:
            if not GENAI_AVAILABLE:
                print("⚠️  google-generativeai library not installed. Using fallback advice only.")
            elif not self.api_key:
                print("⚠️  GEMINI_API_KEY not set. Using fallback advice only.")

    def get_advice(
        self,
        scenario_title: str,
        scenario_description: str,
        choices: List[Dict],
        player_wealth: int,
        player_happiness: int,
        language: str = 'en'
    ) -> AdviceResult:
        """
        Get financial advice for a scenario.
        
        Args:
            scenario_title: Title of the scenario
            scenario_description: Detailed description
            choices: List of available choices with impacts
            player_wealth: Current player wealth
            player_happiness: Current happiness score
            language: Language code ('en', 'hi', 'mr')
        
        Returns:
            AdviceResult with advice text and metadata
        """
        # Validate language
        try:
            lang_enum = Language(language)
        except ValueError:
            lang_enum = Language.ENGLISH
            language = 'en'
        
        # Check cache first
        if self.cache:
            cached_advice = self.cache.get(scenario_title, player_wealth, player_happiness, language)
            if cached_advice:
                return AdviceResult(
                    advice=cached_advice,
                    source='cached',
                    success=True,
                    language=language
                )
        
        # Detect category
        category = self._detect_category(scenario_title, scenario_description)
        
        # Try AI first if available
        if self.model:
            result = self._get_gemini_advice_with_retry(
                scenario_title,
                scenario_description,
                choices,
                player_wealth,
                player_happiness,
                language,
                category
            )
            
            if result.success:
                # Cache successful AI responses
                if self.cache:
                    self.cache.set(scenario_title, player_wealth, player_happiness, language, result.advice)
                return result
        
        # Fallback to curated advice
        return self._get_fallback_advice(
            scenario_title,
            scenario_description,
            choices,
            category,
            language
        )

    def _detect_category(self, title: str, description: str) -> AdviceCategory:
        """Detect scenario category based on keywords."""
        title_lower = title.lower()
        description_lower = description.lower()
        combined_text = f"{title_lower} {description_lower}"
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return AdviceCategory.GENERAL

    def _get_gemini_advice_with_retry(
        self,
        title: str,
        description: str,
        choices: List[Dict],
        wealth: int,
        happiness: int,
        language: str,
        category: AdviceCategory
    ) -> AdviceResult:
        """Get advice from Gemini API with retry logic."""
        
        for attempt in range(self.max_retries):
            try:
                result = self._get_gemini_advice(
                    title, description, choices, wealth, happiness, language, category
                )
                return result
                
            except Exception as e:
                print(f"❌ Gemini API attempt {attempt + 1}/{self.max_retries} failed: {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    print(f"⏳ Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print("❌ All Gemini API attempts failed. Falling back to curated advice.")
                    return AdviceResult(
                        advice="",
                        source='ai',
                        success=False,
                        language=language
                    )

    def _get_gemini_advice(
        self,
        title: str,
        description: str,
        choices: List[Dict],
        wealth: int,
        happiness: int,
        language: str,
        category: AdviceCategory
    ) -> AdviceResult:
        """Get advice from Gemini API."""
        
        # Format choices
        choices_text = "\n".join([
            f"- {c['text']} (Wealth: {c.get('wealth_impact', 0):+}, Happiness: {c.get('happiness_impact', 0):+})"
            for c in choices
        ])
        
        # Language-specific instructions
        lang_instructions = self._get_language_instructions(language)
        
        # Category-specific context
        category_context = self._get_category_context(category, language)
        
        prompt = f"""{lang_instructions['role']}

**Current Status:**
- Wealth: ₹{wealth:,}
- Happiness: {happiness}/100

**Scenario Category:** {category.value.title()}
{category_context}

**Scenario:** {title}
{description}

**Available Choices:**
{choices_text}

{lang_instructions['instruction']}
"""

        response = self.model.generate_content(prompt)
        advice_text = response.text.strip()
        
        return AdviceResult(
            advice=advice_text,
            source='ai',
            success=True,
            language=language,
            category=category.value,
            confidence=0.95  # High confidence for AI responses
        )

    @staticmethod
    def _get_language_instructions(language: str) -> Dict[str, str]:
        """Get language-specific prompt instructions."""
        
        instructions = {
            'en': {
                'role': "You are a friendly Indian financial advisor in a financial literacy game called Arth-Neeti.",
                'instruction': "Give brief, practical financial advice (2-3 sentences max) in a friendly tone. Consider the 50-30-20 rule (50% needs, 30% wants, 20% savings). Don't explicitly say which option to pick, but guide them toward smart financial thinking. Use simple language appropriate for someone new to personal finance."
            },
            'hi': {
                'role': "आप अर्थ-नीति नामक वित्तीय साक्षरता खेल में एक मित्रवत भारतीय वित्तीय सलाहकार हैं।",
                'instruction': "संक्षिप्त, व्यावहारिक वित्तीय सलाह दें (अधिकतम 2-3 वाक्य) मित्रवत भाषा में। 50-30-20 नियम पर विचार करें (50% जरूरतें, 30% इच्छाएं, 20% बचत)। सीधे कौन सा विकल्प चुनना है यह न बताएं, लेकिन उन्हें स्मार्ट वित्तीय सोच की ओर मार्गदर्शन करें। व्यक्तिगत वित्त में नए लोगों के लिए उपयुक्त सरल भाषा का उपयोग करें।"
            },
            'mr': {
                'role': "तुम्ही अर्थ-नीती नावाच्या आर्थिक साक्षरता खेळातील एक मैत्रीपूर्ण भारतीय आर्थिक सल्लागार आहात.",
                'instruction': "संक्षिप्त, व्यावहारिक आर्थिक सल्ला द्या (जास्तीत जास्त 2-3 वाक्ये) मैत्रीपूर्ण भाषेत. 50-30-20 नियमाचा विचार करा (50% गरजा, 30% इच्छा, 20% बचत). कोणता पर्याय निवडायचा हे स्पष्टपणे सांगू नका, परंतु त्यांना स्मार्ट आर्थिक विचारांकडे मार्गदर्शन करा. वैयक्तिक वित्तामध्ये नवीन असलेल्यांसाठी योग्य सोपी भाषा वापरा."
            }
        }
        
        return instructions.get(language, instructions['en'])

    @staticmethod
    def _get_category_context(category: AdviceCategory, language: str) -> str:
        """Get category-specific context for better advice."""
        
        contexts = {
            'en': {
                AdviceCategory.SOCIAL: "Context: Social spending can strengthen relationships but shouldn't compromise financial goals.",
                AdviceCategory.SHOPPING: "Context: Impulse purchases are the #1 budget killer. The 24-hour rule helps avoid regret.",
                AdviceCategory.INVESTMENT: "Context: Starting early is crucial. Even small SIPs compound significantly over time.",
                AdviceCategory.DEBT: "Context: High-interest debt (credit cards, instant loans) creates financial traps. Good debt builds assets.",
                AdviceCategory.EMERGENCY: "Context: Emergency funds prevent debt spirals. Aim for 3-6 months of expenses saved.",
                AdviceCategory.GADGETS: "Context: Electronics depreciate fast. Consider: need vs want, total cost with interest.",
                AdviceCategory.INSURANCE: "Context: Insurance is protection, not investment. Term insurance + health cover are essentials.",
                AdviceCategory.GENERAL: "Context: Financial discipline today creates freedom tomorrow."
            },
            'hi': {
                AdviceCategory.SOCIAL: "संदर्भ: सामाजिक खर्च रिश्तों को मजबूत कर सकता है लेकिन वित्तीय लक्ष्यों से समझौता नहीं करना चाहिए।",
                AdviceCategory.SHOPPING: "संदर्भ: आवेगपूर्ण खरीदारी बजट का सबसे बड़ा दुश्मन है। 24 घंटे का नियम पछतावे से बचाता है।",
                AdviceCategory.INVESTMENT: "संदर्भ: जल्दी शुरुआत करना महत्वपूर्ण है। छोटे SIP भी समय के साथ बड़े बनते हैं।",
                AdviceCategory.DEBT: "संदर्भ: उच्च ब्याज वाले कर्ज (क्रेडिट कार्ड, त्वरित ऋण) वित्तीय जाल बनाते हैं। अच्छा कर्ज संपत्ति बनाता है।",
                AdviceCategory.EMERGENCY: "संदर्भ: आपातकालीन फंड कर्ज के चक्र से बचाता है। 3-6 महीने के खर्च की बचत रखें।",
                AdviceCategory.GADGETS: "संदर्भ: इलेक्ट्रॉनिक्स जल्दी सस्ते हो जाते हैं। विचार करें: जरूरत vs चाह, ब्याज सहित कुल लागत।",
                AdviceCategory.INSURANCE: "संदर्भ: बीमा सुरक्षा है, निवेश नहीं। टर्म इंश्योरेंस + हेल्थ कवर जरूरी हैं।",
                AdviceCategory.GENERAL: "संदर्भ: आज का वित्तीय अनुशासन कल की स्वतंत्रता बनाता है।"
            }
        }
        
        lang_contexts = contexts.get(language, contexts['en'])
        return lang_contexts.get(category, lang_contexts[AdviceCategory.GENERAL])

    def _get_fallback_advice(
        self,
        title: str,
        description: str,
        choices: List[Dict],
        category: AdviceCategory,
        language: str
    ) -> AdviceResult:
        """
        Return curated fallback advice based on scenario category.
        Now supports multiple languages.
        """
        
        # Get advice pool for category and language
        advice_pool = self._get_advice_pool(category, language)
        
        # Select random advice from pool
        advice = random.choice(advice_pool)
        
        return AdviceResult(
            advice=advice,
            source='curated',
            success=True,
            language=language,
            category=category.value,
            confidence=0.8  # Good confidence for curated content
        )

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
