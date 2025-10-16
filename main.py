import os
import yfinance as yf
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_top_stocks():
    # Replace these tickers with your favorites or trending list
    tickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
    stocks = []
    for symbol in tickers:
        stock = yf.Ticker(symbol)
        info = stock.info
        name = info.get("shortName", symbol)
        price = info.get("regularMarketPrice")
        change = info.get("regularMarketChangePercent")
        if price:
            stocks.append({"symbol": symbol, "name": name, "price": price, "change": change})
    return stocks

def explain_stocks(stocks):
    summary = "\n".join([f"{s['name']} ({s['symbol']}): ${s['price']:.2f}, Change: {s['change']:.2f}%" for s in stocks])
    prompt = f"Here are some trending stocks:\n{summary}\n\nWrite a simple, one-line explanation for each stock saying why it might be interesting to an investor. Keep it easy to understand."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    print("Fetching top stocks...\n")
    stocks = get_top_stocks()
    result = explain_stocks(stocks)
    print(result)
