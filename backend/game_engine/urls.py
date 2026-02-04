from django.urls import path
from . import views

urlpatterns = [
    path('start-game/', views.start_game, name='start-game'),
    path('get-card/<int:session_id>/', views.get_card, name='get-card'),
    path('submit-choice/', views.submit_choice, name='submit-choice'),
    path('take-loan/', views.take_loan, name='take-loan'),
    path('session/<int:session_id>/', views.get_session, name='get-session'),
    path('use-lifeline/', views.use_lifeline, name='use-lifeline'),
]
