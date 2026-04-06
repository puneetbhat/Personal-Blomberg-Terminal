## About This Project
Personal Bloomberg Terminal is a comprehensive financial analytics platform built to replicate professional Bloomberg Terminal functionality for personal portfolio management. It combines real-time market data, AI-powered insights, and multi-broker integration to provide institutional-grade portfolio tracking and analysis tools accessible through a web-based dashboard.
The system tracks 59 total holdings across Indian equities, mutual funds, and US stocks, with automatic updates every 30 seconds, delivering live price feeds, sentiment-analyzed news, geopolitical event impact assessments, and performance analytics—all built from scratch using Python Flask backend and vanilla JavaScript frontend.
 
---

##  Key Features

###  Real-Time Market Data

###  Advanced Analytics

###  Intelligent News Feed

###  AI-Powered Insights

###  Multi-Broker Integration

###  Global Markets

---

##  Tech Stack

**Backend:** Flask, yfinance, pandas, feedparser, anthropic (Claude AI)  
**Frontend:** Vanilla JavaScript (ES6+), Chart.js, Lightweight Charts  
**Database:** Firebase Firestore, LocalStorage  
**Security:** SHA-256 hashing, Cloud sync

---

##  Screenshots

### 1. Main Dashboard
<img width="1919" height="1079" alt="Image" src="https://github.com/user-attachments/assets/754548a0-277b-4799-a088-25205917b702" />
Complete portfolio overview with real-time updates every 30 seconds. Features live market indices (Nifty 50, Bank Nifty, Sensex, S&P 500, VIX), portfolio allocation across 4 brokers, top gainers/losers, sector-wise P&L breakdown, live news feed, and floating panels for commodities (Gold, Silver, Crude Oil, Natural Gas, Copper), cryptocurrencies (Bitcoin, Ethereum, Solana, BNB, XRP, Cardano), and forex exchange rates (USD/INR, EUR/INR, GBP/INR). Bottom ticker displays real-time prices from major global markets including NYSE, NASDAQ, and other international exchanges.

### 2. Portfolio vs Benchmark
<img width="1130" height="845" alt="Image" src="https://github.com/user-attachments/assets/f3b46f2c-0ab3-4772-a0a0-df12ec1f5add" />
Performance comparison across all timeframes (1D, 1W, 1M, 3M, 6M, 1Y, YTD) and broker breakdowns. View returns for individual brokers (Angel One, Zerodha Kite, Groww MF, US holdings) or combined portfolio against benchmark indices. Chart shows relative performance with alpha calculation, helping identify outperformance or underperformance. Switch between brokers using filter buttons to analyze strategy effectiveness for each trading account independently.

### 3. Portfolio Heatmap
<img width="1128" height="853" alt="Image" src="https://github.com/user-attachments/assets/8e3661c6-206c-40af-abb7-2937aa8022b2" />
Live-updated visual performance tracker connected to Yahoo Finance API. All 38 stocks update every 30 seconds with real-time price changes color-coded by daily returns - green tiles for gains, red for losses, with intensity indicating magnitude of movement. Quickly identify top performers and underperformers at a glance. Click any stock tile to view detailed candlestick charts with historical data. Heatmap automatically adjusts as market conditions change throughout trading hours.

### 4. Sector Analysis
<img width="1124" height="842" alt="Image" src="https://github.com/user-attachments/assets/132af5da-8522-431f-a5ff-00b99216654a" />
Interactive sector-wise portfolio allocation showing exposure across 12 Indian market sectors. Each sector displays percentage change, number of owned stocks, and major holdings within that sector. Helps maintain balanced diversification and identify concentration risks. Click any sector to filter portfolio view and see detailed breakdown of holdings, invested amount, and current value within that sector. Progress bars visualize relative allocation, making it easy to spot overweight or underweight positions compared to market indices

### 5. News Feed with Sentiment
<img width="1127" height="810" alt="Image" src="https://github.com/user-attachments/assets/726e1a49-689c-41e0-a22a-99ec5cfecad3" />
Live news aggregation updating every 30 seconds from 5 major financial sources. Automatically filters and displays only news relevant to your portfolio holdings - when you add a new stock, related news appears immediately, helping with real-time investment decisions. Each article is tagged with AI-powered sentiment analysis (Bull/Bear/Neutral) and stock symbols are highlighted. Click any news item to open the full article in a new tab for detailed reading. Portfolio-aware filtering ensures you never miss important updates about your holdings.

### 6. Geopolitical Events
<img width="417" height="849" alt="Image" src="https://github.com/user-attachments/assets/91271252-9041-45ae-bbee-0aa8627d5ed2" />

AI-powered geopolitical event tracker with portfolio impact analysis, updating every 30 seconds. Major global events (wars, trade disputes, policy changes, economic crises) are analyzed for their impact on your specific holdings. Each event shows severity level (High/Medium/Low), affected portfolio stocks, and percentage impact on your returns. Click any event to open external links for verification and detailed coverage. Helps understand macro factors driving portfolio performance and make informed decisions during volatile market conditions.

### 7. Trading Signals
<img width="417" height="847" alt="Image" src="https://github.com/user-attachments/assets/82cb7c6c-b260-49f5-8f24-8411bd1bab6f" />

Terminal-style trading recommendations connected to external research providers. Each signal displays entry price, target price, stop-loss levels, risk-reward ratio (R:R), and confidence percentage. Shows holding position (HOLD/BUY/SELL), research source, and current progress toward targets. Click any signal to open the external broker's research page for full analysis verification. Signals update as market conditions change, helping identify optimal entry and exit points based on technical and fundamental analysis from professional sources.














