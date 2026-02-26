import threading
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from game_engine.models import GameSession
from game_engine.services import GameEngine

class ConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester')
        self.session = GameSession.objects.create(
            user=self.user,
            wealth=100000,
            current_month=24,  # Level 4 requirements
            financial_literacy=80,
            current_level=5, # Unlock investing
            market_prices={"tech": 100}
        )
        # Ensure portfolio is initialized
        self.session.portfolio = {"tech": 0}
        self.session.save()

    def test_concurrent_buying(self):
        """
        Simulate 10 threads buying stock simultaneously.
        Without locking, this would likely result in less wealth deduction 
        or incorrect portfolio counts due to race conditions.
        """
        success_count = 0
        failure_count = 0
        lock = threading.Lock()

        def buy_stock():
            nonlocal success_count, failure_count
            try:
                # Buy 10 units worth (10 * 100 = 1000)
                result = GameEngine.buy_stock(self.session, 'tech', 1000)
                if 'error' in result:
                    print(f"Buy failed logic: {result['error']}")
                    with lock:
                        failure_count += 1
                else:
                    with lock:
                        success_count += 1
            except Exception as e:
                # Expecting OperationalError on SQLite due to locking
                print(f"Buy failed exception: {e}")
                with lock:
                    failure_count += 1

        threads = []
        for _ in range(10):
            t = threading.Thread(target=buy_stock)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Refresh from DB
        self.session.refresh_from_db()

        print(f"Successes: {success_count}, Failures: {failure_count}")

        # Expected: Wealth should decrease by 1000 * success_count
        expected_wealth = 100000 - (1000 * success_count)
        self.assertEqual(self.session.wealth, expected_wealth, 
                        f"Wealth mismatch! Expected {expected_wealth}, Got {self.session.wealth}")
        
        # Verify Portfolio
        expected_units = 10 * success_count
        self.assertEqual(self.session.portfolio.get('tech'), expected_units,
                        f"Portfolio mismatch! Expected {expected_units}, Got {self.session.portfolio.get('tech')}")
