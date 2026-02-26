""" Market, stock trading, mutual fund, and IPO logic. """
import random
import logging

from ..models import RecurringExpense, StockHistory, FuturesContract, GameSession
from .config import GameEngineConfig

logger = logging.getLogger(__name__)


class MarketService:
    """Stock trading, mutual funds, futures, and IPO operations."""

    @staticmethod
    def update_market_prices(session):
        """
        Apply momentum/trends to prices each month.
        Returns list of significant changes for the news feed.
        """
        CONFIG = GameEngineConfig.CONFIG
        if not session.market_prices:
            return []

        changes = []
        new_month = session.current_month

        histories = StockHistory.objects.filter(session=session, month=new_month)

        for record in histories:
            old_price = session.market_prices.get(record.sector, 0)
            new_price = record.price

            session.market_prices[record.sector] = new_price

            if old_price > 0:
                pct_change = ((new_price - old_price) / old_price) * 100
                if abs(pct_change) > 5:
                    direction = "surged" if pct_change > 0 else "tanked"
                    changes.append(f"{record.sector.title()} {direction} {abs(pct_change):.1f}%")

        # Update Mutual Fund NAVs
        for mf_key, mf_data in CONFIG['MUTUAL_FUNDS'].items():
            key = f"MF_{mf_key}"
            old_nav = session.market_prices.get(key, 100)

            vol = mf_data['volatility']
            change_pct = random.gauss(0.008, vol)

            new_nav = old_nav * (1 + change_pct)
            session.market_prices[key] = max(10, new_nav)

            if change_pct < -0.05:
                changes.append(f"{mf_data['name']} dropped {abs(change_pct * 100):.1f}%")

        return changes

    # ================= STOCK TRADING =================
    @staticmethod
    def buy_stock(session, sector, amount):
        """Buy stocks in a specific sector."""
        from django.db import transaction
        from .game_service import GameService
        CONFIG = GameEngineConfig.CONFIG
        
        with transaction.atomic():
            # Lock the session row to prevent race conditions
            session = GameSession.objects.select_for_update().get(id=session.id)

            GameService._refresh_level(session)
            if session.current_level < CONFIG['LEVEL_UNLOCKS']['investing']:
                return {'error': "Investing unlocks at Level 2."}
            if (
                session.current_level < CONFIG['LEVEL_UNLOCKS']['diversification']
                and session.portfolio
                and any(units > 0 for s, units in session.portfolio.items() if s != sector)
            ):
                return {'error': "Diversification unlocks at Level 3. Stick to one sector for now."}
            if sector not in CONFIG['STOCK_SECTORS']:
                return {'error': "Invalid sector."}

            if amount <= 0:
                return {'error': "Amount must be positive."}

            if session.wealth < amount:
                return {'error': "Insufficient funds."}

            current_price = session.market_prices.get(sector, 100)
            units = amount / current_price

            session.wealth -= amount
            session.portfolio[sector] = session.portfolio.get(sector, 0) + units

            session.purchase_history.append({
                "sector": sector,
                "units": units,
                "price": current_price,
                "month": session.current_month
            })

            session.save()

        return {
            'session': session,
            'message': f"Bought {units:.2f} units of {sector.title()} at ₹{current_price}."
        }

    @staticmethod
    def sell_stock(session, sector, amount):
        """Sell stocks. `amount` refers to UNITS to sell."""
        from django.db import transaction
        CONFIG = GameEngineConfig.CONFIG

        with transaction.atomic():
             # Lock the session row to prevent race conditions
            session = GameSession.objects.select_for_update().get(id=session.id)
            if sector not in CONFIG['STOCK_SECTORS']:
                return {'error': "Invalid sector."}

            units_to_sell = float(amount)

            if units_to_sell <= 0:
                return {'error': "Invalid units."}

            current_owned = session.portfolio.get(sector, 0)
            if current_owned < units_to_sell:
                return {'error': f"You only have {current_owned:.2f} units."}

            current_price = session.market_prices.get(sector, 100)
            cash_value = units_to_sell * current_price

            session.wealth += int(cash_value)
            session.portfolio[sector] = current_owned - units_to_sell
            session.save()

        return {
            'session': session,
            'message': f"Sold {units_to_sell:.2f} units for ₹{int(cash_value)}."
        }

    @staticmethod
    def sell_futures(session, sector, units, duration):
        """Executes a Futures Contract sale."""
        from .game_service import GameService
        CONFIG = GameEngineConfig.CONFIG

        GameService._refresh_level(session)
        if session.current_level < CONFIG['LEVEL_UNLOCKS']['mastery']:
            return {'error': "Mastery futures unlock at Level 4."}
        if sector not in session.market_prices:
            return {'error': "Invalid sector"}

        current_price = session.market_prices[sector]
        current_owned = session.portfolio.get(sector, 0)

        if current_owned < units:
            return {'error': f"Insufficient units. You have {current_owned}."}

        # Note: MarketPredictor is referenced but may not be defined
        # in the original codebase. Keeping the contract_price as a
        # simple premium for now.
        contract_price = current_price * (1 + 0.02 * duration)  # 2% premium per month
        total_payout = contract_price * units

        session.wealth += int(total_payout)
        session.portfolio[sector] = current_owned - units

        FuturesContract.objects.create(
            session=session,
            sector=sector,
            units=units,
            strike_price=contract_price,
            spot_price_at_sale=current_price,
            duration_months=duration,
            created_month=session.current_month
        )

        session.save()

        return {
            'message': f"Contract Sold! {units} {sector} units @ ₹{contract_price}/unit. +₹{int(total_payout)}",
            'session': session
        }

    # ================= MUTUAL FUNDS & IPOs =================
    @staticmethod
    def buy_mutual_fund(session, fund_type, amount):
        """Invest in a Mutual Fund."""
        from .game_service import GameService
        CONFIG = GameEngineConfig.CONFIG

        GameService._refresh_level(session)
        if session.current_level < CONFIG['LEVEL_UNLOCKS']['investing']:
            return {'error': "Investing unlocks at Level 3. (Mutual Funds)"}

        if fund_type not in CONFIG['MUTUAL_FUNDS']:
            return {'error': "Invalid Fund Type."}

        if amount < 500:
            return {'error': "Minimum investment is ₹500."}

        if session.wealth < amount:
            return {'error': "Insufficient funds."}

        key = f"MF_{fund_type}"
        nav = session.market_prices.get(key, 100)
        units = amount / nav

        current_data = session.mutual_funds.get(fund_type, {'units': 0.0, 'invested': 0.0})

        current_data['units'] += units
        current_data['invested'] += amount

        session.mutual_funds[fund_type] = current_data
        session.wealth -= amount
        session.save()

        return {
            'session': session,
            'message': f"Invested ₹{amount} in {CONFIG['MUTUAL_FUNDS'][fund_type]['name']}."
        }

    @staticmethod
    def sell_mutual_fund(session, fund_type, units):
        """Redeem Mutual Fund units."""
        if fund_type not in session.mutual_funds:
            return {'error': "You don't own this fund."}

        current_data = session.mutual_funds[fund_type]
        if current_data['units'] < units:
            return {'error': "Insufficient units."}

        key = f"MF_{fund_type}"
        nav = session.market_prices.get(key, 100)

        redemption_value = units * nav

        session.wealth += int(redemption_value)
        current_data['units'] -= units

        original_units = current_data['units'] + units
        if original_units > 0:
            current_data['invested'] = current_data['invested'] * (current_data['units'] / original_units)

        if current_data['units'] < 0.01:
            del session.mutual_funds[fund_type]
        else:
            session.mutual_funds[fund_type] = current_data

        session.save()

        return {
            'session': session,
            'message': f"Redeemed {units:.2f} units for ₹{int(redemption_value)}."
        }

    @staticmethod
    def apply_for_ipo(session, ipo_name, amount):
        """Apply for an IPO."""
        from .game_service import GameService
        CONFIG = GameEngineConfig.CONFIG

        GameService._refresh_level(session)

        ipo_month = None
        ipo_details = None
        for m, details in CONFIG['IPO_SCHEDULE'].items():
            if details['name'] == ipo_name:
                ipo_month = m
                ipo_details = details
                break

        if not ipo_details:
            return {'error': "Invalid IPO."}

        if session.current_month > ipo_month:
            return {'error': "IPO Closed."}
        if session.current_month < ipo_month:
            return {'error': f"IPO opens in month {ipo_month}."}

        if amount < 10000 or amount > 200000:
            return {'error': "Investment must be between ₹10k and ₹2L."}

        if session.wealth < amount:
            return {'error': "Insufficient funds."}

        for app in session.active_ipos:
            if app['name'] == ipo_name:
                return {'error': "Already applied for this IPO."}

        session.wealth -= amount
        session.active_ipos.append({
            "name": ipo_name,
            "amount": amount,
            "status": "APPLIED",
            "month": session.current_month
        })
        session.save()

        return {
            'session': session,
            'message': f"Applied for {ipo_name} IPO (₹{amount}). Allocation next month."
        }
