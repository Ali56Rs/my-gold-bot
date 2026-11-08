import os
import time
import telebot
import requests
import pandas as pd
from datetime import datetime

TOKEN = "9107865055:AAGhF8R6Ab0kFH808Eue8dERXj6UN87zhgw"
CHAT_ID = "8001570403"

bot = telebot.TeleBot(TOKEN)

def check_economic_calendar():
    try:
        url = "https://financialmodelingprep.com"
        news = requests.get(url, timeout=10).json()
        current_time = datetime.utcnow()
        for event in news[:10]:
            if event.get("impact") == "High" and (event.get("currency") in ["USD", "EUR"]):
                event_time = datetime.strptime(event.get("date"), "%Y-%m-%d %H:%M:%S")
                if abs((current_time - event_time).total_seconds()) < 1800:
                    return True, event.get("event")
        return False, ""
    except:
        return False, ""

def get_live_market_data(symbol):
    try:
        url = f"https://yahoo.com{symbol}=X"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        prices = res['chart']['result'][0]['indicators']['quote'][0]['close']
        df = pd.DataFrame(prices, columns=['close']).dropna()
        return df
    except:
        return None

def advanced_strategy(df):
    if len(df) < 50: return "⏳ مراقبة السوق"
    current_price = df['close'].iloc[-1]
    ma_short = df['close'].rolling(window=14).mean().iloc[-1]
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rs = gain / (loss if loss != 0 else 1)
    rsi = 100 - (100 / (1 + rs))
    
    if current_price > ma_short and rsi < 30:
        return "🔴 شراء (Buy) - فرصة قوية"
    elif current_price < ma_short and rsi > 70:
        return "🔵 بيع (Sell) - فرصة قوية"
    return "⏳ مراقبة السوق"

def core_trading_loop():
    print("🤖 البوت يعمل على خادم Render المستقل بنجاح...")
    pairs = {"EURUSD": "EURUSD", "XAUUSD": "XAUUSD"}
    while True:
        is_news_time, event_name = check_economic_calendar()
        if is_news_time:
            time.sleep(600)
            continue
        for name, sym in pairs.items():
            df = get_live_market_data(sym)
            if df is None: continue
            signal = advanced_strategy(df)
            if "فرصة قوية" in signal:
                price = df['close'].iloc[-1]
                msg = f"🚨 **إشارة تداول فنية فورية ({name})**\n📈 التوصية: {signal}\n💰 السعر الحالي: {price:.4f}\n🎯 الهدف المتوقع (TP): {price * 1.003:.4f}\n🛑 وقف الخسارة (SL): {price * 0.997:.4f}"
                bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
        time.sleep(300)

if __name__ == "__main__":
    core_trading_loop()
