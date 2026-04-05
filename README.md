 Portfolio Coverage

- **38 Indian Equities** (NSE) - Angel One (29) + Zerodha Kite (9)
- **14 Mutual Funds** (Groww MF)  
- **7 US Stocks** (NYSE/NASDAQ)
- **Total Value**: ₹6.21L (~$7.18K USD)

---

##  Key Features

###  Real-Time Market Data
- Live price updates via **yfinance API** (30-sec cache)
- Multi-threaded fetching: **50+ tickers in 5-8 seconds**
- Indices: Nifty 50, Bank Nifty, Sensex, S&P 500, VIX

###  Advanced Analytics
- **12-sector breakdown** with allocation heatmap
- **Portfolio vs Benchmark** performance tracking (Alpha calculation)
- Interactive candlestick charts (multiple timeframes)
- Top gainers/losers identification

###  Intelligent News Feed
- **RSS aggregation** from 5 sources (ET, Moneycontrol, LiveMint, CNBC, Bloomberg)
- **Sentiment analysis** (Bull/Bear/Neutral tags)
- **Portfolio-aware filtering** (only relevant stock news)

###  AI-Powered Insights
- **Claude AI integration** for geopolitical event analysis
- Impact assessment on portfolio holdings
- Automated news generation for market events

###  Multi-Broker Integration
- **Angel One** (29 stocks) | **Zerodha Kite** (9 stocks) | **Groww** (14 MFs)
- Broker-wise filtering and performance tracking
- Color-coded visualization (Orange/Blue/Green)

###  Global Markets
- **Commodities**: Gold, Silver, Crude Oil, Natural Gas, Copper
- **Crypto**: BTC, ETH, BNB, SOL, XRP, ADA
- **Forex**: USD/INR, EUR/INR, GBP/INR

---

##  Tech Stack

**Backend:** Flask, yfinance, pandas, feedparser, anthropic (Claude AI)  
**Frontend:** Vanilla JavaScript (ES6+), Chart.js, Lightweight Charts  
**Database:** Firebase Firestore, LocalStorage  
**Security:** SHA-256 hashing, Cloud sync

---

##  Screenshots

### 1. Main Dashboard
![Main Dashboard](<img width="1919" height="1079" alt="main-dashboard" src="https://github.com/user-attachments/assets/9ea95a6d-8a42-46d4-9ef5-2d82cb631af4" />)
*Complete overview: Portfolio allocation, broker breakdown, live news feed, commodities & crypto prices*

### 2. Portfolio vs Benchmark
![Portfolio Performance](screenshots/portfolio-benchmark.png)
*3-month performance: Portfolio +6.90% vs Nifty 50 +5.59% | Alpha: +1.31%*

### 3. Portfolio Heatmap
![Portfolio Heatmap](screenshots/portfolio-heatmap.png)
*Visual performance tracking: 38 stocks color-coded by daily returns (green = gains, red = losses)*

### 4. Sector Analysis
![Sector Breakdown](screenshots/sector-analysis.png)
*12 sectors tracked: Banking & Finance (↑0.45%), Energy & Power (↑1.18%), Defence (↑2.10%), IT (↑1.82%), etc.*

### 5. News Feed with Sentiment
![News Feed](screenshots/news-feed.png)
*Real-time news aggregation with Bull/Bear/Neutral sentiment tags and portfolio-specific filtering*

### 6. Geopolitical Events
![Geo Events](screenshots/geo-events.png)
*AI-powered impact analysis: Iran-USA tensions affecting 6 portfolio holdings (RELIANCE, ONGC, TATAPOWER, JSWENERGY, SPICEJET, HAL)*

### 7. Trading Signals
![Trading Signals](screenshots/trading-signals.png)
*AI-generated entry/target/stop-loss recommendations with risk-reward ratios and confidence scores*
