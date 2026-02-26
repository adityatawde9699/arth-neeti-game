import os
import sys
import django

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from game_engine.models import GameSession
from game_engine.services.game_service import GameService

def test_level_up():
    print("Testing Level Up Logic...")
    
    # Setup
    user, _ = User.objects.get_or_create(username='test_level_user')
    session = GameSession.objects.create(user=user, wealth=10000, current_month=1, current_level=1)
    
    # Test 1: No Change
    up, desc = GameService._refresh_level(session)
    print(f"Test 1 (No Change): Level={session.current_level}, Up={up}, Desc={desc}")
    if not up and session.current_level == 1:
        print("PASS")
    else:
        print("FAIL")

    # Test 2: Jump to Level 3 via Literacy (Fast Track)
    # Level 3 requires Month 12 OR Literacy 45
    session.financial_literacy = 50
    up, desc = GameService._refresh_level(session)
    print(f"Test 2 (Literacy Jump): Level={session.current_level}, Up={up}, Desc={desc}")
    
    if up and session.current_level == 3 and "Investing" in desc:
        print("PASS")
    else:
        print("FAIL")

    # Test 3: Jump to Level 5 via Month
    # Level 5 requires Month 36 OR Literacy 90
    session.current_month = 40
    up, desc = GameService._refresh_level(session)
    print(f"Test 3 (Time Jump): Level={session.current_level}, Up={up}, Desc={desc}")
    
    if up and session.current_level == 5 and "Mastery" in desc:
        print("PASS")
    else:
        print("FAIL")

    # Cleanup
    session.delete()
    print("Done.")

if __name__ == "__main__":
    test_level_up()
