from rest_framework import serializers
from .models import GameSession, ScenarioCard, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'wealth_impact', 'happiness_impact', 'credit_impact', 'literacy_impact']


class ScenarioCardSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = ScenarioCard
        fields = ['id', 'title', 'description', 'category', 'difficulty', 'choices']


class GameSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = GameSession
        fields = [
            'id', 'username', 'current_month', 'wealth',
            'happiness', 'credit_score', 'financial_literacy', 'lifelines', 'is_active'
        ]
        read_only_fields = ['id', 'username', 'financial_literacy', 'lifelines']


class SubmitChoiceSerializer(serializers.Serializer):
    """Serializer for the submit-choice endpoint."""
    session_id = serializers.IntegerField()
    card_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()
