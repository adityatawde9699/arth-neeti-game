import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from game_engine.models import GameSession, PortfolioItem, TransactionLedger

def verify():
    sessions = GameSession.objects.all()
    print(f"Total Sessions: {sessions.count()}")
    
    total_portfolio_items = PortfolioItem.objects.count()
    print(f"Total Portfolio Items: {total_portfolio_items}")
    
    total_ledger_items = TransactionLedger.objects.count()
    print(f"Total Ledger Items: {total_ledger_items}")

    for session in sessions:
        # Check if portfolio items match JSON
        json_portfolio = session.portfolio or {}
        db_portfolio = session.portfolio_items.all()
        
        # Simple count check
        json_count = len([k for k, v in json_portfolio.items() if v > 0])
        db_count = db_portfolio.count()
        
        if json_count != db_count:
            print(f"MISMATCH Session {session.id}: JSON has {json_count}, DB has {db_count}")
        else:
            # check values
            for item in db_portfolio:
                if json_portfolio.get(item.sector) != item.units:
                     print(f"VALUE MISMATCH Session {session.id} Sector {item.sector}: JSON {json_portfolio.get(item.sector)} != DB {item.units}")

        # Check Ledger
        # Harder to check exact match without parsing logic again, but count should be consistent
        json_history = session.purchase_history or []
        db_history = session.transactions.filter(transaction_type='BUY')
        
        if len(json_history) != db_history.count():
             print(f"HISTORY MISMATCH Session {session.id}: JSON {len(json_history)}, DB {db_history.count()}")

    print("Verification Complete.")

if __name__ == '__main__':
    verify()
