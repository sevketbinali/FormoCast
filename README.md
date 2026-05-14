# FormoCast 🚀

FormoCast is an automated financial analysis service that detects technical analysis patterns in stock and crypto charts, predicts price movements, and notifies you via email with professional-grade visual reports.

## ✨ Key Features
- **Automated Detection:** Identifies Double Top, Double Bottom, and more.
- **Premium Reports:** Dark-mode charts sent directly to your inbox.
- **Performance Analytics:** Tracks prediction accuracy over time.
- **Docker Ready:** Deploy anywhere with a single command.

## 🛠 Tech Stack
- **Python 3.10+** (Pandas, Scipy, Matplotlib)
- **yfinance** (Market Data)
- **SQLite** (Persistence)
- **Docker & Docker Compose**

## 🚀 Getting Started

### 1. Prerequisites
- Docker & Docker Compose installed.
- An SMTP server (e.g., Gmail App Password).

### 2. Configuration
Copy `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```

### 3. Usage
Run the pattern scanner:
```bash
docker-compose run app python main.py --scan --tickers AAPL TSLA BTC-USD
```

Run the accuracy analyzer:
```bash
docker-compose run app python main.py --analyze
```

## 📂 Project Structure
- `core/`: Detection and prediction logic.
- `services/`: External integrations (Data, Visuals, Email).
- `db/`: Database models and persistence.
- `docs/`: (See `requirements.md`, `design.md`, `tasks.md` for details).

## 📄 Documentation
For detailed insights into the architecture and requirements, please refer to:
- [Requirements](requirements.md)
- [Design Document](design.md)
- [Task Roadmap](tasks.md)
