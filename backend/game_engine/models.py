from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# --- 1. PLAYER PROFILE SYSTEM ---
class PlayerProfile(models.Model):
    """Persistent player stats across all games."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_games = models.IntegerField(default=0)
    highest_wealth = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    highest_credit_score = models.IntegerField(default=700)
    highest_happiness = models.IntegerField(default=0)
    highest_stock_profit = models.IntegerField(default=0)
    badges = models.JSONField(default=list)  # e.g., ["Savings Master", "Stock Guru"]
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class PersonaProfile(models.Model):
    class CareerStage(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        EARLY_CAREER = 'EARLY_CAREER', 'Early Career'
        MID_CAREER = 'MID_CAREER', 'Mid Career'
        LATE_CAREER = 'LATE_CAREER', 'Late Career'
        RETIRED = 'RETIRED', 'Retired'

    class ResponsibilityLevel(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'

    class RiskAppetite(models.TextChoices):
        CONSERVATIVE = 'CONSERVATIVE', 'Conservative'
        BALANCED = 'BALANCED', 'Balanced'
        AGGRESSIVE = 'AGGRESSIVE', 'Aggressive'

    session = models.OneToOneField(
        'GameSession',
        on_delete=models.CASCADE,
        related_name='persona_profile',
        null=True,
        blank=True,
    )
    career_stage = models.CharField(
        max_length=20,
        choices=CareerStage.choices,
        default=CareerStage.EARLY_CAREER,
    )
    responsibility_level = models.CharField(
        max_length=10,
        choices=ResponsibilityLevel.choices,
        default=ResponsibilityLevel.MEDIUM,
    )
    risk_appetite = models.CharField(
        max_length=15,
        choices=RiskAppetite.choices,
        default=RiskAppetite.BALANCED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.session_id:
            return f"Persona Profile - Session {self.session_id}"
        return "Persona Profile"


# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PlayerProfile.objects.create(user=instance)


# --- 2. GAME SESSION (EVOLVED) ---
class GameSession(models.Model):
    """Tracks the user's current run through the game."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions')
    current_month = models.IntegerField(default=1)  # 1 to 60 (5 years)
    wealth = models.IntegerField(default=25000)     # Starting salary in INR
    happiness = models.IntegerField(default=100)    # Mental Health / Life satisfaction
    credit_score = models.IntegerField(default=700) # CIBIL-like score
    financial_literacy = models.IntegerField(default=0)  # Hidden Score for persona
    lifelines = models.IntegerField(default=3)      # "Ask NCFE" hints available
    is_active = models.BooleanField(default=True)

    current_level = models.IntegerField(default=1)
    
    # --- NEW: Stock Market 2.0 ---
    # Market prices for each sector (starts at 100)
    market_prices = models.JSONField(default=dict)  # {"gold": 100, "tech": 100, "real_estate": 100}
    # Market trends (Momentum) - stores integer -5 to +5 indicating current trend
    market_trends = models.JSONField(default=dict)  # {"gold": 2, "tech": -5, "real_estate": 0}
    # Player's portfolio (units held per sector)
    portfolio = models.JSONField(default=dict)  # {"gold": 0, "tech": 0, "real_estate": 0}
    # NEW: Purchase history for profit calculation
    purchase_history = models.JSONField(default=list)  # [{"sector": "tech", "units": 10, "price": 100, "month": 1}]
    
    # --- NEW: Recurring Expenses ---
    # This acts as a CACHE for the total monthly drain, updated by advance_month
    recurring_expenses = models.IntegerField(default=0)

    # --- NEW: Gameplay Log & Final Report ---
    gameplay_log = models.TextField(blank=True, default="")
    final_report = models.TextField(blank=True, default="")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Initialize market prices if empty
        if not self.market_prices:
            self.market_prices = {"gold": 100, "tech": 100, "real_estate": 100}
        if not self.portfolio:
            self.portfolio = {"gold": 0, "tech": 0, "real_estate": 0}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.id} - User: {self.user.username} - Month: {self.current_month}"

    class Meta:
        ordering = ['-created_at']


class IncomeSource(models.Model):
    class SourceType(models.TextChoices):
        SALARY = 'SALARY', 'Salary'
        BUSINESS = 'BUSINESS', 'Business'
        INVESTMENT = 'INVESTMENT', 'Investment'
        FREELANCE = 'FREELANCE', 'Freelance'
        RENTAL = 'RENTAL', 'Rental'
        OTHER = 'OTHER', 'Other'

    class Frequency(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        QUARTERLY = 'QUARTERLY', 'Quarterly'
        ANNUAL = 'ANNUAL', 'Annual'
        ONE_TIME = 'ONE_TIME', 'One-time'

    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='income_sources')
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    amount_base = models.IntegerField(validators=[MinValueValidator(0)])
    variability = models.FloatField(default=0.0, validators=[MinValueValidator(0.0)])
    frequency = models.CharField(max_length=20, choices=Frequency.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source_type} - ₹{self.amount_base}"



# --- 3. GAME HISTORY (for profile dashboard) ---
class GameHistory(models.Model):
    """Summary of completed games for the profile dashboard."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_history')
    final_wealth = models.IntegerField()
    final_happiness = models.IntegerField()
    final_credit_score = models.IntegerField()
    financial_literacy_score = models.IntegerField()
    persona = models.CharField(max_length=100)
    end_reason = models.CharField(max_length=20)  # COMPLETED, BANKRUPTCY, BURNOUT
    months_played = models.IntegerField()
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.persona} ({self.played_at.date()})"

    class Meta:
        ordering = ['-played_at']


class StockHistory(models.Model):
    """
    Stores the PRE-GENERATED price trajectory for the entire game session.
    This is the 'Ground Truth' that the ML model predicts.
    """
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='market_history')
    sector = models.CharField(max_length=50) # 'tech', 'gold', 'real_estate'
    month = models.IntegerField() # 1 to 12
    price = models.IntegerField()
    
    # ML Confidence Metrics (Optional for UI)
    volatility_index = models.FloatField(default=0.0) 

    class Meta:
        ordering = ['session', 'month']
        unique_together = ('session', 'sector', 'month')

class FuturesContract(models.Model):
    """
    Represents a 'Short Selling' hedge.
    Player sells NOW at a guaranteed price based on ML prediction.
    """
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='futures_contracts')
    sector = models.CharField(max_length=50)
    units = models.FloatField()
    strike_price = models.IntegerField() # The price they got paid
    spot_price_at_sale = models.IntegerField() # Reference for analytics
    duration_months = models.IntegerField()
    created_month = models.IntegerField()
    
    # Profit/Loss calculation (Virtual, since cash is immediate)
    final_market_price = models.IntegerField(null=True, blank=True)
    is_successful = models.BooleanField(default=False) # True if Strike > Final Price

    def __str__(self):
        return f"{self.sector} Future - {self.units}u @ {self.strike_price}"


# --- 4. MARKET EVENTS (News System) ---
class MarketEvent(models.Model):
    """News events that affect stock market sectors."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Impact on next month's prices: {"tech": 1.2, "gold": 0.9} means Tech +20%, Gold -10%
    sector_impacts = models.JSONField()
    
    # When this news should appear (0 = random)
    trigger_month = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# --- 5. RECURRING EXPENSES ---
class RecurringExpense(models.Model):
    """Tracks subscriptions and recurring costs for a session."""
    CATEGORY_CHOICES = [
        ('HOUSING', 'Housing'),
        ('FOOD', 'Food'),
        ('TRANSPORT', 'Transport'),
        ('UTILITIES', 'Utilities'),
        ('LIFESTYLE', 'Lifestyle'),
        ('DEBT', 'Debt & Loans'),
        ('OTHER', 'Other')
    ]

    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='expenses')
    name = models.CharField(max_length=100)  # e.g., "Netflix Subscription"
    amount = models.IntegerField()  # Monthly cost
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    is_essential = models.BooleanField(default=False)
    inflation_rate = models.FloatField(default=0.0) # Annual inflation (e.g., 0.05)
    
    started_month = models.IntegerField()  # When expense started
    is_cancelled = models.BooleanField(default=False)
    cancelled_month = models.IntegerField(null=True, blank=True)

    def __str__(self):
        status = "Active" if not self.is_cancelled else "Cancelled"
        type_str = "Needs" if self.is_essential else "Wants"
        return f"{self.name} ({self.category} - {type_str}) - ₹{self.amount}/mo"


# --- 6. SCENARIO CARDS ---
class ScenarioCard(models.Model):
    """The events/scenarios presented to the player."""
    CATEGORY_CHOICES = [
        ('NEEDS', 'Needs'),
        ('WANTS', 'Wants'),
        ('EMERGENCY', 'Emergency'),
        ('INVESTMENT', 'Investment'),
        ('SOCIAL', 'Social Pressure'),
        ('TRAP', 'Hidden Trap'),
        ('NEWS', 'Market News'),  # NEW: For stock market events
        ('QUIZ', 'Pop Quiz'),     # NEW: For recall mechanics
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    title_hi = models.CharField(max_length=200, blank=True, null=True)
    description_hi = models.TextField(blank=True, null=True)
    title_mr = models.CharField(max_length=200, blank=True, null=True)
    description_mr = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='WANTS')
    difficulty = models.IntegerField(default=1)  # 1 (Easy) to 5 (Hard)
    min_month = models.IntegerField(default=1)   # Earliest month this card can appear
    is_active = models.BooleanField(default=True)
    
    # NEW: For NEWS cards - link to MarketEvent
    market_event = models.ForeignKey(MarketEvent, on_delete=models.SET_NULL, null=True, blank=True)
    
    # NEW: For choices that add recurring expenses
    adds_recurring_expense = models.IntegerField(default=0)  # Amount (0 = no expense)
    expense_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"

    class Meta:
        ordering = ['category', 'difficulty']


# --- 7. CHOICES ---
class Choice(models.Model):
    """The options available for each ScenarioCard."""
    card = models.ForeignKey(ScenarioCard, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)  # e.g., "Go with them (-₹10k)"
    text_hi = models.CharField(max_length=200, blank=True, null=True)
    text_mr = models.CharField(max_length=200, blank=True, null=True)

    # Consequences (Delta values)
    wealth_impact = models.IntegerField(default=0)      # e.g., -10000
    happiness_impact = models.IntegerField(default=0)   # e.g., +20
    credit_impact = models.IntegerField(default=0)      # e.g., -50
    literacy_impact = models.IntegerField(default=0)    # e.g., -5 (Bad financial decision)

    # Educational Feedback (shown after choice)
    feedback = models.TextField(blank=True)
    feedback_hi = models.TextField(blank=True, null=True)
    feedback_mr = models.TextField(blank=True, null=True)
    is_recommended = models.BooleanField(default=False)  # For analytics: was this the "right" choice?
    
    # NEW: For choices that add recurring expenses
    adds_recurring_expense = models.IntegerField(default=0)
    expense_name = models.CharField(max_length=100, blank=True)
    
    # NEW: For choices that cancel recurring expenses
    cancels_expense_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.card.title} -> {self.text[:30]}"


# --- 8. PLAYER CHOICE LOG ---
class PlayerChoice(models.Model):
    """Logs all choices made by a player in a session (for analytics & recall)."""
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='player_choices')
    card = models.ForeignKey(ScenarioCard, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)  # null = skipped
    chosen_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session.id} - {self.card.title}"
