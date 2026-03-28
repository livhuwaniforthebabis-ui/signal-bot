import os
import requests
import time

# Load Telegram info from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("Set TELEGRAM_TOKEN and CHAT_ID as environment variables.")

# Crypto config
CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
INTERVAL = 60  # seconds

previous_prices = {s: None for s in CRYPTO_SYMBOLS}
previous_signals = {s: None for s in CRYPTO_SYMBOLS}

def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return float(response.json()['price'])

def generate_signal(current, previous):
    if previous is None:
        return "⚪ HOLD"
    change = (current - previous) / previous
    if change >= 0.01:
        return "📈 BUY"
    elif change <= -0.01:
        return "📉 SELL"
    return "⚪ HOLD"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print("Telegram error:", e)

print("🚀 Crypto Bot started...")

while True:
    for symbol in CRYPTO_SYMBOLS:
        try:
            price = get_price(symbol)
            signal = generate_signal(price, previous_prices[symbol])
            if signal != previous_signals[symbol]:
                message = f"{symbol}\nPrice: ${price:.2f}\nSignal: {signal}"
                send_telegram(message)
                previous_signals[symbol] = signal
                print(f"Sent {symbol}: {signal}")
            previous_prices[symbol] = price
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    time.sleep(INTERVAL)
