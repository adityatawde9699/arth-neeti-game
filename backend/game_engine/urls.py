from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    # NOTE: register/ and login/ routes removed - handled by Firebase client-side
    path('profile/', views.get_profile, name='profile'),
    
    # Game
    path('start-game/', views.start_game, name='start-game'),
    path('get-card/<int:session_id>/', views.get_card, name='get-card'),
    path('submit-choice/', views.submit_choice, name='submit-choice'),
    path('take-loan/', views.take_loan, name='take-loan'),
    path('skip-card/', views.skip_card, name='skip-card'),
    path('session/<int:session_id>/', views.get_session, name='get-session'),
    path('use-lifeline/', views.use_lifeline, name='use-lifeline'),
    path('ai-advice/', views.get_ai_advice, name='ai-advice'),
    path('leaderboard/', views.get_leaderboard, name='leaderboard'),
    
    # Stock Market
    path('buy-stock/', views.buy_stock, name='buy-stock'),
    path('sell-stock/', views.sell_stock, name='sell-stock'),
    path('market-status/<int:session_id>/', views.market_status, name='market-status'),
    path('trade/futures/', views.trade_futures, name='trade-futures'),
    path('market/history/<int:session_id>/', views.get_market_history, name='market-history'),
    
    # Mutual Funds & IPOs
    path('market/mutual-fund/invest/', views.invest_mutual_fund, name='invest-mutual-fund'),
    path('market/mutual-fund/redeem/', views.redeem_mutual_fund, name='redeem-mutual-fund'),
    path('market/ipo/apply/', views.apply_ipo, name='apply-ipo'),
]
