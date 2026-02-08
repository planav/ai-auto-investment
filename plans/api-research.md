# API Research: Market Data & LLM Options

## Market Data APIs

### 1. Finnhub (RECOMMENDED PRIMARY)

**Website**: https://finnhub.io

#### Free Tier Limits
- 60 API calls/minute
- WebSocket access for real-time data
- No daily limits on most endpoints

#### Key Features
- Real-time US stock quotes (WebSocket + REST)
- Historical candlestick data (1min to monthly)
- Company fundamentals (financials, metrics)
- News sentiment analysis
- Economic calendar
- Insider transactions
- Earnings calendar

#### Critical Endpoints

```bash
# Real-time quote
GET https://finnhub.io/api/v1/quote?symbol=AAPL&token={API_KEY}

# Historical candles (1min, 5min, 15min, 30min, 60min, D, W, M)
GET https://finnhub.io/api/v1/stock/candle?symbol=AAPL&resolution=D&from=1572651390&to=1575243390&token={API_KEY}

# Company profile
GET https://finnhub.io/api/v1/stock/profile2?symbol=AAPL&token={API_KEY}

# Financial metrics
GET https://finnhub.io/api/v1/stock/metric?symbol=AAPL&metric=all&token={API_KEY}

# News
GET https://finnhub.io/api/v1/news?category=general&token={API_KEY}
GET https://finnhub.io/api/v1/company-news?symbol=AAPL&from=2024-01-01&to=2024-01-31&token={API_KEY}

# Sentiment
GET https://finnhub.io/api/v1/news-sentiment?symbol=AAPL&token={API_KEY}

# Insider transactions
GET https://finnhub.io/api/v1/stock/insider-transactions?symbol=AAPL&from=2024-01-01&to=2024-01-31&token={API_KEY}

# Earnings surprises
GET https://finnhub.io/api/v1/stock/earnings?symbol=AAPL&token={API_KEY}
```

#### Response Examples

**Quote**:
```json
{
  "c": 261.74,    // Current price
  "d": 2.91,      // Change
  "dp": 1.1249,   // Percent change
  "h": 263.31,    // High of day
  "l": 260.68,    // Low of day
  "o": 261.07,    // Open price
  "pc": 258.83,   // Previous close
  "t": 1582641000 // Timestamp
}
```

**Candles**:
```json
{
  "c": [217.68, 221.03, 219.89],  // Close prices
  "h": [222.49, 221.5, 220.94],   // High prices
  "l": [217.19, 217.1402, 218.83],// Low prices
  "o": [221.03, 218.55, 220.0],   // Open prices
  "s": "ok",                       // Status
  "t": [1569297600, 1569384000, 1569470400], // Timestamps
  "v": [33463820, 24018876, 20730608]        // Volumes
}
```

#### Python Integration
```python
import requests
import websocket
import json

class FinnhubClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_quote(self, symbol):
        url = f"{self.base_url}/quote"
        params = {"symbol": symbol, "token": self.api_key}
        response = requests.get(url, params=params)
        return response.json()
    
    def get_candles(self, symbol, resolution="D", from_ts=None, to_ts=None):
        url = f"{self.base_url}/stock/candle"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts,
            "token": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def get_news_sentiment(self, symbol):
        url = f"{self.base_url}/news-sentiment"
        params = {"symbol": symbol, "token": self.api_key}
        response = requests.get(url, params=params)
        return response.json()
```

---

### 2. Yahoo Finance (via yfinance library)

**Library**: https://github.com/ranaroussi/yfinance

#### Pros
- Completely free
- No API key required
- Comprehensive data (stocks, ETFs, crypto, forex)
- Historical data going back decades
- Dividend and split data

#### Cons
- Unofficial API (may break)
- Rate limited by Yahoo
- Not suitable for high-frequency trading

#### Usage
```python
import yfinance as yf

# Get stock data
ticker = yf.Ticker("AAPL")

# Current info
info = ticker.info

# Historical data
hist = ticker.history(period="1y", interval="1d")

# Dividends
dividends = ticker.dividends

# Splits
splits = ticker.splits

# Multiple symbols
data = yf.download(["AAPL", "MSFT", "GOOGL"], period="1y", group_by='ticker')
```

---

### 3. Alpha Vantage

**Website**: https://www.alphavantage.co

#### Free Tier Limits
- 25 API calls/day
- 5 API calls/minute

#### Features
- Stock time series
- Technical indicators (50+)
- Fundamental data
- Forex and crypto
- Sector performance

#### Note
Very limited free tier - only suitable for low-frequency updates.

---

### 4. Polygon.io

**Website**: https://polygon.io

#### Free Tier
- 5 API calls/minute
- 2 years historical data
- Real-time data for delayed (15min) tier

#### Features
- Stocks, options, forex, crypto
- WebSocket streaming
- Market data APIs

---

## LLM APIs

### 1. Google Gemini 2.0 Flash (RECOMMENDED)

**Website**: https://ai.google.dev

#### Free Tier
- Gemini 2.0 Flash: 1,500 requests/day
- Rate limit: 15 requests/minute
- 1 million tokens/day

#### Pricing (if exceeding free tier)
- Input: $0.075 / 1M tokens
- Output: $0.30 / 1M tokens

#### Features
- Multimodal (text, images, video)
- JSON mode for structured output
- Function calling
- 1M token context window

#### API Key
Get from: https://makersuite.google.com/app/apikey

#### Python Integration
```python
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def analyze_portfolio(self, portfolio_data):
        prompt = f"""
        Analyze this investment portfolio and provide recommendations:
        
        Portfolio: {portfolio_data}
        
        Provide analysis in JSON format with these fields:
        - risk_assessment
        - diversification_score
        - recommendations (array)
        - overall_rating
        """
        
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    
    def explain_prediction(self, symbol, prediction_data):
        prompt = f"""
        Explain this stock prediction in simple terms:
        
        Stock: {symbol}
        Prediction Data: {prediction_data}
        
        Provide a 2-3 sentence explanation suitable for a beginner investor.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
```

---

### 2. OpenRouter

**Website**: https://openrouter.ai

#### Free Models Available
- meta-llama/llama-3.1-8b-instruct:free
- google/gemma-2-9b-it:free
- mistralai/mistral-7b-instruct:free
- nousresearch/hermes-3-llama-3.1-405b:free

#### Features
- Unified API for 100+ models
- Free tier available for select models
- OpenAI-compatible API

#### Python Integration
```python
import requests

class OpenRouterClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
    
    def chat_completion(self, messages, model="meta-llama/llama-3.1-8b-instruct:free"):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        return response.json()
```

---

### 3. Groq

**Website**: https://groq.com

#### Free Tier
- $200/month in credits
- Rate limits apply

#### Features
- Extremely fast inference
- Models: Llama 3.1, Mixtral, Gemma
- OpenAI-compatible API

#### Python Integration
```python
from groq import Groq

class GroqClient:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
    
    def analyze_market(self, market_data):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst."
                },
                {
                    "role": "user",
                    "content": f"Analyze this market data: {market_data}"
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return chat_completion.choices[0].message.content
```

---

### 4. Cohere (Trial)

**Website**: https://cohere.com

#### Free Trial
- 1,000 API calls/month
- No credit card required

#### Features
- Command R model (good for RAG)
- Embed models for semantic search
- Classify endpoints

---

## Recommended Architecture

### Market Data Strategy

**Primary**: Finnhub (60 calls/min free tier)
- Real-time quotes
- News sentiment
- Company fundamentals

**Backup**: Yahoo Finance (yfinance library)
- Historical data
- No rate limits
- Free forever

**Cache Layer**: Redis
- Cache quotes for 60 seconds
- Cache historical data for 1 hour
- Reduce API calls

### LLM Strategy

**Primary**: Gemini 2.0 Flash
- Free tier: 1,500 requests/day
- JSON mode for structured output
- Good for portfolio analysis

**Use Cases**:
1. Portfolio explanation generation
2. Risk assessment summaries
3. Investment recommendation rationales
4. Market sentiment analysis

### Rate Limiting Strategy

```python
# Finnhub: 60 calls/minute
# Implement token bucket or sliding window

import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls=60, window=60):
        self.max_calls = max_calls
        self.window = window
        self.calls = deque()
    
    def can_call(self):
        now = time.time()
        # Remove calls outside window
        while self.calls and self.calls[0] < now - self.window:
            self.calls.popleft()
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def wait_time(self):
        if len(self.calls) < self.max_calls:
            return 0
        return self.calls[0] + self.window - time.time()
```

---

## API Keys Setup Instructions

### Finnhub
1. Go to https://finnhub.io/register
2. Create free account
3. Copy API key from dashboard
4. Add to `.env`: `FINNHUB_API_KEY=your_key`

### Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Add to `.env`: `GEMINI_API_KEY=your_key`

### OpenRouter (optional backup)
1. Go to https://openrouter.ai/keys
2. Create API key
3. Add to `.env`: `OPENROUTER_API_KEY=your_key`

---

## Cost Estimation

### Free Tier Usage

**Finnhub (Free)**:
- 60 calls/minute = 86,400 calls/day max
- Sufficient for real-time quotes of 50 stocks (1 call/min each)

**Gemini 2.0 Flash (Free)**:
- 1,500 requests/day
- 15 requests/minute
- Sufficient for portfolio analysis on demand

### If Exceeding Free Tiers

**Finnhub Paid**:
- Standard: $50/month (unlimited REST)
- Professional: $250/month (WebSocket + more)

**Gemini Paid**:
- Flash: ~$0.50 per 1M tokens
- Pro: ~$3.50 per 1M tokens
- Typical portfolio analysis: ~500 tokens = $0.000375 per request

---

## Implementation Priority

1. **Finnhub** - Essential for real market data
2. **Gemini 2.0 Flash** - Essential for AI explanations
3. **Yahoo Finance** - Backup for historical data
4. **OpenRouter** - Optional backup LLM
