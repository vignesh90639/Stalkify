# database_models_mongo.py - MongoDB Database Models for Atlas
import pymongo
from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId

class Database:
    def __init__(self, connection_string=None):
        """Initialize MongoDB database connection"""
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = os.getenv('MONGODB_URI', 'mongodb+srv://Finesse:nani@8522@stalkify.8mxgxjv.mongodb.net/?appName=stalkify')

        self.client = MongoClient(self.connection_string)
        self.db = self.client['stalkify']
        self.init_collections()

    def init_collections(self):
        """Ensure collections exist (MongoDB creates them automatically)"""
        # Collections will be created automatically when first document is inserted
        # We can add indexes here if needed
        try:
            # Create indexes for better performance
            self.db.companies.create_index([("symbol", 1)], unique=True)
            self.db.stock_data.create_index([("company_id", 1)])
            self.db.ai_analysis.create_index([("company_id", 1)])
            self.db.price_history.create_index([("symbol", 1), ("date", -1)])
            self.db.portfolios.create_index([("user_id", 1)])
            self.db.holdings.create_index([("portfolio_id", 1), ("symbol", 1)])
            self.db.watchlist.create_index([("user_id", 1), ("symbol", 1)], unique=True)
            self.db.predictions.create_index([("symbol", 1)])
            self.db.users.create_index([("username", 1)], unique=True)
            self.db.users.create_index([("email", 1)], unique=True)
        except Exception as e:
            print(f"Index creation error: {e}")

    # ===== COMPANY OPERATIONS =====

    def add_company(self, symbol, name, sector=None, industry=None, website=None, description=None):
        """Add or update a company"""
        try:
            company_data = {
                "symbol": symbol,
                "name": name,
                "sector": sector,
                "industry": industry,
                "website": website,
                "description": description[:500] if description else None,
                "created_at": datetime.utcnow()
            }

            # Upsert operation (insert or update)
            result = self.db.companies.update_one(
                {"symbol": symbol},
                {"$set": company_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
                upsert=True
            )

            # Get the company document
            company = self.db.companies.find_one({"symbol": symbol})
            return str(company["_id"]) if company else None

        except Exception as e:
            print(f"Error adding company: {e}")
            return None

    def get_all_companies(self):
        """Get all companies"""
        try:
            companies = list(self.db.companies.find({}, {"_id": 0}).sort("symbol", 1))
            # Convert ObjectId to string for JSON serialization
            for company in companies:
                if "_id" in company:
                    company["_id"] = str(company["_id"])
            return companies
        except Exception as e:
            print(f"Error getting companies: {e}")
            return []

    def get_company_by_symbol(self, symbol):
        """Get company by symbol"""
        try:
            company = self.db.companies.find_one({"symbol": symbol}, {"_id": 0})
            return company
        except Exception as e:
            print(f"Error getting company: {e}")
            return None

    # ===== STOCK DATA OPERATIONS =====

    def update_stock_data(self, company_id, price, open_price, high_price, low_price,
                         high_52week, low_52week, dividend_yield, volume, market_cap, pe_ratio, eps, risk_level=None, volatility=None, return_30d=None):
        """Update stock data"""
        try:
            stock_data = {
                "company_id": company_id,
                "risk_level": risk_level,
                "price": price,
                "open_price": open_price,
                "high_price": high_price,
                "low_price": low_price,
                "high_52week": high_52week,
                "low_52week": low_52week,
                "dividend_yield": dividend_yield,
                "volume": volume,
                "market_cap": market_cap,
                "pe_ratio": pe_ratio,
                "eps": eps,
                "volatility": volatility,
                "return_30d": return_30d,
                "last_updated": datetime.utcnow()
            }

            # Replace existing data for this company
            self.db.stock_data.replace_one(
                {"company_id": company_id},
                stock_data,
                upsert=True
            )

            return True
        except Exception as e:
            print(f"Error updating stock data: {e}")
            return False

    def get_stock_data(self, company_id):
        """Get latest stock data"""
        try:
            data = self.db.stock_data.find_one({"company_id": company_id}, {"_id": 0})
            return data
        except Exception as e:
            print(f"Error getting stock data: {e}")
            return None

    def get_all_stocks_with_data(self):
        """Get all companies with their stock data in ONE query (optimized)"""
        try:
            # Use MongoDB aggregation pipeline to join collections
            pipeline = [
                {
                    "$lookup": {
                        "from": "stock_data",
                        "localField": "_id",
                        "foreignField": "company_id",
                        "as": "stock_data"
                    }
                },
                {
                    "$unwind": {
                        "path": "$stock_data",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": {"$toString": "$_id"},
                        "symbol": 1,
                        "name": 1,
                        "sector": 1,
                        "industry": 1,
                        "website": 1,
                        "description": 1,
                        "created_at": 1,
                        "company_id": {"$toString": "$_id"},
                        "risk_level": "$stock_data.risk_level",
                        "price": "$stock_data.price",
                        "open_price": "$stock_data.open_price",
                        "high_price": "$stock_data.high_price",
                        "low_price": "$stock_data.low_price",
                        "high_52week": "$stock_data.high_52week",
                        "low_52week": "$stock_data.low_52week",
                        "dividend_yield": "$stock_data.dividend_yield",
                        "volume": "$stock_data.volume",
                        "market_cap": "$stock_data.market_cap",
                        "pe_ratio": "$stock_data.pe_ratio",
                        "eps": "$stock_data.eps",
                        "volatility": "$stock_data.volatility",
                        "return_30d": "$stock_data.return_30d",
                        "last_updated": "$stock_data.last_updated"
                    }
                },
                {"$sort": {"symbol": 1}}
            ]

            results = list(self.db.companies.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error getting stocks with data: {e}")
            return []

    # ===== PRICE HISTORY OPERATIONS =====

    def add_price_history(self, symbol, date, open_price, high, low, close, volume):
        """Add historical price data"""
        try:
            # Convert date string to datetime if needed
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d")

            price_data = {
                "symbol": symbol,
                "date": date,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume
            }

            # Upsert operation
            self.db.price_history.replace_one(
                {"symbol": symbol, "date": date},
                price_data,
                upsert=True
            )

            return True
        except Exception as e:
            print(f"Error adding price history: {e}")
            return False

    def get_price_history(self, symbol, days=30):
        """Get price history for a stock"""
        try:
            prices = list(self.db.price_history.find(
                {"symbol": symbol},
                {"_id": 0}
            ).sort("date", -1).limit(days))

            return prices
        except Exception as e:
            print(f"Error getting price history: {e}")
            return []

    # ===== PORTFOLIO OPERATIONS =====

    def create_portfolio(self, user_id='default', name='My Portfolio'):
        """Create a new portfolio"""
        try:
            portfolio_data = {
                "user_id": user_id,
                "name": name,
                "created_at": datetime.utcnow()
            }

            result = self.db.portfolios.insert_one(portfolio_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating portfolio: {e}")
            return None

    def add_holding(self, portfolio_id, symbol, shares, purchase_price=None, purchase_date=None):
        """Add a stock holding to portfolio"""
        try:
            if purchase_date is None:
                purchase_date = datetime.utcnow().date()

            holding_data = {
                "portfolio_id": portfolio_id,
                "symbol": symbol,
                "shares": shares,
                "purchase_price": purchase_price,
                "purchase_date": purchase_date
            }

            self.db.holdings.insert_one(holding_data)
            return True
        except Exception as e:
            print(f"Error adding holding: {e}")
            return False

    def get_portfolio_holdings(self, portfolio_id):
        """Get all holdings in a portfolio"""
        try:
            # Use aggregation to join with companies collection
            pipeline = [
                {"$match": {"portfolio_id": portfolio_id}},
                {
                    "$lookup": {
                        "from": "companies",
                        "localField": "symbol",
                        "foreignField": "symbol",
                        "as": "company"
                    }
                },
                {
                    "$unwind": {
                        "path": "$company",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": {"$toString": "$_id"},
                        "portfolio_id": 1,
                        "symbol": 1,
                        "shares": 1,
                        "purchase_price": 1,
                        "purchase_date": 1,
                        "name": "$company.name",
                        "sector": "$company.sector"
                    }
                }
            ]

            holdings = list(self.db.holdings.aggregate(pipeline))
            return holdings
        except Exception as e:
            print(f"Error getting portfolio holdings: {e}")
            return []

    # ===== WATCHLIST OPERATIONS =====

    def add_to_watchlist(self, symbol, user_id='default'):
        """Add stock to watchlist"""
        try:
            watchlist_data = {
                "user_id": user_id,
                "symbol": symbol,
                "added_date": datetime.utcnow()
            }

            self.db.watchlist.insert_one(watchlist_data)
            return True
        except Exception as e:
            # Check if it's a duplicate key error (already exists)
            if "duplicate key" in str(e).lower():
                return False
            print(f"Error adding to watchlist: {e}")
            return False

    def get_watchlist(self, user_id='default'):
        """Get user's watchlist"""
        try:
            # Use aggregation to join with companies collection
            pipeline = [
                {"$match": {"user_id": user_id}},
                {
                    "$lookup": {
                        "from": "companies",
                        "localField": "symbol",
                        "foreignField": "symbol",
                        "as": "company"
                    }
                },
                {
                    "$unwind": {
                        "path": "$company",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": {"$toString": "$_id"},
                        "user_id": 1,
                        "symbol": 1,
                        "added_date": 1,
                        "name": "$company.name",
                        "sector": "$company.sector"
                    }
                },
                {"$sort": {"added_date": -1}}
            ]

            watchlist = list(self.db.watchlist.aggregate(pipeline))
            return watchlist
        except Exception as e:
            print(f"Error getting watchlist: {e}")
            return []

    def remove_from_watchlist(self, symbol, user_id='default'):
        """Remove stock from watchlist"""
        try:
            result = self.db.watchlist.delete_one({"user_id": user_id, "symbol": symbol})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error removing from watchlist: {e}")
            return False

    # ===== AI ANALYSIS OPERATIONS =====

    def add_ai_analysis(self, company_id, score, sentiment, ai_risk):
        """Add AI analysis"""
        try:
            analysis_data = {
                "company_id": company_id,
                "score": score,
                "sentiment": sentiment,
                "ai_risk": ai_risk,
                "created_at": datetime.utcnow()
            }

            self.db.ai_analysis.insert_one(analysis_data)
            return True
        except Exception as e:
            print(f"Error adding AI analysis: {e}")
            return False

    def get_ai_analysis(self, company_id, limit=10):
        """Get AI analysis for a company"""
        try:
            analysis = list(self.db.ai_analysis.find(
                {"company_id": company_id},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit))

            return analysis
        except Exception as e:
            print(f"Error getting AI analysis: {e}")
            return []

    # ===== USER OPERATIONS =====

    def create_user(self, username, email, password_hash=None, full_name=None, oauth_provider=None, oauth_id=None, avatar_url=None):
        """Create a new user"""
        try:
            user_data = {
                "username": username,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "oauth_provider": oauth_provider,
                "oauth_id": oauth_id,
                "avatar_url": avatar_url,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "is_active": True
            }

            result = self.db.users.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            if "duplicate key" in str(e).lower():
                return None
            print(f"Error creating user: {e}")
            return None

    def get_user_by_oauth(self, oauth_provider, oauth_id):
        """Get user by OAuth provider and ID"""
        try:
            user = self.db.users.find_one({
                "oauth_provider": oauth_provider,
                "oauth_id": oauth_id
            }, {"_id": 0})
            return user
        except Exception as e:
            print(f"Error getting user by OAuth: {e}")
            return None

    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            user = self.db.users.find_one({"username": username}, {"_id": 0})
            return user
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None

    def get_user_by_email(self, email):
        """Get user by email"""
        try:
            user = self.db.users.find_one({"email": email}, {"_id": 0})
            return user
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    def update_last_login(self, user_id):
        """Update user's last login time"""
        try:
            self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return True
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False

    # ===== PREDICTION OPERATIONS =====

    def add_prediction(self, symbol, prediction_date, predicted_price, confidence, ai_signal):
        """Add AI prediction"""
        try:
            prediction_data = {
                "symbol": symbol,
                "prediction_date": prediction_date,
                "predicted_price": predicted_price,
                "confidence": confidence,
                "ai_signal": ai_signal,
                "created_at": datetime.utcnow()
            }

            self.db.predictions.insert_one(prediction_data)
            return True
        except Exception as e:
            print(f"Error adding prediction: {e}")
            return False

    def get_predictions(self, symbol, limit=10):
        """Get AI predictions for a stock"""
        try:
            predictions = list(self.db.predictions.find(
                {"symbol": symbol},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit))

            return predictions
        except Exception as e:
            print(f"Error getting predictions: {e}")
            return []

# Initialize database with MongoDB Atlas connection
db = Database('mongodb+srv://Finesse:nani@8522@stalkify.8mxgxjv.mongodb.net/?appName=stalkify')
