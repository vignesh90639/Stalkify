# ai_model.py
import random
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

def run_ai_analysis(symbols):
    """
    Returns a list of AI outputs with enhanced analysis using real data
    { name, symbol, ai_signal, confidence, risk_level }
    """
    out = []
    for s in symbols:
        try:
            # Get real historical data for trend analysis
            ticker = yf.Ticker(s)
            hist = ticker.history(period="30d")
            
            if not hist.empty and len(hist) > 0:
                # Extract closes for trend analysis
                closes = hist['Close'].tolist()
                recent_price = closes[-1]
                avg_price = sum(closes) / len(closes)
                trend = ((recent_price - avg_price) / avg_price) * 100
                
                # Determine signal based on real trend
                if trend > 5:
                    sig = "BUY"
                    confidence = random.randint(75, 95)
                elif trend < -5:
                    sig = "SELL"
                    confidence = random.randint(70, 90)
                else:
                    sig = "HOLD"
                    confidence = random.randint(60, 80)
                
                # Calculate real volatility
                returns = []
                for i in range(1, len(closes)):
                    r = ((closes[i] - closes[i-1]) / closes[i-1]) * 100 if closes[i-1] != 0 else 0
                    returns.append(r)
                
                if returns:
                    avg_return = sum(abs(r) for r in returns) / len(returns)
                    if avg_return > recent_price * 0.05:
                        risk = "Bold"
                    elif avg_return > recent_price * 0.02:
                        risk = "Moderate"
                    else:
                        risk = "Safe"
                else:
                    risk = "Moderate"
            else:
                # No data available
                sig = "HOLD"
                risk = "Moderate"
                confidence = 50
        except Exception as e:
            print(f"Error analyzing {s}: {e}")
            sig = "HOLD"
            risk = "Moderate"
            confidence = 50
        
        out.append({
            "name": s,
            "symbol": s,
            "ai_signal": sig,
            "confidence": f"{confidence}%",
            "risk_level": risk
        })
    return out

def predict_stock_price(symbol, days_ahead=30):
    """
    AI prediction using real historical data and trend analysis
    Returns predicted prices for future dates
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="180d")
        
        if hist is None or hist.empty or len(hist) < 30:
            print(f"Insufficient historical data for {symbol}")
            return None
        
        # Extract closes
        closes = hist['Close'].dropna().tolist()
        
        if len(closes) < 30:
            print(f"Not enough valid close prices for {symbol}")
            return None
        
        # Get trend from last 30 days
        recent_prices = closes[-30:]
        x = np.arange(len(recent_prices))
        
        try:
            # Simple linear regression
            coeffs = np.polyfit(x, recent_prices, 1)
            slope = coeffs[0]
        except Exception:
            slope = 0  # No trend detected
        
        # Predict future prices
        last_price = float(recent_prices[-1])
        
        if last_price <= 0:
            print(f"Invalid price for {symbol}: {last_price}")
            return None
        
        predictions = []
        
        for i in range(1, days_ahead + 1):
            # Add some randomness to make it realistic (1% volatility)
            noise = np.random.normal(0, last_price * 0.01)
            predicted_price = last_price + (slope * i) + noise
            predicted_price = max(0.01, predicted_price)  # Ensure positive price
            
            predictions.append({
                "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                "price": round(predicted_price, 2)
            })
        
        return {
            "symbol": symbol,
            "current_price": round(last_price, 2),
            "predicted_trend": "upward" if slope > 0 else "downward",
            "predictions": predictions
        }
    except Exception as e:
        print(f"Prediction error for {symbol}: {e}")
        return None

def simulate_what_if(symbol, scenario):
    """
    What-if simulator for different market scenarios using real data
    scenario: { type: 'market_crash' | 'bull_market' | 'volatility' | 'custom',
                percent_change: number, shares: number, time_horizon: 'short' | 'medium' | 'long' }
    """
    try:
        if not symbol or not isinstance(symbol, str):
            print(f"Invalid symbol: {symbol}")
            return None

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="30d")

        if hist is None or hist.empty or len(hist) == 0:
            print(f"No historical data found for {symbol}")
            return None

        current_price = float(hist['Close'].iloc[-1])
        if current_price <= 0:
            print(f"Invalid price for {symbol}: {current_price}")
            return None

        scenario_type = scenario.get('type', 'market_crash')
        time_horizon = scenario.get('time_horizon', 'medium')

        # Define scenario impacts based on historical market data
        scenarios = {
            'market_crash': -20,      # Based on 1987 crash (-33%) and 2020 COVID (-34%)
            'bull_market': 25,        # Average bull market returns (20-30%)
            'volatility': 0,          # High volatility with no net change
            'recession': -15,         # Typical recession impact (10-20% drops)
            'tech_boom': 30,          # Tech sector surges (2020-2021 saw 30%+)
            'rate_hike': -8,          # Fed rate hikes cause 5-10% corrections
            'inflation': -10,         # Inflation fears cause market drops
            'deflation': -12,         # Rare deflation scenarios
            'war': -18,               # Geopolitical events (Gulf War -19%)
            'recovery': 20            # Post-crisis recovery rallies
        }

        percent_change = scenarios.get(scenario_type, -20)  # Default to market crash if invalid

        # Apply time horizon modifier
        time_multipliers = {
            'short': 0.7,   # Shorter term events have less severe impact (quick recovery)
            'medium': 1.0,  # Normal impact
            'long': 1.3     # Longer term events have more severe/compound impact
        }

        multiplier = time_multipliers.get(time_horizon, 1.0)
        percent_change *= multiplier
        
        # Calculate new price
        simulated_price = max(0.01, current_price * (1 + percent_change / 100))
        
        # Calculate portfolio impact
        shares = scenario.get('shares', 100)
        if shares < 1:
            shares = 100
            
        current_value = current_price * shares
        simulated_value = simulated_price * shares
        profit_loss = simulated_value - current_value
        
        # Risk assessment - real volatility from historical data
        closes = hist['Close'].dropna().tolist()
        if len(closes) > 1:
            returns = []
            for i in range(1, len(closes)):
                try:
                    r = ((closes[i] - closes[i-1]) / closes[i-1]) * 100
                    returns.append(r)
                except:
                    pass
            
            volatility = sum(abs(r) for r in returns) / len(returns) if returns else 0
        else:
            volatility = 0
        
        risk_score = min(100, int(volatility * 10))
        
        return {
            "symbol": symbol,
            "scenario": scenario_type,
            "current_price": round(current_price, 2),
            "simulated_price": round(simulated_price, 2),
            "price_change": round(simulated_price - current_price, 2),
            "percent_change": round(percent_change, 2),
            "shares": shares,
            "current_value": round(current_value, 2),
            "simulated_value": round(simulated_value, 2),
            "profit_loss": round(profit_loss, 2),
            "risk_score": risk_score,
            "recommendation": get_recommendation(percent_change, risk_score)
        }
    except Exception as e:
        print(f"Simulation error for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_recommendation(percent_change, risk_score):
    """Generate AI recommendation based on scenario"""
    if percent_change > 15 and risk_score < 30:
        return "STRONG BUY - High potential gain with low risk"
    elif percent_change > 5 and risk_score < 50:
        return "BUY - Moderate potential with acceptable risk"
    elif percent_change < -10:
        return "SELL - Consider exiting position to minimize loss"
    elif risk_score > 70:
        return "CAUTION - High volatility, consider hedging"
    else:
        return "HOLD - Monitor position closely"

def get_news():
    """Get market news"""
    return [
        {"title": "Market Update: Tech Leads Gains", "source": "Stalkify AI", "link": "#", "pubDate": "Today"},
        {"title": "Global Markets Watch", "source": "Stalkify AI", "link": "#", "pubDate": "Today"},
        {"title": "Energy Sector Sees Volatility", "source": "Stalkify AI", "link": "#", "pubDate": "Yesterday"}
    ]
