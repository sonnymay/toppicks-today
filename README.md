# 📈 TopPicks Today

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)
![Finnhub](https://img.shields.io/badge/Finnhub-00ADEF?style=flat&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

**TopPicks Today** is a real-time, AI-powered stock insight app that scans the latest financial news, detects the most mentioned stocks, and explains in plain English *why they're trending today.*

Built with **Python**, **Streamlit**, **Finnhub API**, and **OpenAI GPT API**.

---

## ✨ Features

- 📰 **Live News Scanning** — Fetches today's market headlines from Finnhub
- 🤖 **AI Ticker Extraction** — Detects trending tickers using regex + GPT fallback
- 💡 **AI Insights** — Explains in one friendly sentence why each stock stands out
- 💰 **Real-Time Prices** — Displays current stock price, change, and % movement
- 🔄 **One-Click Refresh** — Instantly fetches new market picks

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web UI framework |
| Finnhub API | Live financial news + price data |
| OpenAI GPT API | Ticker extraction + plain-English insights |
| Regex | Fallback ticker detection from headlines |

---

## 💼 What This Code Shows

- Real-world **OpenAI API integration** with prompt engineering
- **Third-party REST API** consumption (Finnhub) with error handling
- **Streamlit** app architecture for rapid data app development
- Combining **regex + LLM** for robust entity extraction from free text
- Clean, readable Python with a focus on user-facing output

---

## 🚀 Run Locally

```bash
git clone https://github.com/sonnymay/toppicks-today
cd toppicks-today
pip install -r requirements.txt
```

Create a `.env` file or set secrets in Streamlit:

```
FINNHUB_API_KEY=your_finnhub_key
OPENAI_API_KEY=your_openai_key
```

Then run:

```bash
streamlit run app.py
```

---

## 📄 License

MIT
