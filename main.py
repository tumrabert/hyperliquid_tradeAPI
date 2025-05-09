from hyperliquid.utils import constants
import time
from hyperliquid_client import (
    setup
)
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
app = Flask(__name__)

# Global variables for exchange connection
address = None
info = None
exchange = None

def open_order(exchange, coin, is_buy, sz):
    """
    Open an order on the exchange.
    
    Args:
        exchange: The exchange object.
        coin: The coin to trade.
        is_buy: True for buy, False for sell.
        sz: Size of the order.
        
    Returns:
        The result of the order.
    """
    print(f"Attempting Market {'Buy' if is_buy else 'Sell'} {sz} {coin}.")
    order_result = exchange.market_open(coin, is_buy, sz, None, 0.01)
    if order_result["status"] == "ok":
        for status in order_result["response"]["data"]["statuses"]:
            try:
                filled = status["filled"]
                print(f'Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
            except KeyError:
                print(f'Error: {status["error"]}')
    return order_result

def close_position(exchange, coin,sz):
    """
    Close all positions for a given coin.
    
    Args:
        exchange: The exchange object.
        coin: The coin to close.
        
    Returns:
        The result of the close operation.
    """
    print(f"Attempting to Market Close {coin} amount {sz}.")
    order_result = exchange.market_close(coin=coin ,sz = sz)
    if order_result["status"] == "ok":
        for status in order_result["response"]["data"]["statuses"]:
            try:
                filled = status["filled"]
                print(f'Order #{filled["oid"]} filled {filled["totalSz"]} @{filled["avgPx"]}')
            except KeyError:
                print(f'Error: {status["error"]}')
    return order_result

@app.route('/long', methods=['POST'])
def long_position():
    try:
        data = request.json
        print(data)
        symbol = data.get('symbol', '').replace('USDT.P', '')  # Convert BTCUSDT.P to BTC
        side = data.get('side', '').lower()
        qty = float(data.get('qty', 0))
        
        # Validate inputs
        if not symbol or not side or qty <= 0:
            return jsonify({'status': 'error', 'message': 'Invalid input parameters'}), 400
            
        # For long position: buy = open long, sell = close long
        is_buy = side == 'buy'
        
        if is_buy:
            result = open_order(exchange, symbol, True, qty)
        else:
            result = close_position(exchange, symbol, qty)
            
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/short', methods=['POST'])
def short_position():
    try:
        data = request.json
        symbol = data.get('symbol', '').replace('USDT.P', '')  # Convert BTCUSDT.P to BTC
        side = data.get('side', '').lower()
        qty = float(data.get('qty', 0))
        
        # Validate inputs
        if not symbol or not side or qty <= 0:
            return jsonify({'status': 'error', 'message': 'Invalid input parameters'}), 400
            
        # For short position: sell = open short, buy = close short
        is_buy = side == 'buy'
        
        if is_buy:
            result = open_order(exchange, symbol, False, qty)
        else:
            result = close_position(exchange, symbol, qty)
            
        return jsonify({'status': 'success', 'result': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def main():
    global address, info, exchange
    load_dotenv()
    api_url = constants.TESTNET_API_URL if os.getenv("TYPE") == "dev" else constants.MAINNET_API_URL
    PORT=os.getenv("PORT", 5001)
    address, info, exchange = setup(api_url, skip_ws=True)
    # Run a test order if needed
    # coin = "BTC"
    # is_buy = False # long = True, short = False
    # sz = 0.0003
    # order_result = open_order(exchange, coin, is_buy, sz)
    # print("Waiting for 20s before closing")
    # time.sleep(20)
    # order_result = close_position(exchange, coin,0.0001)
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=PORT, debug=True)


if __name__ == "__main__":
    main()


# body params

# Long

# {"symbol":"{{ticker}}","side":"{{strategy.order.action}}","positionSide":"LONG","investmentType":"coin_qty","qty":"{{strategy.order.comment}}"}

# Short 

# {"symbol":"{{ticker}}","side":"{{strategy.order.action}}","positionSide":"SHORT","investmentType":"coin_qty","qty":"{{strategy.order.comment}}"}
