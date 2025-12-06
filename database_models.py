# database_models.py - MySQL Database Models
import mysql.connector
from datetime import datetime
import json

class Database:
    def __init__(self, host='localhost', user='root', password='', database='stalkify'):
        """Initialize MySQL database connection"""
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.init_database()
    
    def get_connection(self):
        """Get MySQL database connection"""
        return mysql.connector.connect(**self.config)
    
    def init_database(self):
        """Ensure database and tables exist"""
        try:
            # Connect without database first
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password']
            )
            cursor = conn.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor.execute(f"USE {self.config['database']}")
            
            # Create tables (matching your existing schema + enhancements)
            
            # Companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    sector VARCHAR(100),
                    industry VARCHAR(100),
                    website TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX(symbol)
                )
            ''')
            
            # Stock data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_id INT,
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
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    INDEX(company_id)
                )
            ''')
            # Ensure risk_level, high_52week and low_52week columns exist for upgrades (best-effort)
            try:
                cursor.execute("SHOW COLUMNS FROM stock_data LIKE 'risk_level'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE stock_data ADD COLUMN risk_level VARCHAR(20)")

                cursor.execute("SHOW COLUMNS FROM stock_data LIKE 'high_52week'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE stock_data ADD COLUMN high_52week FLOAT")

                cursor.execute("SHOW COLUMNS FROM stock_data LIKE 'low_52week'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE stock_data ADD COLUMN low_52week FLOAT")
                cursor.execute("SHOW COLUMNS FROM stock_data LIKE 'dividend_yield'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE stock_data ADD COLUMN dividend_yield FLOAT")

                cursor.execute("SHOW COLUMNS FROM stock_data LIKE 'volatility'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE stock_data ADD COLUMN volatility FLOAT")

                cursor.execute("SHOW COLUMNS FROM stock_data LIKE 'return_30d'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE stock_data ADD COLUMN return_30d FLOAT")
            except Exception:
                # ignore errors (e.g., permissions or older MySQL versions)
                pass
            
            # AI analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_id INT,
                    score INT,
                    sentiment VARCHAR(50),
                    ai_risk VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    INDEX(company_id)
                )
            ''')
            
            # Stock price history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    date DATE NOT NULL,
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume BIGINT,
                    UNIQUE KEY unique_price (symbol, date),
                    INDEX(symbol),
                    INDEX(date)
                )
            ''')
            
            # User portfolios table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(100) DEFAULT 'default',
                    name VARCHAR(255) DEFAULT 'My Portfolio',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX(user_id)
                )
            ''')
            
            # Portfolio holdings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holdings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    portfolio_id INT,
                    symbol VARCHAR(20) NOT NULL,
                    shares FLOAT NOT NULL,
                    purchase_price FLOAT,
                    purchase_date DATE,
                    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
                    INDEX(portfolio_id),
                    INDEX(symbol)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    full_name VARCHAR(255),
                    oauth_provider VARCHAR(50),
                    oauth_id VARCHAR(255),
                    avatar_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    INDEX(username),
                    INDEX(email),
                    INDEX(oauth_provider, oauth_id)
                )
            ''')
            
            try:
                cursor.execute("SHOW COLUMNS FROM users LIKE 'oauth_provider'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)")
                cursor.execute("SHOW COLUMNS FROM users LIKE 'oauth_id'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255)")
                cursor.execute("SHOW COLUMNS FROM users LIKE 'avatar_url'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
                cursor.execute("SHOW COLUMNS FROM users LIKE 'last_login'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL")
                cursor.execute("SHOW COLUMNS FROM users LIKE 'is_active'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
            except Exception:
                pass
            
            # Watchlist table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(100) DEFAULT 'default',
                    symbol VARCHAR(20) NOT NULL,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_watch (user_id, symbol),
                    INDEX(user_id),
                    INDEX(symbol)
                )
            ''')
            
            # AI Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    symbol VARCHAR(20) NOT NULL,
                    prediction_date DATE NOT NULL,
                    predicted_price FLOAT,
                    confidence FLOAT,
                    ai_signal VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX(symbol),
                    INDEX(prediction_date)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as err:
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
                ON DUPLICATE KEY UPDATE 
                    name=%s, sector=%s, industry=%s, website=%s, description=%s
            ''', (symbol, name, sector, industry, website, description,
                  name, sector, industry, website, description))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding company: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_companies(self):
        """Get all companies"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM companies ORDER BY symbol')
        companies = cursor.fetchall()
        
        conn.close()
        return companies
    
    def get_company_by_symbol(self, symbol):
        """Get company by symbol"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
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

            # Insert new data (including volatility and return_30d)
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
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM stock_data WHERE company_id = %s', (company_id,))
        data = cursor.fetchone()
        
        conn.close()
        return data
    
    def get_all_stocks_with_data(self):
        """Get all companies with their stock data in ONE query (optimized)"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
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
                INSERT INTO price_history (symbol, date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    open=%s, high=%s, low=%s, close=%s, volume=%s
            ''', (symbol, date, open_price, high, low, close, volume,
                  open_price, high, low, close, volume))
            
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
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM price_history 
            WHERE symbol = %s 
            ORDER BY date DESC 
            LIMIT %s
        ''', (symbol, days))
        
        prices = cursor.fetchall()
        
        conn.close()
        return prices
    
    # ===== PORTFOLIO OPERATIONS =====
    
    def create_portfolio(self, user_id='default', name='My Portfolio'):
        """Create a new portfolio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO portfolios (user_id, name)
            VALUES (%s, %s)
        ''', (user_id, name))
        
        portfolio_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return portfolio_id
    
    def add_holding(self, portfolio_id, symbol, shares, purchase_price=None, purchase_date=None):
        """Add a stock holding to portfolio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if purchase_date is None:
            purchase_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO holdings (portfolio_id, symbol, shares, purchase_price, purchase_date)
            VALUES (%s, %s, %s, %s, %s)
        ''', (portfolio_id, symbol, shares, purchase_price, purchase_date))
        
        conn.commit()
        conn.close()
        return True
    
    def get_portfolio_holdings(self, portfolio_id):
        """Get all holdings in a portfolio"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT h.*, c.name, c.sector 
            FROM holdings h
            LEFT JOIN companies c ON h.symbol = c.symbol
            WHERE h.portfolio_id = %s
        ''', (portfolio_id,))
        
        holdings = cursor.fetchall()
        
        conn.close()
        return holdings
    
    # ===== WATCHLIST OPERATIONS =====
    
    def add_to_watchlist(self, symbol, user_id='default'):
        """Add stock to watchlist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO watchlist (user_id, symbol)
                VALUES (%s, %s)
            ''', (user_id, symbol))
            
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def get_watchlist(self, user_id='default'):
        """Get user's watchlist"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT w.*, c.name, c.sector 
            FROM watchlist w
            LEFT JOIN companies c ON w.symbol = c.symbol
            WHERE w.user_id = %s
            ORDER BY w.added_date DESC
        ''', (user_id,))
        
        watchlist = cursor.fetchall()
        
        conn.close()
        return watchlist
    
    def remove_from_watchlist(self, symbol, user_id='default'):
        """Remove stock from watchlist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM watchlist 
            WHERE user_id = %s AND symbol = %s
        ''', (user_id, symbol))
        
        conn.commit()
        conn.close()
        return True
    
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
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM ai_analysis 
            WHERE company_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        ''', (company_id, limit))
        
        analysis = cursor.fetchall()
        
        conn.close()
        return analysis
    
    # ===== USER OPERATIONS =====
    
    def create_user(self, username, email, password_hash=None, full_name=None, oauth_provider=None, oauth_id=None, avatar_url=None):
        """Create a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, oauth_provider, oauth_id, avatar_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (username, email, password_hash, full_name, oauth_provider, oauth_id, avatar_url))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except mysql.connector.IntegrityError:
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_by_oauth(self, oauth_provider, oauth_id):
        """Get user by OAuth provider and ID"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE oauth_provider = %s AND oauth_id = %s', (oauth_provider, oauth_id))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def get_user_by_email(self, email):
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def update_last_login(self, user_id):
        """Update user's last login time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET last_login = NOW() 
            WHERE id = %s
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    
    # ===== PREDICTION OPERATIONS =====
    
    def add_prediction(self, symbol, prediction_date, predicted_price, confidence, ai_signal):
        """Add AI prediction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions (symbol, prediction_date, predicted_price, confidence, ai_signal)
            VALUES (%s, %s, %s, %s, %s)
        ''', (symbol, prediction_date, predicted_price, confidence, ai_signal))
        
        conn.commit()
        conn.close()
        return True
    
    def get_predictions(self, symbol, limit=10):
        """Get AI predictions for a stock"""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE symbol = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        ''', (symbol, limit))
        
        predictions = cursor.fetchall()
        
        conn.close()
        return predictions


# Initialize database with your MySQL credentials
# CHANGE THESE TO YOUR MYSQL SETTINGS:
db = Database(
    host='localhost',
    user='root',
    password='',  # Add your MySQL password here
    database='stalkify'
)
