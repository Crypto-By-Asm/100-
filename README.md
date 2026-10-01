# Crypto Bot by ASM Traders

Professional AI-integrated crypto analytics, selective signals, demo trading and SEO blog platform.

**Separate project from ASM VEO.**

## Features (v1.0)

- Live Binance market data + candlestick charts (TradingView Lightweight Charts)
- Multi-indicator engine: RSI, MACD, EMA20/50/200, ADX, ATR, Volume
- Selective **LONG / SHORT / WAIT** signal scoring
- Dynamic validity window (6–20 minutes)
- Entry + Stop Loss + TP1 / TP2 / TP3 + Risk/Reward
- Gemini AI signal explanations (server-side key only)
- 30-topic SEO blog structure + AI article generation
- Full Auth (Register / Login / JWT)
- Subscription plans (Free / Pro / Elite)
- Demo / Paper trading with virtual balance, open/close, P&L tracking
- Responsive premium UI

## Important Philosophy

- **No hard-coded 98%/99% accuracy claims.**
- Model score is a relative strength score, **not** a guaranteed win probability.
- Real performance will come from future backtesting + live/demo statistics.

## Quick Start

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional but recommended)

uvicorn app:app --reload
```

Open: http://127.0.0.1:8000

## Environment Variables

See `.env.example`

- `GEMINI_API_KEY` — required for AI explanations & blog generation
- `SECRET_KEY` — change in production
- `DATABASE_URL` — default SQLite

## Project Structure

```
app.py                 # FastAPI entry
config/                # Settings + Database
models/                # SQLAlchemy models (User, Blog, Demo)
auth/                  # JWT + password security
api/                   # Routers (auth, market, signals, blog, demo)
strategy/              # Indicators + Signal engine + Risk + Duration
services/              # Gemini + Blog generator + Demo trading logic
data/                  # Market data (Binance)
templates/             # Frontend HTML
static/                # CSS + JS
```

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/register` | Create account |
| `POST /api/auth/login` | Login → JWT |
| `GET  /api/auth/me` | Current user |
| `GET  /api/auth/plans` | Subscription plans |
| `GET  /api/market/klines` | OHLCV data |
| `GET  /api/signals/current` | Current signal (+ optional AI explain) |
| `GET  /api/blog/posts` | Published articles |
| `POST /api/blog/generate` | Generate AI articles (auth) |
| `GET  /api/demo/account` | Demo balance & stats |
| `POST /api/demo/trades` | Open paper trade |
| `POST /api/demo/trades/{id}/close` | Close paper trade |

## Next Roadmap Ideas

- Full backtesting engine + performance dashboard
- Real-time WebSocket candles
- Multi-symbol watchlist
- Payment integration for Pro/Elite
- Advanced order types in demo
- Sitemap + Schema markup for blog SEO

---

Built for ASM Traders · 2026
