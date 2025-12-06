import os
from database_models import db
import yfinance as yf

def add_company(symbol):
    """Add company to database using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        name = info.get("longName", symbol)
        sector = info.get("sector", "Unknown")
        industry = info.get("industry", "Unknown")
        website = info.get("website", "")
        description = info.get("longBusinessSummary", "")

        db.add_company(
            symbol=symbol,
            name=name,
            sector=sector,
            industry=industry,
            website=website,
            description=description[:500] if description else ""
        )
    except Exception as e:
        print(f"Error adding company {symbol}: {e}")

def store_stock_data(symbol):
    """Store current stock data for a symbol"""
    try:
        db_company = db.get_company_by_symbol(symbol)
        if not db_company:
            return False
        company_id = db_company['id']

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            latest = hist.iloc[-1]
            db.update_stock_data(
                company_id=company_id,
                price=float(latest['Close']),
                open_price=float(latest['Open']),
                high_price=float(latest['High']),
                low_price=float(latest['Low']),
                volume=int(latest['Volume']),
                market_cap=ticker.info.get('marketCap'),
                pe_ratio=ticker.info.get('trailingPE'),
                eps=ticker.info.get('trailingEps')
            )
            return True
        return False
    except Exception as e:
        print(f"Error storing stock data for {symbol}: {e}")
        return False

def save_ai_analysis(symbol, score, sentiment, ai_risk):
    """Save AI analysis for a symbol"""
    try:
        db_company = db.get_company_by_symbol(symbol)
        if not db_company:
            return False
        company_id = db_company['id']

        db.add_ai_analysis(company_id=company_id, score=score, sentiment=sentiment, ai_risk=ai_risk)
        return True
    except Exception as e:
        print(f"Error saving AI analysis for {symbol}: {e}")
        return False

def get_companies():
    """Get all companies from database"""
    return db.get_all_companies()

def get_ai_analysis(symbol):
    """Get AI analysis for a symbol"""
    try:
        db_company = db.get_company_by_symbol(symbol)
        if not db_company:
            return None
        company_id = db_company['id']
        return db.get_ai_analysis(company_id)
    except Exception as e:
        print(f"Error getting AI analysis for {symbol}: {e}")
        return None
