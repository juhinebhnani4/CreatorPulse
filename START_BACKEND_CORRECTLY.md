# How to Start Backend Correctly

## ⚠️ Issue

The backend can't find the `.env` file because it's looking in the wrong location.

## ✅ Correct Way to Start Backend

### From the ROOT directory (scraper-scripts/):

```bash
# Make sure you're in the root directory
cd "E:\Career coaching\100x\scraper-scripts"

# Start backend from root
.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

### Why This Works:

```
scraper-scripts/           ← You should be HERE
├── .env                   ← Backend config looks for ../.env (parent dir)
├── backend/
│   ├── config.py          ← Sets env_file="../.env"
│   └── main.py
└── .venv/
```

When you run from `scraper-scripts/`, the backend's `../. env` resolves to `scraper-scripts/.env` ✅

## ❌ Wrong Way

```bash
# Don't do this:
cd backend
python -m uvicorn main:app --reload

# Backend's ../. env would look for scraper-scripts/.env (doesn't exist)
```

## 🧪 Verify It Works

After starting correctly, test the health endpoint:

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "environment": "development",
    "timestamp": "..."
  }
}
```

## 🚀 Quick Start Command

**Copy and paste this:**

```bash
cd "E:\Career coaching\100x\scraper-scripts" && .venv\Scripts\python.exe -m uvicorn backend.main:app --reload --port 8000
```

That's it! The backend will:
- ✅ Load .env from root directory
- ✅ Connect to Supabase
- ✅ Auto-reload on code changes
- ✅ Run the FIXED user creation code
