# database_models_render.py - PostgreSQL Database Models for Render
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

class Database:
    def __init__(self, database_url=None):
        """Initialize PostgreSQL database connection"""
        if database_url:
            self.database_url = database_url
        else:
            self.database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/stalkify')

        self.init_database()

    def get_connection(self):
        """Get PostgreSQL database connection"""
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)

    def init_database(self):
        """Ensure database and tables exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Create tables (PostgreSQL syntax)

            # Companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    sector VARCHAR(100),
                    industry VARCHAR(100),
                    website TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Stock data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    risk_level VARCHAR(20),
                    price FLOAT,
                    open_price FLOAT,
                    high_price FLOAT,
                    low_price FLOAT,
                    high_52week FLOAT,
                    low_52week FLOAT,
                    dividend_yield FLOAT,
                    volume BIGINT,
                    market_cap BIGINT,
                    pe_ratio FLOAT,
                    eps FLOAT,
                    volatility FLOAT,
                    return_30d FLOAT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # AI analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                    score INTEGER,
                    sentiment VARCHAR(50),
                    ai_risk VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Stock price history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    date DATE NOT NULL,
                    open_price FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close_price FLOAT,
                    volume BIGINT,
                    UNIQUE(symbol, date)
                )
            ''')

            # User portfolios table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(100) DEFAULT 'default',
                    name VARCHAR(255) DEFAULT 'My Portfolio',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Portfolio holdings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holdings (
                    id SERIAL PRIMARY KEY,
                    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
                    symbol VARCHAR(20) NOT NULL,
                    shares FLOAT NOT NULL,
                    purchase_price FLOAT,
                    purchase_date DATE
                )
            ''')

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    full_name VARCHAR(255),
                    oauth_provider VARCHAR(50),
                    oauth_id VARCHAR(255),
                    avatar_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

            # Watchlist table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(100) DEFAULT 'default',
                    symbol VARCHAR(20) NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, symbol)
                )
            ''')

            # AI Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    prediction_date DATE NOT NULL,
                    predicted_price FLOAT,
                    confidence FLOAT,
                    ai_signal VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()

        except Exception as err:
            print(f"Database initialization error: {err}")

    # ===== COMPANY OPERATIONS =====

    def add_company(self, symbol, name, sector=None, industry=None, website=None, description=None):
        """Add or update a company"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO companies (symbol, name, sector, industry, website, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    sector = EXCLUDED.sector,
                    industry = EXCLUDED.industry,
                    website = EXCLUDED.website,
                    description = EXCLUDED.description
            ''', (symbol, name, sector, industry, website, description))

            conn.commit()

            # Get the company ID
            cursor.execute('SELECT id FROM companies WHERE symbol = %s', (symbol,))
            result = cursor.fetchone()
            return result['id'] if result else None

        except Exception as e:
            print(f"Error adding company: {e}")
            return None
        finally:
            conn.close()

    def get_all_companies(self):
        """Get all companies"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM companies ORDER BY symbol')
        companies = cursor.fetchall()

        conn.close()
        return companies

    def get_company_by_symbol(self, symbol):
        """Get company by symbol"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM companies WHERE symbol = %s', (symbol,))
        company = cursor.fetchone()

        conn.close()
        return company

    # ===== STOCK DATA OPERATIONS =====

    def update_stock_data(self, company_id, price, open_price, high_price, low_price,
                         high_52week, low_52week, dividend_yield, volume, market_cap, pe_ratio, eps, risk_level=None, volatility=None, return_30d=None):
        """Update stock data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Delete old data for this company
            cursor.execute('DELETE FROM stock_data WHERE company_id = %s', (company_id,))

            # Insert new data
            cursor.execute('''
                INSERT INTO stock_data
                (company_id, risk_level, price, open_price, high_price, low_price, high_52week, low_52week, dividend_yield, volume, market_cap, pe_ratio, eps, volatility, return_30d)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (company_id, risk_level, price, open_price, high_price, low_price, high_52week, low_52week, dividend_yield, volume, market_cap, pe_ratio, eps, volatility, return_30d))

            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating stock data: {e}")
            return False
        finally:
            conn.close()

    def get_stock_data(self, company_id):
        """Get latest stock data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM stock_data WHERE company_id = %s', (company_id,))
        data = cursor.fetchone()

        conn.close()
        return data

    def get_all_stocks_with_data(self):
        """Get all companies with their stock data in ONE query"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT c.*, s.*
            FROM companies c
            LEFT JOIN stock_data s ON c.id = s.company_id
            ORDER BY c.symbol
        ''')

        results = cursor.fetchall()
        conn.close()
        return results

    # ===== PRICE HISTORY OPERATIONS =====

    def add_price_history(self, symbol, date, open_price, high, low, close, volume):
        """Add historical price data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO price_history (symbol, date, open_price, high, low, close_price, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, date) DO UPDATE SET
                    open_price = EXCLUDED.open_price,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close_price = EXCLUDED.close_price,
                    volume = EXCLUDED.volume
            ''', (symbol, date, open_price, high, low, close, volume))

            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding price: {e}")
            return False
        finally:
            conn.close()

    def get_price_history(self, symbol, days=30):
        """Get price history for a stock"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM price_history
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT %s
        ''', (symbol, days))

        prices = cursor.fetchall()

        conn.close()
        return prices

    # ===== AI ANALYSIS OPERATIONS =====

    def add_ai_analysis(self, company_id, score, sentiment, ai_risk):
        """Add AI analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO ai_analysis (company_id, score, sentiment, ai_risk)
            VALUES (%s, %s, %s, %s)
        ''', (company_id, score, sentiment, ai_risk))

        conn.commit()
        conn.close()
        return True

    def get_ai_analysis(self, company_id, limit=10):
        """Get AI analysis for a company"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM ai_analysis
            WHERE company_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        ''', (company_id, limit))

        analysis = cursor.fetchall()

        conn.close()
        return analysis

# Initialize database with Render's DATABASE_URL
db = Database()
