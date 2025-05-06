
    # import os
    # import sys

    # # Add the src directory to the Python path
    # sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import ccxt




if __name__ == "__main__":

    # Load the Deribit exchange (supports options)
    exchange = ccxt.deribit({
        'enableRateLimit': True,
    })

    # Load markets
    markets = exchange.load_markets()

    # Filter for options
    option_markets = {symbol: market for symbol, market in markets.items() if market['type'] == 'option'}

    # Print some info
    print(f"Found {len(option_markets)} option markets on Deribit.\n")
    for symbol, market in list(option_markets.items())[:10]:  # Show a few
        print(f"{symbol} | Base: {market['base']} | Strike: {market.get('strike', 'N/A')} | Expiry: {market.get('expiry', 'N/A')} | Option Type: {market.get('optionType', 'N/A')}")




    print("done!")

