# app.py
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import yfinance as yf
from random import randint, choice
import statistics
from ai_model import predict_stock_price, simulate_what_if, run_ai_analysis
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time as _time
from math import ceil
from database_models import db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = 'stalkify_secret_key_change_in_production_2025'  # Change this in production!

from stock_symbols_220 import STOCK_SYMBOLS

# -------------------------
# LOGIN DECORATOR
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
# HOME ROUTE
# -------------------------
@app.route('/')
def home():
    return render_template('home.html')

# -------------------------
# LOGIN ROUTE
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            
            db.update_last_login(user['id'])
            
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

# -------------------------
# REGISTER ROUTE
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        # Validation
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        # Check if user exists
        if db.get_user_by_username(username):
            return render_template('register.html', error='Username already exists')
        
        if db.get_user_by_email(email):
            return render_template('register.html', error='Email already registered')
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = db.create_user(username, email, password_hash, full_name)
        
        if user_id:
            # Create default portfolio for user
            db.create_portfolio(user_id=str(user_id), name=f"{username}'s Portfolio")
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error='Registration failed. Please try again.')
    
    return render_template('register.html')

# -------------------------
# LOGOUT ROUTE
# -------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

# -------------------------
# DASHBOARD ROUTE
# -------------------------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# -------------------------
# WHAT-IF SIMULATOR ROUTE
# -------------------------
@app.route('/simulator')
def simulator():
    return render_template('simulator.html')

# -------------------------
# CONTACT ROUTE
# -------------------------
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    message = request.form.get('message', '')
    
    # Here you can add email sending logic or save to database
    print(f"Contact form submitted - Name: {name}, Email: {email}, Message: {message}")
    
    return render_template('contact.html', name=name)

# -------------------------
# TERMS AND CONDITIONS ROUTE
# -------------------------
@app.route('/terms')
def terms():
    return render_template('terms.html')

# -------------------------
# PRIVACY POLICY ROUTE
# -------------------------
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# -------------------------
# COMPANY DETAILS ROUTE
# -------------------------
@app.route('/company/<symbol>')
def company_details(symbol):
    return render_template('company.html', symbol=symbol.upper())

def fetch_single_stock(symbol):
    """Fetch a single ticker, compute metrics and persist to DB. Returns a dict or None."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="30d")
        
        if hist is None or hist.empty:
            return None

        current_price = float(hist['Close'].iloc[-1])
        if len(hist) > 1:
            prev_close = float(hist['Close'].iloc[-2])
            change_percent = ((current_price - prev_close) / prev_close) * 100
        else:
            change_percent = 0

        try:
            info = ticker.info or {}
        except Exception:
            info = {}

        name = info.get("shortName") or info.get("longName") or symbol
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        dividend_yield = info.get("dividendYield")
        high_52week = info.get("fiftyTwoWeekHigh")
        low_52week = info.get("fiftyTwoWeekLow")
        eps = info.get("trailingEps")
        sector = info.get("sector")
        industry = info.get("industry")
        website = info.get("website")
        description = info.get("longBusinessSummary", "")

        try:
            closes = hist['Close'].dropna().astype(float)
            if len(closes) >= 2:
                first = closes.iloc[0]
                last = closes.iloc[-1]
                return_30d = ((last - first) / first) * 100 if first != 0 else 0
                daily_rets = closes.pct_change().dropna()
                volatility = float(daily_rets.std() * 100) if not daily_rets.empty else 0
            else:
                return_30d = 0
                volatility = 0
        except Exception:
            return_30d = 0
            volatility = 0

        try:
            pe_penalty = 0.0
            if pe_ratio:
                if pe_ratio > 50:
                    pe_penalty = 2.0
                elif pe_ratio > 25:
                    pe_penalty = 1.0

            mc_mod = 0.0
            if market_cap:
                if market_cap >= 50_000_000_000:
                    mc_mod = -1.0
                elif market_cap >= 10_000_000_000:
                    mc_mod = -0.5
        except Exception:
            pe_penalty = 0.0
            mc_mod = 0.0

        risk_score = (volatility * 0.6) + (max(0, -return_30d) * 0.3) + pe_penalty + mc_mod
        if risk_score >= 8:
            risk_level = 'Bold'
        elif risk_score >= 3:
            risk_level = 'Moderate'
        else:
            risk_level = 'Safe'

        try:
            db.add_company(
                symbol=symbol,
                name=name,
                sector=sector,
                industry=industry,
                website=website,
                description=description[:500] if description else None
            )
            company = db.get_company_by_symbol(symbol)
            if company:
                db.update_stock_data(
                    company_id=company['id'],
                    price=current_price,
                    open_price=float(hist['Open'].iloc[-1]) if 'Open' in hist else None,
                    high_price=float(hist['High'].iloc[-1]) if 'High' in hist else None,
                    low_price=float(hist['Low'].iloc[-1]) if 'Low' in hist else None,
                    high_52week=high_52week,
                    low_52week=low_52week,
                    dividend_yield=dividend_yield,
                    volume=int(hist['Volume'].iloc[-1]) if 'Volume' in hist else None,
                    market_cap=market_cap,
                    pe_ratio=pe_ratio,
                    eps=eps,
                    risk_level=risk_level,
                    volatility=volatility,
                    return_30d=return_30d
                )
        except Exception as e:
            print(f"Info error for {symbol}: {e}")

        return {
            "name": name,
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "change_percent": round(change_percent, 2),
            "risk_level": risk_level,
            "market_cap": market_cap,
            "pe_ratio": pe_ratio,
            "dividend_yield": dividend_yield,
            "high_52week": high_52week,
            "low_52week": low_52week,
            "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist else None,
            "ai_signal": choice(["BUY", "HOLD", "SELL"]),
            "confidence": f"{randint(50,100)}%",
            "volatility": volatility,
            "return_30d": return_30d
        }
    except Exception as e:
        msg = str(e)
        if "Rate limited" in msg or "Too Many Requests" in msg:
            print(f"Rate limited: {symbol} - skipping")
        else:
            print(f"Error fetching {symbol}: {e}")
        return None

# -------------------------
# API: Get Real Stock Data (Optimized with Threading)
# -------------------------
@app.route('/api/get_stocks')
def get_stocks():
    # Fetch all companies with stock data in ONE optimized query
    stocks = []
    
    # Get AI signals for all stocks
    try:
        companies = db.get_all_companies()
        symbols = [c['symbol'] for c in companies]
        ai_results = run_ai_analysis(symbols)
        ai_map = {r['symbol']: r for r in ai_results}
    except Exception as e:
        print(f"AI analysis error in get_stocks: {e}")
        ai_map = {}
    
    rows = db.get_all_stocks_with_data()
    
    for row in rows:
        symbol = row['symbol']
        ai_data = ai_map.get(symbol, {})
        
        # Compute change percent relative to open price if available
        change_pct = 0
        if row.get('open_price') and row.get('price') is not None:
            change_pct = ((row['price'] - row['open_price']) / row['open_price']) * 100 if row['open_price'] != 0 else 0
        
        stocks.append({
            'name': row['name'] or row['symbol'],
            'symbol': symbol,
            'current_price': round(row['price'], 2) if row.get('price') is not None else None,
            'change_percent': round(change_pct, 2),
            'risk_level': row.get('risk_level') or 'Moderate',
            'market_cap': row.get('market_cap'),
            'pe_ratio': row.get('pe_ratio'),
            'dividend_yield': row.get('dividend_yield'),
            'high_52week': row.get('high_52week'),
            'low_52week': row.get('low_52week'),
            'volume': row.get('volume'),
            'ai_signal': ai_data.get('ai_signal', 'HOLD'),
            'confidence': ai_data.get('confidence', '50%')
        })

    return jsonify(stocks)

# -------------------------
# API: Get Company Details
# -------------------------
@app.route('/api/company/<symbol>')
def get_company_details(symbol):
    """Get detailed company information from database"""
    try:
        symbol = symbol.upper()
        company = db.get_company_by_symbol(symbol)
        
        if not company:
            return jsonify({'error': f'Company {symbol} not found'}), 404
        
        # Get stock data
        stock_data = db.get_stock_data(company['id'])
        
        # Get price history
        history = db.get_price_history(symbol, days=365)
        
        # Format history for chart
        formatted_history = []
        for h in reversed(history):  # Oldest first
            formatted_history.append({
                'date': h['date'].isoformat() if hasattr(h['date'], 'isoformat') else str(h['date']),
                'open': float(h['open']) if h['open'] else 0,
                'high': float(h['high']) if h['high'] else 0,
                'low': float(h['low']) if h['low'] else 0,
                'close': float(h['close']) if h['close'] else 0,
                'volume': int(h['volume']) if h['volume'] else 0
            })
        
        # Calculate previous close
        previous_close = 0
        if len(formatted_history) > 1:
            previous_close = formatted_history[-2]['close']
        
        response = {
            'symbol': company['symbol'],
            'name': company['name'],
            'sector': company['sector'],
            'industry': company['industry'],
            'website': company['website'],
            'description': company['description'],
            'current_price': float(stock_data['price']) if stock_data and stock_data['price'] else 0,
            'previous_close': previous_close,
            'open': float(stock_data['open_price']) if stock_data and stock_data['open_price'] else None,
            'day_high': float(stock_data['high_price']) if stock_data and stock_data['high_price'] else None,
            'day_low': float(stock_data['low_price']) if stock_data and stock_data['low_price'] else None,
            'volume': int(stock_data['volume']) if stock_data and stock_data['volume'] else 0,
            'market_cap': stock_data['market_cap'] if stock_data else None,
            'pe_ratio': float(stock_data['pe_ratio']) if stock_data and stock_data['pe_ratio'] else None,
            '52week_high': float(stock_data['high_52week']) if stock_data and stock_data['high_52week'] else None,
            '52week_low': float(stock_data['low_52week']) if stock_data and stock_data['low_52week'] else None,
            'dividend_yield': float(stock_data['dividend_yield']) if stock_data and stock_data['dividend_yield'] else None,
            'eps': float(stock_data['eps']) if stock_data and stock_data['eps'] else None,
            'history': formatted_history,
            'employees': None,
            'beta': None,
            'avg_volume': int(stock_data['volume']) if stock_data and stock_data['volume'] else 0
        }
        
        return jsonify(response)
    except Exception as e:
        print(f"Error fetching company details: {e}")
        return jsonify({'error': str(e)}), 500

# -------------------------
# API: Get AI Data (Simulated)
# -------------------------
@app.route('/api/get_ai_data')
def get_ai_data():
    # Use the AI model to classify risk and signals, persist risk_level to DB when possible.
    companies = db.get_all_companies()
    symbols = [c['symbol'] for c in companies]

    # Run AI analysis (this may call finnhub internally)
    try:
        ai_results = run_ai_analysis(symbols)
    except Exception as e:
        print(f"AI analysis error: {e}")
        return jsonify([])

    ai_data = []
    # Map results and persist risk_level into stock_data where we have a company record
    for res in ai_results:
        sym = res.get('symbol')
        company = db.get_company_by_symbol(sym)
        stock_row = None
        if company:
            stock_row = db.get_stock_data(company['id'])

        # Persist risk_level back to DB if we have an existing stock row (best-effort)
        if company and stock_row:
            try:
                db.update_stock_data(
                    company_id=company['id'],
                    price=stock_row.get('price'),
                    open_price=stock_row.get('open_price'),
                    high_price=stock_row.get('high_price'),
                    low_price=stock_row.get('low_price'),
                    high_52week=stock_row.get('high_52week'),
                            low_52week=stock_row.get('low_52week'),
                            dividend_yield=stock_row.get('dividend_yield'),
                            volume=stock_row.get('volume'),
                    market_cap=stock_row.get('market_cap'),
                    pe_ratio=stock_row.get('pe_ratio'),
                    eps=stock_row.get('eps') if stock_row.get('eps') is not None else None,
                    risk_level=res.get('risk_level')
                )
            except Exception as e:
                print(f"Failed to persist risk for {sym}: {e}")

        # Convert confidence to score (0-100)
        confidence_str = res.get('confidence', '50%').replace('%', '')
        try:
            score = int(confidence_str)
        except:
            score = 50
        
        # Build enriched AI payload merging with any cached metrics
        payload = {
            'name': company['name'] if company else res.get('name'),
            'symbol': sym,
            'score': score,
            'sentiment': res.get('ai_signal') or 'HOLD',
            'ai_risk': res.get('risk_level'),
            'ai_signal': res.get('ai_signal') or 'HOLD',
            'volatility': stock_row.get('volatility') if stock_row else None,
            'return_30d': stock_row.get('return_30d') if stock_row else None,
            'confidence': res.get('confidence')
        }
        ai_data.append(payload)

    return jsonify(ai_data)


# -------------------------
# Endpoints to store related data from site
# -------------------------


@app.route('/add_company', methods=['POST'])
def add_company_route():
    """Add a company by symbol. This will fetch latest data and store it in DB."""
    symbol = request.form.get('symbol') or request.json and request.json.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400

    symbol = symbol.strip().upper()

    # Use existing fetch_single_stock to get and store data
    try:
        result = fetch_single_stock(symbol)
        if result:
            return jsonify({'message': f'Added/updated {symbol}', 'data': result})
        else:
            return jsonify({'error': f'Failed to fetch data for {symbol}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update_stock', methods=['POST'])
def update_stock_route():
    """Update stock data for a single symbol (refresh cached values)."""
    symbol = request.form.get('symbol') or request.json and request.json.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400

    symbol = symbol.strip().upper()

    try:
        result = fetch_single_stock(symbol)
        if result:
            return jsonify({'message': f'Updated {symbol}', 'data': result})
        else:
            return jsonify({'error': f'Failed to update {symbol}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/add_ai_analysis', methods=['POST'])
def add_ai_analysis_route():
    """Add AI analysis for a given symbol. Expects symbol, score, sentiment, ai_risk."""
    data = request.form if request.form else (request.json or {})
    symbol = (data.get('symbol') or '').strip().upper()
    score = data.get('score')
    sentiment = data.get('sentiment')
    ai_risk = data.get('ai_risk')

    if not symbol or score is None or not sentiment or not ai_risk:
        return jsonify({'error': 'symbol, score, sentiment and ai_risk are required'}), 400

    try:
        # Ensure company exists
        company = db.get_company_by_symbol(symbol)
        if not company:
            db.add_company(symbol=symbol, name=symbol)
            company = db.get_company_by_symbol(symbol)

        if not company:
            return jsonify({'error': 'Failed to create company record'}), 500

        db.add_ai_analysis(company_id=company['id'], score=int(score), sentiment=sentiment, ai_risk=ai_risk)
        return jsonify({'message': 'AI analysis saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/add_prediction', methods=['POST'])
def add_prediction_route():
    """Add an AI prediction record. Expects symbol, prediction_date (YYYY-MM-DD), predicted_price, confidence, ai_signal."""
    data = request.form if request.form else (request.json or {})
    symbol = (data.get('symbol') or '').strip().upper()
    prediction_date = data.get('prediction_date')
    predicted_price = data.get('predicted_price')
    confidence = data.get('confidence')
    ai_signal = data.get('ai_signal')

    if not symbol or not prediction_date or predicted_price is None:
        return jsonify({'error': 'symbol, prediction_date, predicted_price required'}), 400

    try:
        db.add_prediction(symbol=symbol, prediction_date=prediction_date, predicted_price=float(predicted_price), confidence=float(confidence) if confidence else None, ai_signal=ai_signal)
        return jsonify({'message': 'Prediction saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# -------------------------
# API: AI Price Prediction
# -------------------------
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400
            
        symbol = data.get('symbol', '').upper().strip()
        
        try:
            days = int(data.get('days', 30))
        except (ValueError, TypeError):
            days = 30
        
        if not symbol or len(symbol) == 0:
            return jsonify({"error": "Stock symbol is required"}), 400
        
        if days < 1 or days > 365:
            return jsonify({"error": "Days must be between 1 and 365"}), 400
        
        print(f"Generating prediction for {symbol} ({days} days)")
        prediction = predict_stock_price(symbol, days)
        
        if prediction and prediction.get('predictions'):
            return jsonify(prediction)
        else:
            return jsonify({"error": f"Unable to fetch data for symbol {symbol}. Please verify the symbol exists."}), 500
    except Exception as e:
        print(f"Prediction error: {e}")
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

# -------------------------
# API: What-If Simulation
# -------------------------
@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400

        symbol = data.get('symbol', '').upper().strip()

        if not symbol or len(symbol) == 0:
            return jsonify({"error": "Stock symbol is required"}), 400

        try:
            shares = int(data.get('shares', 100))
            percent_change = float(data.get('percent_change', 0))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid shares or percent_change value"}), 400

        if shares < 1:
            return jsonify({"error": "Shares must be at least 1"}), 400

        time_horizon = data.get('time_horizon', 'medium')

        scenario = {
            'type': data.get('scenario_type', 'custom'),
            'percent_change': percent_change,
            'shares': shares,
            'time_horizon': time_horizon
        }

        print(f"Running simulation for {symbol}: {scenario}")
        result = simulate_what_if(symbol, scenario)

        if result:
            return jsonify(result)
        else:
            return jsonify({"error": f"Unable to fetch data for symbol {symbol}. Please verify the symbol exists."}), 500
    except Exception as e:
        print(f"Simulation error: {e}")
        return jsonify({"error": f"Simulation error: {str(e)}"}), 500

# -------------------------
# API: Get Portfolio Performance
# -------------------------
@app.route('/api/portfolio_performance')
def portfolio_performance():
    try:
        # Get 30-day history for all stocks
        portfolio_data = {}
        dates = []
        
        for symbol in STOCK_SYMBOLS:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="30d")
                
                if not hist.empty:
                    for date, row in hist.iterrows():
                        date_str = date.strftime("%Y-%m-%d")
                        if date_str not in portfolio_data:
                            portfolio_data[date_str] = 0
                            if date_str not in dates:
                                dates.append(date_str)
                        
                        # Add closing price (simulating 1 share per stock for demo)
                        portfolio_data[date_str] += float(row['Close'])
            except:
                continue
        
        # Sort dates
        dates.sort()
        
        # Prepare response
        performance = []
        for date in dates:
            performance.append({
                "date": date,
                "value": round(portfolio_data[date], 2)
            })
        
        return jsonify(performance)
    except Exception as e:
        print(f"Error calculating portfolio: {e}")
        return jsonify({"error": str(e)}), 500

# -------------------------
# API: Get Financial News
# -------------------------
@app.route('/api/news')
def get_news():
    # Return latest news using NewsAPI when available, otherwise aggregate RSS feeds
    try:
        items = get_latest_news()
        return jsonify(items)
    except Exception as e:
        print(f"News fetch error: {e}")
        return jsonify([])


# Simple caching for news (in-memory)
NEWS_CACHE = {"ts": 0, "data": []}
NEWS_TTL = int(os.getenv('NEWS_TTL_SECONDS', '300'))  # default 5 minutes


def time_ago(dt):
    if not dt:
        return 'Unknown'
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return f"{int(seconds)}s ago"
    if seconds < 3600:
        return f"{int(seconds//60)}m ago"
    if seconds < 86400:
        return f"{int(seconds//3600)}h ago"
    return f"{int(seconds//86400)}d ago"


def fetch_news_from_newsapi(api_key, page_size=10):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {'category': 'business', 'language': 'en', 'pageSize': page_size}
    headers = {'Authorization': api_key}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    j = resp.json()
    items = []
    for a in j.get('articles', []):
        pub = None
        try:
            pub = parsedate_to_datetime(a.get('publishedAt')) if a.get('publishedAt') else None
        except Exception:
            try:
                pub = datetime.fromisoformat(a.get('publishedAt')) if a.get('publishedAt') else None
            except Exception:
                pub = None

        items.append({
            'title': a.get('title'),
            'description': a.get('description') or a.get('content') or '',
            'source': a.get('source', {}).get('name') or '',
            'link': a.get('url'),
            'pubDate': pub.isoformat() if pub else None,
            'time': time_ago(pub) if pub else 'Unknown'
        })
    return items


def fetch_rss_feed(feed_url, max_items=8):
    try:
        r = requests.get(feed_url, timeout=8, headers={'User-Agent': 'Stalkify-News/1.0'})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = []
        # RSS and Atom support
        for item in root.findall('.//item')[:max_items]:
            title = item.findtext('title')
            desc = item.findtext('description') or item.findtext('{http://www.w3.org/2005/Atom}summary') or ''
            link = item.findtext('link') or item.findtext('{http://www.w3.org/2005/Atom}link')
            pub = item.findtext('pubDate') or item.findtext('{http://www.w3.org/2005/Atom}updated')
            dt = None
            try:
                if pub:
                    dt = parsedate_to_datetime(pub)
            except Exception:
                try:
                    dt = datetime.fromisoformat(pub)
                except Exception:
                    dt = None

            items.append({
                'title': title,
                'description': desc,
                'source': feed_url.split('/')[2] if '//' in feed_url else feed_url,
                'link': link,
                'pubDate': dt.isoformat() if dt else None,
                'time': time_ago(dt) if dt else 'Unknown'
            })
        return items
    except Exception as e:
        print(f"RSS fetch error for {feed_url}: {e}")
        return []


def get_latest_news(limit=8):
    now_ts = int(datetime.now(timezone.utc).timestamp())
    if NEWS_CACHE['data'] and (now_ts - NEWS_CACHE['ts'] < NEWS_TTL):
        return NEWS_CACHE['data']

    items = []
    # Try NewsAPI if key provided
    api_key = os.getenv('NEWS_API_KEY')
    if api_key:
        try:
            items = fetch_news_from_newsapi(api_key, page_size=limit)
        except Exception as e:
            print(f"NewsAPI error: {e}")
            items = []

    if not items:
        feeds = [
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://feeds.cnbc.com/cnbc/id/100003114/device/rss/rss.html',
            'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'https://feeds.finance.yahoo.com/rss/2.0/headline'
        ]
        seen = set()
        for f in feeds:
            for it in fetch_rss_feed(f, max_items=limit):
                if it.get('link') and it['link'] in seen:
                    continue
                seen.add(it.get('link'))
                items.append(it)
                if len(items) >= limit:
                    break
            if len(items) >= limit:
                break

    # Sort by pubDate if available
    def sort_key(i):
        try:
            return parsedate_to_datetime(i['pubDate']) if i.get('pubDate') else datetime.now(timezone.utc)
        except Exception:
            try:
                return datetime.fromisoformat(i['pubDate']) if i.get('pubDate') else datetime.now(timezone.utc)
            except Exception:
                return datetime.now(timezone.utc)

    items.sort(key=sort_key, reverse=True)
    items = items[:limit]

    NEWS_CACHE['ts'] = now_ts
    NEWS_CACHE['data'] = items
    return items


# -------------------------
# Background updater (batch fetch + cache)
# -------------------------
def chunked(iterable, size):
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def refresh_all_stocks(chunk_size=100):
    """Fetch stock data in parallel using ThreadPoolExecutor and update DB cache."""
    symbols = STOCK_SYMBOLS
    total = len(symbols)
    if total == 0:
        return

    print(f"Starting parallel refresh of {total} stocks (max {chunk_size} workers)...")
    processed = 0

    # Use optimized batch processing
    with ThreadPoolExecutor(max_workers=min(chunk_size, total)) as executor:
        futures = {executor.submit(fetch_single_stock, symbol): symbol for symbol in symbols}

        for i, future in enumerate(as_completed(futures), 1):
            try:
                result = future.result()
                if result:
                    processed += 1
            except Exception as e:
                symbol = futures[future]
                print(f"Error processing symbol {symbol}: {e}")

            if i % 20 == 0:
                print(f"Processed {i}/{total} stocks...")

    print(f"Completed parallel processing {processed}/{total} stocks")

def refresh_all_stocks_fast(chunk_size=150):
    """Fast refresh using batch processing and simplified data fetching."""
    symbols = STOCK_SYMBOLS
    total = len(symbols)
    if total == 0:
        return

    print(f"Starting FAST parallel refresh of {total} stocks (max {chunk_size} workers)...")

    def fetch_stock_basic(symbol):
        """Simplified stock fetch for faster loading."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")  # Reduced from 30d to 5d

            if hist is None or hist.empty:
                return None

            current_price = float(hist['Close'].iloc[-1])
            if len(hist) > 1:
                prev_close = float(hist['Close'].iloc[-2])
                change_percent = ((current_price - prev_close) / prev_close) * 100
            else:
                change_percent = 0

            # Simplified info fetch
            try:
                info = ticker.info or {}
                name = info.get("shortName") or info.get("longName") or symbol
                market_cap = info.get("marketCap")
                volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist else None
            except Exception:
                name = symbol
                market_cap = None
                volume = None

            # Simplified risk calculation (skip complex volatility for speed)
            risk_level = "Moderate"  # Default

            # Fast DB update
            try:
                db.add_company(
                    symbol=symbol,
                    name=name,
                    sector=None,  # Skip for speed
                    industry=None,
                    website=None,
                    description=None
                )
                company = db.get_company_by_symbol(symbol)
                if company:
                    db.update_stock_data(
                        company_id=company['id'],
                        price=current_price,
                        open_price=float(hist['Open'].iloc[-1]) if 'Open' in hist else None,
                        high_price=float(hist['High'].iloc[-1]) if 'High' in hist else None,
                        low_price=float(hist['Low'].iloc[-1]) if 'Low' in hist else None,
                        volume=volume,
                        market_cap=market_cap,
                        risk_level=risk_level
                    )
            except Exception as e:
                print(f"DB error for {symbol}: {e}")

            return {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "change_percent": round(change_percent, 2),
                "risk_level": risk_level
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None

    processed = 0
    with ThreadPoolExecutor(max_workers=min(chunk_size, total)) as executor:
        futures = {executor.submit(fetch_stock_basic, symbol): symbol for symbol in symbols}

        for i, future in enumerate(as_completed(futures), 1):
            try:
                result = future.result()
                if result:
                    processed += 1
            except Exception as e:
                symbol = futures[future]
                print(f"Error processing symbol {symbol}: {e}")

            if i % 25 == 0:
                print(f"Processed {i}/{total} stocks...")

    print(f"Completed FAST parallel processing {processed}/{total} stocks")


def background_updater(interval_seconds=600):
    """Background thread that refreshes stock cache every `interval_seconds`."""
    print(f"Background updater started, refreshing every {interval_seconds} seconds")
    first_run = True
    while True:
        try:
            if first_run:
                print("Running initial stock cache refresh...")
                first_run = False
            refresh_all_stocks(chunk_size=50)
            print(f"Stock cache refresh completed. Next refresh in {interval_seconds}s")
        except Exception as e:
            print(f"Background refresh error: {e}")
        _time.sleep(interval_seconds)


# Start background updater thread (daemon)
def start_background_thread():
    t = threading.Thread(target=background_updater, kwargs={'interval_seconds': 300}, daemon=True)
    t.start()


@app.route('/admin/refresh_stocks', methods=['POST'])
def admin_refresh_stocks():
    """Trigger immediate refresh of cached stock data (starts in background)."""
    data = request.get_json() or {}
    fast_mode = data.get('fast', False)

    def run_refresh():
        try:
            if fast_mode:
                refresh_all_stocks_fast(chunk_size=150)
                print("FAST manual refresh completed")
            else:
                refresh_all_stocks(chunk_size=100)
                print("Manual refresh completed")
        except Exception as e:
            print(f"Manual refresh error: {e}")

    threading.Thread(target=run_refresh, daemon=True).start()
    mode = "FAST" if fast_mode else "FULL"
    return jsonify({'message': f'{mode} refresh started'}), 202

@app.route('/admin/refresh_stocks_fast', methods=['POST'])
def admin_refresh_stocks_fast():
    """Trigger FAST immediate refresh of cached stock data (starts in background)."""
    def run_refresh():
        try:
            refresh_all_stocks_fast(chunk_size=150)
            print("FAST manual refresh completed")
        except Exception as e:
            print(f"FAST manual refresh error: {e}")

    threading.Thread(target=run_refresh, daemon=True).start()
    return jsonify({'message': 'FAST refresh started'}), 202

# -------------------------
# API: Get Watchlist
# -------------------------
@app.route('/api/watchlist')
def get_watchlist_api():
    watchlist = db.get_watchlist()
    return jsonify(watchlist)

# -------------------------
# API: Add to Watchlist
# -------------------------
@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist_api():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    if db.add_to_watchlist(symbol):
        return jsonify({"message": f"Added {symbol} to watchlist"})
    else:
        return jsonify({"error": "Failed to add to watchlist"}), 500

# -------------------------
# API: Remove from Watchlist
# -------------------------
@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist_api():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    
    db.remove_from_watchlist(symbol)
    return jsonify({"message": f"Removed {symbol} from watchlist"})

# -------------------------
# API: Get Portfolio
# -------------------------
@app.route('/api/portfolio/<int:portfolio_id>')
def get_portfolio_api(portfolio_id):
    holdings = db.get_portfolio_holdings(portfolio_id)
    return jsonify(holdings)

# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("STALKIFY - AI Stock Market Analysis Platform")
    print("=" * 60)
    print(f"📊 Tracking {len(STOCK_SYMBOLS)} stocks (269 comprehensive market coverage)")
    print(f"💾 Database: stalkify.db")
    print("🌐 Server starting on http://127.0.0.1:5000")
    print("⚡ Performance: Batched loading, caching, and background updates")
    print("=" * 60)
    # Start the background updater before serving requests
    start_background_thread()
    app.run(debug=True, use_reloader=False)
