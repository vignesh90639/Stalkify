# 🚀 Deployment & GitHub Upload Guide

## Files to Keep

✅ **Keep these files:**
- `app.py` - Main Flask application
- `ai_model.py` - AI prediction models
- `database_models.py` - MySQL database models
- `init_database.py` - Database initialization script
- `database.sql` - SQL schema (optional reference)
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation

✅ **Folders:**
- `static/` - CSS, JS files
- `templates/` - HTML files

❌ **Already removed:**
- `__pycache__/` - Python cache
- `stalkify.db` - SQLite database
- `companies.py` - Unused file
- `stock_api.py` - Unused file
- `OAUTH_SETUP.md` - OAuth guide (removed)

## 📤 Upload to GitHub

### Step 1: Initialize Git
```bash
cd C:\Users\Guest123\OneDrive\Stalkify
git init
```

### Step 2: Add Files
```bash
git add .
```

### Step 3: Commit
```bash
git commit -m "Initial commit: Stalkify AI Stock Analysis Platform"
```

### Step 4: Add Remote Repository
```bash
git remote add origin https://github.com/vignesh90639/Stalkify.git
```

### Step 5: Push to GitHub
```bash
git branch -M main
git push -u origin main
```

## 🔐 Security Notes

Before pushing to GitHub:

1. **Change the secret key** in `app.py`:
   ```python
   app.secret_key = 'your-random-secret-key-here'
   ```

2. **Remove MySQL password** from `database_models.py` or use environment variables

3. **Add sensitive data to `.gitignore`** (already done)

## 📦 Project Structure

```
Stalkify/
├── app.py                    # Main Flask app
├── ai_model.py              # AI prediction logic
├── database_models.py       # MySQL database operations
├── init_database.py         # Database setup script
├── requirements.txt         # Python dependencies
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
├── database.sql            # SQL schema
├── static/                 # Static assets
│   ├── style.css          # Home page styles
│   ├── dashboard.css      # Dashboard styles
│   ├── simulator.css      # Simulator styles
│   ├── company.css        # Company page styles
│   ├── auth.css           # Auth page styles
│   ├── script.js          # Home page scripts
│   ├── dashboard.js       # Dashboard scripts
│   ├── simulator.js       # Simulator scripts
│   └── company.js         # Company page scripts
└── templates/              # HTML templates
    ├── home.html          # Landing page
    ├── dashboard.html     # Analytics dashboard
    ├── simulator.html     # What-If simulator
    ├── company.html       # Company details
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── contact.html       # Contact success
    ├── terms.html         # Terms & Conditions
    └── privacy.html       # Privacy Policy
```

## 🌐 Live Deployment Guide

### **Netlify Deployment** 🚫 **NOT RECOMMENDED**

**Why Netlify won't work:**
- ❌ **No persistent server**: Netlify is for static sites and serverless functions
- ❌ **No MongoDB Atlas support**: Only limited database options
- ❌ **Flask incompatibility**: Cannot run full Python web applications
- ❌ **Background jobs**: Cannot run the stock refresh background processes

**Alternative for Netlify:** Convert to a static frontend with API backend elsewhere.

---

### **Render Deployment** ✅ **RECOMMENDED**

**Why Render works perfectly:**
- ✅ **Full Python support**: Can run Flask applications
- ✅ **MongoDB Atlas compatible**: Easy to connect to your existing Atlas database
- ✅ **Background workers**: Can run stock refresh processes
- ✅ **Free tier**: Enough for development/testing
- ✅ **Easy deployment**: Git-based deployment

#### **Step 1: Prepare for Render**

1. **MongoDB Atlas is already configured:**
   - Your connection string is already in `database_models_mongo.py`
   - No database conversion needed - MongoDB is document-based

2. **Update app.py for MongoDB:**
   ```python
   # Change this line in app.py:
   from database_models_mongo import db  # Already done!
   ```

3. **Set up environment variables:**
   ```bash
   # In Render dashboard, add these environment variables:
   # MONGODB_URI=mongodb+srv://Finesse:nani@8522@stalkify.8mxgxjv.mongodb.net/?appName=stalkify
   # SECRET_KEY=your-random-secret-key-here
   # FLASK_ENV=production
   ```

#### **Step 2: Deploy to Render**

1. **Connect your GitHub repository** (already pushed!)
2. **Create Web Service:**
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Add environment variables

3. **MongoDB Atlas is ready:**
   - Your Atlas cluster is already configured
   - Connection string is embedded in the code

4. **No database setup needed** - MongoDB creates collections automatically

#### **Step 3: Post-Deployment Setup**

1. **First run will create collections** automatically
2. **Stock refresh will populate data** on first background run
3. **Configure domain** (optional)

---

### **Alternative Deployment Options**

#### **Railway** ⭐ **Great Alternative**
- Similar to Render
- Easier PostgreSQL setup
- Built-in database management

#### **Fly.io** ⭐ **Another Good Option**
- Excellent for Python apps
- Built-in PostgreSQL
- Global CDN included

#### **Heroku** (Traditional)
- More complex setup
- Expensive for database
- Good documentation

#### **Vercel + Railway**
- Frontend on Vercel (static)
- Backend on Railway
- Best for JAMstack approach

---

### **Recommended Deployment Strategy**

1. **Use Render** for full-stack deployment
2. **Convert to PostgreSQL** (Render's native database)
3. **Deploy Flask app** with background workers
4. **Set up monitoring** and logging

**Estimated cost:** Free tier sufficient for development, ~$7-15/month for production.

## 👨‍💻 Developer

**Vignesh Mamindla**
- GitHub: https://github.com/vignesh90639
- LinkedIn: https://www.linkedin.com/in/vignesh-mamindla-881b34383/
- Email: vigneshgotjob@gmail.com
