import random
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import (
    GameSession, ScenarioCard, Choice, PlayerChoice,
    PlayerProfile, GameHistory, MarketEvent, RecurringExpense
)
from .serializers import (
    GameSessionSerializer, ScenarioCardSerializer, SubmitChoiceSerializer,
    PlayerProfileSerializer, GameHistorySerializer, RecurringExpenseSerializer
)
from .advisor import get_advisor
from .services import GameEngine


# ==================== AUTHENTICATION ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user and create their profile."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    email = request.data.get('email', '').strip()

    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 6:
        return Response(
            {'error': 'Password must be at least 6 characters.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already taken.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create user (signal auto-creates PlayerProfile)
    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'Registration successful!',
        'token': token.key,
        'username': user.username
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Authenticate user and return token."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user:
        token, _ = Token.objects.get_or_create(user=user)
        profile = PlayerProfileSerializer(user.profile).data if hasattr(user, 'profile') else {}
        return Response({
            'message': 'Login successful!',
            'token': token.key,
            'username': user.username,
            'profile': profile
        })

    return Response(
        {'error': 'Invalid username or password.'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Get current user's profile and game history."""
    user = request.user
    
    # Ensure profile exists
    profile, _ = PlayerProfile.objects.get_or_create(user=user)
    
    # Get game history
    history = GameHistory.objects.filter(user=user)[:10]
    
    return Response({
        'profile': PlayerProfileSerializer(profile).data,
        'game_history': GameHistorySerializer(history, many=True).data
    })


# ==================== GAME ENDPOINTS ====================



@api_view(['POST'])
def start_game(request):
    """Start a new game session using the Game Engine."""
    
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

    # Use Engine to start session
    session = GameEngine.start_new_session(user)

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

    # Use GameEngine for smart selection
    card = GameEngine.get_next_card(session)

    if not card:
        return Response({
            'message': 'No more scenarios available!',
            'game_complete': True,
            'session': GameSessionSerializer(session).data
        })

    serializer = ScenarioCardSerializer(card)
    
    # Calculate remaining (approximation)
    remaining = ScenarioCard.objects.filter(min_month__lte=session.current_month).count()
    
    return Response({
        'card': serializer.data,
        'session': GameSessionSerializer(session).data,
        # Just return a placeholder or calculate if needed
        'cards_remaining': remaining 
    })


@api_view(['POST'])
def submit_choice(request):
    """
    Process a player's choice via the GameEngine.
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

    # DELEGATE TO ENGINE
    result = GameEngine.process_choice(session, choice.card, choice)
    
    response_data = {
        'feedback': result['feedback'],
        'was_recommended': choice.is_recommended,
        'session': GameSessionSerializer(result['session']).data,
        'game_over': result['game_over'],
    }

    if result['game_over']:
        response_data['game_over_reason'] = result['game_over_reason']
        response_data['final_persona'] = result['final_persona']

    return Response(response_data)


@api_view(['POST'])
def take_loan(request):
    """
    Emergency loan endpoint.
    """
    session_id = request.data.get('session_id')
    loan_type = request.data.get('loan_type')

    if not session_id or not loan_type:
        return Response({'error': 'Missing params.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
        # SECURITY CHECK
        GameEngine.validate_ownership(request.user, session)
        
        # LOGIC
        result = GameEngine.process_loan(session, loan_type)
        if 'error' in result:
             return Response(result, status=status.HTTP_400_BAD_REQUEST)
             
        return Response({
            'session': GameSessionSerializer(session).data,
            'message': result['message']
        })
        
    except GameSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def skip_card(request):
    """
    Skip the current scenario card.
    """
    session_id = request.data.get('session_id')
    card_id = request.data.get('card_id')

    if not session_id or not card_id:
        return Response({'error': 'Missing params.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
        GameEngine.validate_ownership(request.user, session)
        
        card = ScenarioCard.objects.get(id=card_id)
        
        result = GameEngine.process_skip(session, card)
        
        return Response({
            'session': GameSessionSerializer(session).data,
            'message': result['message'],
            'skipped': True
        })
        
    except (GameSession.DoesNotExist, ScenarioCard.DoesNotExist):
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)





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

    # Delegate to Engine
    result = GameEngine.use_lifeline(session, card)
    
    if 'error' in result:
        return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'hint': result['hint'],
        'choice_id': result.get('choice_id'), # Add this to frontend
        'lifelines_remaining': result['lifelines_remaining'],
        'session': GameSessionSerializer(session).data
    })


@api_view(['POST'])
def get_ai_advice(request):
    """
    Get AI-powered financial advice for the current scenario.
    Uses Gemini API if available, otherwise returns curated fallback advice.
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

    try:
        card = ScenarioCard.objects.get(id=card_id)
    except ScenarioCard.DoesNotExist:
        return Response(
            {'error': 'Card not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Get choices for the card
    choices = [
        {
            'text': c.text,
            'wealth_impact': c.wealth_impact,
            'happiness_impact': c.happiness_impact,
        }
        for c in card.choices.all()
    ]

    # Get advice from the advisor
    advisor = get_advisor()
    result = advisor.get_advice(
        scenario_title=card.title,
        scenario_description=card.description,
        choices=choices,
        player_wealth=session.wealth,
        player_happiness=session.happiness
    )

    return Response({
        'advice': result['advice'],
        'source': result['source'],
    })


@api_view(['GET'])
def get_leaderboard(request):
    """
    Get top 10 players by final score.
    """
    # Get completed sessions with highest scores
    top_sessions = GameSession.objects.filter(
        is_active=False
    ).order_by('-financial_literacy', '-wealth')[:10]

    leaderboard = []
    for i, session in enumerate(top_sessions, 1):
        # Calculate Portfolio Value
        portfolio_val = 0
        if session.portfolio and session.market_prices:
             for sector, units in session.portfolio.items():
                 price = session.market_prices.get(sector, 0)
                 portfolio_val += (units * price)
        
        total_wealth = session.wealth + int(portfolio_val)

        # Calculate a composite score
        score = (
            session.financial_literacy * 10 +
            max(0, total_wealth) // 1000 +
            session.credit_score // 10
        )
        
        # Use GameEngine for persona (Fixed 500 Error)
        persona_data = GameEngine.generate_persona(session)
        
        leaderboard.append({
            'rank': i,
            'player_name': session.user.username.replace('Guest_', 'Player '),
            'score': score,
            'wealth': total_wealth, # Display Net Worth instead of just Cash
            'credit_score': session.credit_score,
            'persona': persona_data['persona'],
        })

    return Response({
        'leaderboard': leaderboard
    })


@api_view(['POST'])
def buy_stock(request):
    """Buy units of a stock sector."""
    session_id = request.data.get('session_id')
    sector = request.data.get('sector', '').lower()
    amount = request.data.get('amount', 0)

    if not session_id:
        return Response({'error': 'session_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
        GameEngine.validate_ownership(request.user, session)
        
        amount = int(amount) # Front end sends invest amount in Rupees
        result = GameEngine.buy_stock(session, sector, amount)
        
        if 'error' in result:
             return Response(result, status=status.HTTP_400_BAD_REQUEST)
             
        return Response({
            'session': GameSessionSerializer(session).data,
            'message': result['message']
        })

    except (ValueError, TypeError):
        return Response({'error': 'Invalid amount.'}, status=status.HTTP_400_BAD_REQUEST)
    except GameSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def sell_stock(request):
    """Sell units of a stock sector."""
    session_id = request.data.get('session_id')
    sector = request.data.get('sector', '').lower()
    amount = request.data.get('amount', 0) # Units

    if not session_id:
        return Response({'error': 'session_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
        GameEngine.validate_ownership(request.user, session)
        
        result = GameEngine.sell_stock(session, sector, amount)
        
        if 'error' in result:
             return Response(result, status=status.HTTP_400_BAD_REQUEST)
             
        return Response({
            'session': GameSessionSerializer(session).data,
            'message': result['message']
        })

    except (ValueError, TypeError):
        return Response({'error': 'Invalid amount.'}, status=status.HTTP_400_BAD_REQUEST)
    except GameSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionDenied:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)




@api_view(['GET'])
def market_status(request, session_id):
    """Get current market prices and portfolio value."""
    try:
        session = GameSession.objects.get(id=session_id, is_active=True)
    except GameSession.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Calculate portfolio value
    portfolio_value = 0
    holdings = []
    
    # We need to know the sectors. GameEngine defines them.
    stock_sectors = ['gold', 'tech', 'real_estate'] # Or import from GameEngine.CONFIG ideally
    
    for sector in stock_sectors:
        units = session.portfolio.get(sector, 0)
        price = session.market_prices.get(sector, 100)
        value = int(units * price)
        portfolio_value += value
        holdings.append({
            'sector': sector,
            'units': round(units, 2),
            'current_price': price,
            'value': value
        })

    return Response({
        'market_prices': session.market_prices,
        'portfolio': holdings,
        'total_portfolio_value': portfolio_value,
        'net_worth': session.wealth + portfolio_value
    })
