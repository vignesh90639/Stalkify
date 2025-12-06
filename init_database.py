# init_database.py - Initialize MySQL database with stock data
from database_models import db
from app import STOCK_SYMBOLS
import yfinance as yf
from datetime import datetime

def populate_companies():
    """Populate database with company information"""
    print(f"\nPopulating database with {len(STOCK_SYMBOLS)} companies...")
    
    success_count = 0
    fail_count = 0
    
    for i, symbol in enumerate(STOCK_SYMBOLS, 1):
        try:
            print(f"[{i}/{len(STOCK_SYMBOLS)}] Fetching {symbol}...", end=" ")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Add company to database
            db.add_company(
                symbol=symbol,
                name=info.get('longName') or symbol,
                sector=info.get('sector'),
                industry=info.get('industry'),
                website=info.get('website'),
                description=info.get('longBusinessSummary', '')[:500] if info.get('longBusinessSummary') else ''
            )
            
            # Add recent price history (1 month)
            hist = ticker.history(period="30d")
            
            if not hist.empty:
                for date, row in hist.iterrows():
                    db.add_price_history(
                        symbol=symbol,
                        date=date.strftime("%Y-%m-%d"),
                        open_price=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=int(row['Volume'])
                    )
            
            print("✓")
            success_count += 1
            
        except Exception as e:
            print(f"✗ Error: {e}")
            fail_count += 1
            continue
    
    print(f"\n✅ Successfully added: {success_count}")
    print(f"❌ Failed: {fail_count}")

def create_default_portfolio():
    """Create a default demo portfolio"""
    print("\nCreating default portfolio...")
    
    portfolio_id = db.create_portfolio(user_id='default', name='Demo Portfolio')
    
    # Add some sample holdings
    sample_holdings = [
        ('AAPL', 10, 150.00),
        ('MSFT', 5, 300.00),
        ('GOOGL', 3, 120.00),
        ('TSLA', 2, 200.00),
        ('NVDA', 4, 400.00),
        ('AMZN', 2, 180.00),
        ('META', 5, 350.00)
    ]
    
    for symbol, shares, price in sample_holdings:
        db.add_holding(portfolio_id, symbol, shares, price)
    
    print(f"✅ Default portfolio created with ID: {portfolio_id}")
    print(f"   Added {len(sample_holdings)} sample holdings")

def add_sample_watchlist():
    """Add sample stocks to watchlist"""
    print("\nAdding sample watchlist...")
    
    watchlist_stocks = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'GOOGL', 'MSFT', 'AMZN', 'META']
    
    for symbol in watchlist_stocks:
        db.add_to_watchlist(symbol)
    
    print(f"✅ Added {len(watchlist_stocks)} stocks to watchlist")

def display_stats():
    """Display database statistics"""
    try:
        companies = db.get_all_companies()
        watchlist = db.get_watchlist()
        
        print("\n" + "=" * 60)
        print("DATABASE STATISTICS")
        print("=" * 60)
        print(f"📊 Total Companies: {len(companies)}")
        print(f"⭐ Watchlist Items: {len(watchlist)}")
        print(f"💼 Database: MySQL (stalkify)")
        print("=" * 60)
    except Exception as e:
        print(f"Error getting stats: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("STALKIFY DATABASE INITIALIZATION")
    print("=" * 60)
    print(f"\n📌 This will populate MySQL database with {len(STOCK_SYMBOLS)} stocks")
    print("⚠️  Make sure MySQL is running!")
    print("\nNote: This may take 5-10 minutes depending on your connection")
    
    choice = input("\nContinue? (y/n): ")
    
    if choice.lower() == 'y':
        populate_companies()
        create_default_portfolio()
        add_sample_watchlist()
        display_stats()
        
        print("\n✅ DATABASE READY!")
        print("\nYou can now run: python app.py")
    else:
        print("❌ Cancelled.")
