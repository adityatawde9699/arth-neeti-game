import random
import uuid
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import GameSession, ScenarioCard, Choice, PlayerChoice
from .serializers import (
    GameSessionSerializer,
    ScenarioCardSerializer,
    SubmitChoiceSerializer
)


@api_view(['POST'])
def start_game(request):
    """
    Start a new game session.
    For demo purposes, creates/uses a demo user if not authenticated.
    """
    # Get or create a user for the session
    if request.user.is_authenticated:
        user = request.user
    else:
        # Generate unique guest username to avoid session collision
        guest_username = f"Guest_{uuid.uuid4().hex[:8]}"
        user = User.objects.create(
            username=guest_username,
            email=f"{guest_username}@guest.arthneeti.com"
        )

    # Create a new game session
    session = GameSession.objects.create(
        user=user,
        wealth=25000,      # Starting salary
        happiness=100,     # Full happiness
        credit_score=700,  # Average credit score
        current_month=1
    )

    serializer = GameSessionSerializer(session)
    return Response({
        'message': 'Game started! Welcome to Arth-Neeti.',
        'session': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_card(request, session_id):
    """
    Get a random scenario card appropriate for the current game month.
    """
    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'Session not found or inactive.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get cards that haven't been shown in this session and are appropriate for current month
    shown_card_ids = PlayerChoice.objects.filter(
        session=session
    ).values_list('card_id', flat=True)

    available_cards = ScenarioCard.objects.filter(
        is_active=True,
        min_month__lte=session.current_month
    ).exclude(id__in=shown_card_ids)

    if not available_cards.exists():
        # If all cards shown, allow repeats (or end game)
        available_cards = ScenarioCard.objects.filter(
            is_active=True,
            min_month__lte=session.current_month
        )

    if not available_cards.exists():
        return Response({
            'message': 'No more scenarios available!',
            'game_complete': True,
            'session': GameSessionSerializer(session).data
        })

    # Weighted random selection based on difficulty
    card = random.choice(list(available_cards))

    serializer = ScenarioCardSerializer(card)
    return Response({
        'card': serializer.data,
        'session': GameSessionSerializer(session).data,
        'cards_remaining': available_cards.count() - 1
    })


@api_view(['POST'])
def submit_choice(request):
    """
    Process a player's choice and update game state.
    """
    serializer = SubmitChoiceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    session_id = serializer.validated_data['session_id']
    card_id = serializer.validated_data['card_id']
    choice_id = serializer.validated_data['choice_id']

    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'Session not found or inactive.'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        choice = Choice.objects.get(id=choice_id, card_id=card_id)
    except Choice.DoesNotExist:
        return Response(
            {'error': 'Invalid choice.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Apply choice impacts
    session.wealth += choice.wealth_impact
    session.happiness += choice.happiness_impact
    session.credit_score += choice.credit_impact
    session.financial_literacy += choice.literacy_impact

    # Clamp values
    session.happiness = max(0, min(100, session.happiness))
    session.credit_score = max(300, min(900, session.credit_score))

    # Log the choice
    PlayerChoice.objects.create(
        session=session,
        card=choice.card,
        choice=choice
    )

    # Check win/loss conditions
    game_over = False
    game_over_reason = None

    if session.wealth <= 0:
        game_over = True
        game_over_reason = 'BANKRUPTCY'
        session.is_active = False
    elif session.happiness <= 0:
        game_over = True
        game_over_reason = 'BURNOUT'
        session.is_active = False

    # Advance month every 3 choices (3 cards per month × 12 months = 36 cards for 1-year game)
    choices_count = PlayerChoice.objects.filter(session=session).count()
    session.current_month = (choices_count // 3) + 1

    # Check if 1 year (12 months) completed - hackathon-friendly game length
    if session.current_month > 12:
        game_over = True
        game_over_reason = 'COMPLETED'
        session.is_active = False

    session.save()

    response_data = {
        'feedback': choice.feedback,
        'was_recommended': choice.is_recommended,
        'session': GameSessionSerializer(session).data,
        'game_over': game_over,
    }

    if game_over:
        response_data['game_over_reason'] = game_over_reason
        response_data['final_persona'] = _calculate_persona(session)

    return Response(response_data)


def _calculate_persona(session):
    """Calculate the player's financial persona based on their performance."""
    score = session.financial_literacy

    if score >= 80:
        return {
            'title': 'The Warren Buffett',
            'description': 'You made smart financial decisions consistently. Your future is secure!'
        }
    elif score >= 60:
        return {
            'title': 'The Cautious Saver',
            'description': 'You played it safe. Sometimes too safe, but your finances are stable.'
        }
    elif score >= 40:
        return {
            'title': 'The Balanced Spender',
            'description': 'You found a balance between enjoying life and saving. Well done!'
        }
    elif score >= 20:
        return {
            'title': 'The YOLO Enthusiast',
            'description': 'You lived life to the fullest! Maybe a bit too much...'
        }
    else:
        return {
            'title': 'The FOMO Victim',
            'description': 'Social pressure got the best of you. Time to learn some financial discipline!'
        }


@api_view(['GET'])
def get_session(request, session_id):
    """Get current session state."""
    try:
        session = GameSession.objects.get(id=session_id)
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'Session not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        'session': GameSessionSerializer(session).data
    })


@api_view(['POST'])
def use_lifeline(request):
    """
    Use a lifeline to reveal the recommended choice for a card.
    Costs 1 lifeline per use.
    """
    session_id = request.data.get('session_id')
    card_id = request.data.get('card_id')

    if not session_id or not card_id:
        return Response(
            {'error': 'session_id and card_id are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
    except GameSession.DoesNotExist:
        return Response(
            {'error': 'Session not found or inactive.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if session.lifelines <= 0:
        return Response(
            {'error': 'No lifelines remaining!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        card = ScenarioCard.objects.get(id=card_id)
    except ScenarioCard.DoesNotExist:
        return Response(
            {'error': 'Card not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Deduct lifeline
    session.lifelines -= 1
    session.save()

    # Get recommended choice hints
    choices = card.choices.all()
    hints = [
        {
            'choice_id': choice.id,
            'is_recommended': choice.is_recommended
        }
        for choice in choices
    ]

    return Response({
        'hints': hints,
        'lifelines_remaining': session.lifelines,
        'session': GameSessionSerializer(session).data
    })
