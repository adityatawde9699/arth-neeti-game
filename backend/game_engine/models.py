from django.db import models
from django.contrib.auth.models import User


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.id} - User: {self.user.username} - Month: {self.current_month}"

    class Meta:
        ordering = ['-created_at']


class ScenarioCard(models.Model):
    """The events/scenarios presented to the player."""
    CATEGORY_CHOICES = [
        ('NEEDS', 'Needs'),
        ('WANTS', 'Wants'),
        ('EMERGENCY', 'Emergency'),
        ('INVESTMENT', 'Investment'),
        ('SOCIAL', 'Social Pressure'),
        ('TRAP', 'Hidden Trap'),
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

    def __str__(self):
        return f"[{self.category}] {self.title}"

    class Meta:
        ordering = ['category', 'difficulty']


class Choice(models.Model):
    """The options available for each ScenarioCard."""
    card = models.ForeignKey(ScenarioCard, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)  # e.g., "Go with them (-₹10k)"

    # Consequences (Delta values)
    wealth_impact = models.IntegerField(default=0)      # e.g., -10000
    happiness_impact = models.IntegerField(default=0)   # e.g., +20
    credit_impact = models.IntegerField(default=0)      # e.g., -50
    literacy_impact = models.IntegerField(default=0)    # e.g., -5 (Bad financial decision)

    # Educational Feedback (shown after choice)
    feedback = models.TextField(blank=True)
    is_recommended = models.BooleanField(default=False)  # For analytics: was this the "right" choice?

    def __str__(self):
        return f"{self.card.title} -> {self.text[:30]}"


class PlayerChoice(models.Model):
    """Logs all choices made by a player in a session (for analytics)."""
    session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='player_choices')
    card = models.ForeignKey(ScenarioCard, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    chosen_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session.id} - {self.card.title}"
