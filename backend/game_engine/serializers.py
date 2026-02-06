from rest_framework import serializers
from .models import (
    GameSession, ScenarioCard, Choice, PlayerProfile, 
    GameHistory, MarketEvent, RecurringExpense
)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = [
            'id', 'text', 'wealth_impact', 'happiness_impact', 
            'credit_impact', 'literacy_impact', 
            'adds_recurring_expense', 'expense_name', 'cancels_expense_name'
        ]


class ScenarioCardSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = ScenarioCard
        fields = [
            'id', 'title', 'description',
            'title_hi', 'description_hi',
            'title_mr', 'description_mr',
            'category', 'difficulty', 'choices',
            'adds_recurring_expense', 'expense_name'
        ]


class RecurringExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringExpense
        fields = ['id', 'name', 'amount', 'started_month', 'is_cancelled']


class GameSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    active_expenses = serializers.SerializerMethodField()

    class Meta:
        model = GameSession
        fields = [
            'id', 'username', 'current_month', 'wealth',
            'happiness', 'credit_score', 'financial_literacy', 
            'lifelines', 'is_active',
            'market_prices', 'portfolio', 'recurring_expenses',
            'active_expenses'
        ]
        read_only_fields = ['id', 'username', 'financial_literacy', 'lifelines']

    def get_active_expenses(self, obj):
        expenses = obj.expenses.filter(is_cancelled=False)
        return RecurringExpenseSerializer(expenses, many=True).data


class PlayerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PlayerProfile
        fields = [
            'username', 'total_games', 'highest_wealth', 'highest_score',
            'highest_credit_score', 'highest_happiness', 'highest_stock_profit',
            'badges'
        ]


class GameHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GameHistory
        fields = [
            'id', 'final_wealth', 'final_happiness', 'final_credit_score',
            'financial_literacy_score', 'persona', 'end_reason', 
            'months_played', 'played_at'
        ]


class MarketEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketEvent
        fields = ['id', 'title', 'description', 'sector_impacts']


class SubmitChoiceSerializer(serializers.Serializer):
    """Serializer for the submit-choice endpoint."""
    session_id = serializers.IntegerField()
    card_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()

    def validate(self, data):
        try:
            session = GameSession.objects.get(id=data['session_id'])
            if not session.is_active:
                raise serializers.ValidationError("Game session is not active.")
        except GameSession.DoesNotExist:
            raise serializers.ValidationError("Session not found.")

        try:
            card = ScenarioCard.objects.get(id=data['card_id'])
        except ScenarioCard.DoesNotExist:
             raise serializers.ValidationError("Card not found.")
             
        try:
            choice = Choice.objects.get(id=data['choice_id'])
        except Choice.DoesNotExist:
             raise serializers.ValidationError("Choice not found.")
             
        # Integrity Check
        if choice.card_id != card.id:
            raise serializers.ValidationError("Choice does not belong to the specified card.")
            
        # Check if already answered (Optional - strict mode)
        # if PlayerChoice.objects.filter(session=session, card=card).exists():
        #     raise serializers.ValidationError("You have already made a choice for this card.")

        return data
