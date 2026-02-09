from django.contrib import admin
from .models import GameSession, ScenarioCard, Choice, PlayerChoice, PersonaProfile, IncomeSource


class ChoiceInline(admin.TabularInline):
    """Inline admin for adding Choices directly on ScenarioCard page."""
    model = Choice
    extra = 2  # Show 2 empty forms by default


@admin.register(ScenarioCard)
class ScenarioCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'min_month', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['title', 'description']
    inlines = [ChoiceInline]


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'current_month', 'wealth', 'happiness',
        'real_estate_holdings', 'gold_holdings', 'current_level',
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'current_month']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['card', 'text', 'wealth_impact', 'happiness_impact', 'is_recommended']
    list_filter = ['is_recommended', 'card__category']
    search_fields = ['text', 'card__title']


@admin.register(PlayerChoice)
class PlayerChoiceAdmin(admin.ModelAdmin):
    list_display = ['session', 'card', 'choice', 'chosen_at']
    list_filter = ['chosen_at']
    readonly_fields = ['chosen_at']


@admin.register(PersonaProfile)
class PersonaProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'career_stage', 'responsibility_level', 'risk_appetite', 'created_at']
    list_filter = ['career_stage', 'responsibility_level', 'risk_appetite']
    search_fields = ['session__user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(IncomeSource)
class IncomeSourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'source_type', 'amount_base', 'frequency', 'created_at']
    list_filter = ['source_type', 'frequency']
    search_fields = ['session__user__username']
    readonly_fields = ['created_at']
