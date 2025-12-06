# 📊 Stalkify - AI-Powered Stock Market Analysis Platform

![Stalkify](https://img.shields.io/badge/AI-Powered-00ffff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?style=for-the-badge)

**Stalkify** is an advanced AI-powered stock market analysis and prediction platform developed by **Vignesh Mamindla** at the **Government Institute of Electronics (GIOE), Secunderabad**.

## ✨ Features

### 🎯 Core Features
- **Real-Time Stock Data** - Track 100+ stocks across multiple sectors
- **AI Predictions** - Machine learning-powered price forecasting
- **What-If Simulator** - Test different market scenarios
- **Interactive Charts** - Beautiful data visualizations with Chart.js
- **Portfolio Management** - Track and manage your investments
- **Watchlist** - Monitor your favorite stocks
- **Company Details** - Comprehensive company information and history
- **Financial News** - Stay updated with latest market news

### 🤖 AI Capabilities
- Price prediction using trend analysis
- Risk assessment and volatility analysis
- Market scenario simulation (Crash, Bull Market, Recession, etc.)
- AI-powered buy/hold/sell signals
- Sentiment analysis

### 💼 User Features
- User authentication (Login/Register)
- Secure password hashing
- Session management
- Personal portfolios
- Custom watchlists

## 🚀 Tech Stack

- **Backend:** Python Flask
- **Database:** MySQL
- **AI/ML:** NumPy, yfinance
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Chart.js
- **Icons:** Font Awesome
- **APIs:** Yahoo Finance API

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/vignesh90639/Stalkify.git
cd Stalkify
```

### 2. Install Dependencies
```bash
pip install flask yfinance numpy mysql-connector-python werkzeug
```

### 3. Configure MySQL Database

Update MySQL credentials in `database_models.py`:
```python
db = Database(
    host='localhost',
    user='root',
    password='your_password',
    database='stalkify'
)
```

### 4. Initialize Database
```bash
python init_database.py
```

This will:
- Create all necessary tables
- Populate 100+ stocks
- Create demo portfolio
- Add sample watchlist

### 5. Run the Application
```bash
python app.py
```

Visit: **http://127.0.0.1:5000**

## 📱 Pages & Routes

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/login` | User login |
| `/register` | User registration |
| `/dashboard` | Main analytics dashboard |
| `/simulator` | What-If scenario simulator |
| `/company/<symbol>` | Company details page |
| `/terms` | Terms and Conditions |
| `/privacy` | Privacy Policy |

## 🎨 Features Overview

### Dashboard
- Real-time stock prices
- Portfolio performance chart (30 days)
- AI insights and predictions
- Latest financial news
- Search and filter stocks
- Quick stats overview

### What-If Simulator
- AI price predictor (up to 90 days)
- Market scenario simulation
- Multiple scenario comparison
- Portfolio impact analysis
- Custom scenario creation

### Company Details
- Full company information
- 1-year price history chart
- Key financial metrics
- Historical data table
- Sector and industry info

## 🗄️ Database Schema

### Tables
- `users` - User accounts
- `companies` - Company information
- `stock_data` - Current stock data
- `price_history` - Historical prices
- `portfolios` - User portfolios
- `holdings` - Portfolio holdings
- `watchlist` - User watchlists
- `ai_analysis` - AI analysis results
- `predictions` - AI predictions

## 🔒 Security

- Passwords hashed with Werkzeug
- Session-based authentication
- SQL injection protection
- Input validation
- Secure database connections

## 📊 Supported Stock Categories

- Tech Giants (AAPL, MSFT, GOOGL, etc.)
- Finance (JPM, BAC, GS, etc.)
- Healthcare (JNJ, PFE, UNH, etc.)
- Consumer & Retail (WMT, HD, NKE, etc.)
- Energy (XOM, CVX, COP, etc.)
- Semiconductors (NVDA, AMD, INTC, etc.)
- And many more...

## 👨‍💻 Developer

**Vignesh Mamindla**
- GitHub: [@vignesh90639](https://github.com/vignesh90639)
- LinkedIn: [Vignesh Mamindla](https://www.linkedin.com/in/vignesh-mamindla-881b34383/)
- Email: vigneshgotjob@gmail.com
- Institution: Government Institute of Electronics, Secunderabad

## 📄 License

This project is developed for educational purposes.

## 🙏 Acknowledgments

- **GIOE** (Government Institute of Electronics) - Supporting Institution
- **Yahoo Finance** - Stock market data API
- **Chart.js** - Beautiful data visualizations
- **Flask** - Web framework

## ⚠️ Disclaimer

This platform is for **educational and informational purposes only**. It is not intended as financial advice. Always consult with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.

## 📞 Support

For issues or questions:
- Email: vigneshgotjob@gmail.com
- Phone: +91 8331097721

---

**Made with ❤️ by Vignesh Mamindla | © 2025 Stalkify**
