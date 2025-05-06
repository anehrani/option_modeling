

# import os
# import sys

# # Add the src directory to the Python path
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

# from app import main



import ccxt
import pandas as pd
import time
from datetime import datetime, timedelta

# Connect to Deribit
exchange = ccxt.deribit()
exchange.load_markets()

# Get current spot price
btc_price = exchange.fetch_ticker('BTC/USDT')['last']

# Get all options expiring today
def get_same_day_options():
    markets = exchange.load_markets()
    today = datetime.utcnow().strftime('%Y-%m-%d')
    options = []

    for symbol, market in markets.items():
        if market['type'] != 'option' or market['base'] != 'BTC':
            continue

        expiry_ts = market.get('expiry')
        if not expiry_ts:
            continue

        expiry_date = datetime.utcfromtimestamp(expiry_ts / 1000).strftime('%Y-%m-%d')
        if expiry_date != today:
            continue

        options.append({
            'symbol': symbol,
            'strike': market['strike'],
            'expiry': expiry_date,
            'optionType': market['optionType'],
        })
    return options

# Score & filter options
def analyze_options(options, spot):
    candidates = []
    for opt in options:
        try:
            ticker = exchange.fetch_ticker(opt['symbol'])
            mark_iv = float(ticker['info'].get('mark_iv', 0))
            delta = float(ticker['info'].get('delta', 0))
            theta = float(ticker['info'].get('theta', 0))
            price = ticker['last'] or ticker['ask'] or 0

            # Filter logic
            if price < 10 or abs(delta) > 0.25 or mark_iv < 0.5:
                continue

            distance = abs(opt['strike'] - spot)
            score = (price / distance) + theta + (mark_iv * 0.1)

            candidates.append({
                **opt,
                'price': price,
                'delta': delta,
                'theta': theta,
                'iv': mark_iv,
                'score': score,
            })
        except Exception as e:
            continue
    return sorted(candidates, key=lambda x: -x['score'])

# Paper trading logic
def paper_trade(options, spot_at_expiry):
    pnl = 0
    for opt in options:
        strike = opt['strike']
        option_type = opt['optionType']
        price_sold = opt['price']

        if (option_type == 'call' and spot_at_expiry > strike) or \
           (option_type == 'put' and spot_at_expiry < strike):
            loss = abs(spot_at_expiry - strike)
            pnl += (price_sold - loss)
        else:
            pnl += price_sold
    return pnl

if __name__ == "__main__":

    same_day_options = get_same_day_options()
    top_picks = analyze_options(same_day_options, btc_price)[:5]

    print("📈 Top Options to Sell Today:")
    df = pd.DataFrame(top_picks)
    print(df[['symbol', 'strike', 'optionType', 'price', 'delta', 'iv', 'theta', 'score']])

    # --- Backtest Simulation ---
    # Fake BTC price at expiry (you can customize this or simulate multiple)
    spot_at_expiry = btc_price  # assume BTC doesn't move much

    paper_pnl = paper_trade(top_picks, spot_at_expiry)
    print(f"\n🧪 Simulated paper P&L (assuming expiry at ${spot_at_expiry:.0f}): ${paper_pnl:.2f}")
