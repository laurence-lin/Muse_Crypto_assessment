from binance.client import Client
import time
import datetime

# Replace with your API keys if needed (optional for public endpoints)
# api_key = "YOUR_API_KEY"
# api_secret = "YOUR_API_SECRET"
# client = Client(api_key, api_secret)

client = Client() # Public endpoints to access current price don't need API keys

symbol = "BTCUSDT"

def get_bitcoin_price():
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker['price'])
        timestamp = datetime.datetime.now().isoformat()
        print(f"{timestamp} - {symbol} Price: {price}")
        return price
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

def main():
    while True:
        get_bitcoin_price()
        time.sleep(600)  # 600 seconds = 10 minutes

if __name__ == "__main__":
    main()