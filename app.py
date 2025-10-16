import os
import re
import requests
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")

# --- Validate API keys ---
if not OPENAI_KEY:
    st.error("🔑 Missing OpenAI API key in .env file.")
    st.stop()
if not FINNHUB_KEY:
    st.error("💹 Missing Finnhub API key in .env file.")
    st.stop()

client = OpenAI(api_key=OPENAI_KEY)

# --- Streamlit UI setup ---
st.set_page_config(page_title="TopPicks Today", page_icon="📈", layout="centered")
st.title("📈 TopPicks Today")
st.write("Get real trending stocks from today's market news — with quick AI insights on why they matter.")

# --- Step 1: Get tickers from Finnhub's latest news ---
@st.cache_data(ttl=1800)  # cache 30 minutes
def get_trending_tickers(limit=5):
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
        res = requests.get(url, timeout=10)
        
        if res.status_code != 200:
            st.error(f"API Error: {res.status_code}")
            return []

        data = res.json()
        
        tickers = []
        ticker_counts = {}  # Track frequency
        
        # Known stock tickers to look for (top 100 most traded)
        common_tickers = {
            "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", 
            "BRK.B", "LLY", "AVGO", "JPM", "V", "UNH", "XOM", "WMT", "MA", 
            "PG", "JNJ", "HD", "COST", "ABBV", "CVX", "MRK", "ORCL", "KO", 
            "BAC", "PEP", "AMD", "CRM", "NFLX", "ACN", "TMO", "CSCO", "LIN",
            "ABT", "MCD", "DHR", "INTC", "PM", "TXN", "INTU", "GE", "CMCSA",
            "CAT", "QCOM", "ISRG", "VZ", "AMGN", "SPGI", "HON", "NEE", "UNP",
            "IBM", "GS", "LOW", "RTX", "BA", "T", "AMAT", "BLK", "ELV", "PLD",
            "DE", "SYK", "AXP", "BKNG", "MS", "TJX", "C", "VRTX", "GILD", "PFE"
        }
        
        for article in data[:50]:  # Check more articles
            # Get headline and summary
            headline = article.get("headline", "")
            summary = article.get("summary", "")
            text = f"{headline} {summary}".upper()
            
            # Look for ticker mentions with $ or parentheses
            # Examples: "Apple (AAPL)" or "$TSLA" or "NASDAQ:MSFT"
            patterns = [
                r'\(([A-Z]{1,5})\)',  # (TICKER)
                r'\$([A-Z]{1,5})\b',  # $TICKER
                r'NASDAQ:([A-Z]{1,5})',  # NASDAQ:TICKER
                r'NYSE:([A-Z]{1,5})',  # NYSE:TICKER
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                for ticker in matches:
                    if ticker in common_tickers:
                        ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        
        # Sort by frequency and get top ones
        sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
        tickers = [t[0] for t in sorted_tickers[:limit]]
        
        st.success(f"✅ Found {len(tickers)} trending tickers from news!")
        
        # If still nothing, use AI to extract from headlines
        if not tickers:
            st.info("Using AI to identify trending stocks from news headlines...")
            return get_tickers_with_ai(data[:20])
        
        return tickers

    except Exception as e:
        st.error(f"⚠️ Failed to fetch trending tickers: {e}")
        return []

# --- AI-powered ticker extraction ---
def get_tickers_with_ai(articles):
    """Use OpenAI to extract ticker symbols from news headlines"""
    headlines = "\n".join([
        f"- {article.get('headline', '')}" 
        for article in articles[:15]
    ])
    
    prompt = f"""From these recent financial news headlines, identify the 5 most mentioned stock ticker symbols (like AAPL, TSLA, MSFT, etc.).

Headlines:
{headlines}

Return ONLY a comma-separated list of ticker symbols, nothing else. For example: AAPL,MSFT,GOOGL,TSLA,NVDA"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract stock ticker symbols from news headlines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        tickers = [t.strip() for t in result.split(",") if re.match(r'^[A-Z]{1,5}$', t.strip())]
        return tickers[:5]
    except:
        # Ultimate fallback
        return ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]

# --- Step 2: Get quote data for each ticker ---
def get_stock_quotes(tickers):
    results = []
    for symbol in tickers:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_KEY}"
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            q = r.json()
            if q.get("c"):  # current price exists
                results.append({
                    "symbol": symbol,
                    "price": q["c"],
                    "change": q.get("d", 0),
                    "percent": q.get("dp", 0)
                })
        except (requests.RequestException, ValueError, KeyError):
            continue
    return results

# --- Step 3: AI insights generation ---
def get_ai_insights(stocks):
    if not stocks:
        return None

    market_data = "\n".join([
        f"- {s['symbol']}: ${s['price']:.2f} ({s['percent']:+.2f}%)"
        for s in stocks
    ])

    prompt = (
        f"These are today's trending stocks mentioned in recent market news:\n"
        f"{market_data}\n\n"
        "For each stock, write one short and simple sentence explaining "
        "why investors might find it interesting today. "
        "Keep it conversational and avoid financial jargon."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise, friendly financial assistant."},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"⚠️ Failed to generate AI insights: {e}")
        return None

# --- Main Action Button ---
if st.button("Show Today's Top Picks"):
    with st.spinner("Gathering live market data..."):
        tickers = get_trending_tickers(limit=5)
        if not tickers:
            st.warning("No trending tickers found at the moment.")
        else:
            stocks = get_stock_quotes(tickers)
            if not stocks:
                st.warning("No stock data available.")
            else:
                insights = get_ai_insights(stocks)
                st.session_state["result"] = (stocks, insights)

# --- Display Results ---
if "result" in st.session_state:
    stocks, insights = st.session_state["result"]

    if insights:
        st.subheader("💡 AI Insights")
        st.write(insights)
        st.write("---")

    if stocks:
        st.subheader("📊 Real Trending Stocks")
        for s in stocks:
            st.markdown(
                f"**{s['symbol']}** — ${s['price']:.2f} "
                f"({s['percent']:+.2f}%)"
            )
            st.write("---")

# --- Refresh Button ---
if st.button("🔄 Get New Picks"):
    get_trending_tickers.clear()  # Clear cache for fresh data
    st.session_state.pop("result", None)
    st.rerun()