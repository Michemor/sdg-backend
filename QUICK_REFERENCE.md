# QUICK_REFERENCE.md - Frontend Developer Cheat Sheet

## 🚀 Quick Commands

```bash
# Setup (first time only)
git clone <repo>
cd impactDashboard
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver

# API Base URL
http://localhost:8000/api/
```

## 🔐 Authentication Pattern

```javascript
// 1. Login to get token
const loginRes = await fetch('http://localhost:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'password' })
});
const { access } = await loginRes.json();

// 2. Use token in all requests
const headers = { 'Authorization': `Bearer ${access}` };

// 3. If token expires, refresh it
const refreshRes = await fetch('http://localhost:8000/api/auth/token/refresh/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ refresh: refreshToken })
});
```

## 📡 Essential Endpoints

| Method | Endpoint | Auth? | Purpose |
|--------|----------|-------|---------|
| POST | `/auth/login/` | ❌ | Get JWT token |
| GET | `/sdg/` | ❌ | List all 17 goals |
| GET | `/sdg/{id}/` | ❌ | Get SDG details |
| POST | `/activities/upload/` | ✅ | Create activity |
| GET | `/activities/` | ✅ | List activities |
| GET | `/activities/{id}/` | ✅ | Get activity details |
| GET | `/dashboard/summary/` | ❌ | Dashboard metrics |
| GET | `/analytics/trends/` | ❌ | Analytics data |
| GET | `/reports/generate/{id}/` | ✅ | Generate PDF |

## 📝 Upload Activity (Multipart Form Data)

```javascript
const formData = new FormData();
formData.append('title', 'Climate Research Project');
formData.append('description', 'Research on carbon sequestration methods');
formData.append('activity_type', 'research');  // or: project, curriculum, outreach
formData.append('evidence_file', fileInput.files[0]);

const res = await fetch('http://localhost:8000/api/activities/upload/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData  // NOT JSON!
});
const activity = await res.json();
```

## 📊 Response Format

### Success (200-201)
```json
{
  "id": 1,
  "title": "Climate Research",
  "description": "...",
  "activity_type": "research",
  "lead_author_detail": {
    "id": 1,
    "username": "admin"
  },
  "sdg_impacts": [
    {
      "id": 42,
      "sdg_goal": 13,
      "score": 95,
      "justification": "Directly addresses climate action..."
    }
  ]
}
```

### Error (400-500)
```json
{
  "error": "Field name error message",
  "detail": "Not found."
}
```

## 🔗 CORS Headers Setup

In `.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

Change `localhost:3000` to your frontend URL.

## 🚨 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | No/wrong token | Include `Authorization: Bearer TOKEN` header |
| `403 Forbidden` | Not authenticated | Login first to get token |
| `415 Unsupported Media Type` | Using JSON for file upload | Use `FormData` instead |
| `CORS error in console` | Frontend URL not allowed | Update `CORS_ALLOWED_ORIGINS` in `.env` |
| `404 Not Found` | Wrong endpoint URL | Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) |
| `400 Bad Request` | Missing required field | Check request payload |

## 💾 Database Models

### SDGGoal (17 UN Goals)
```python
{
  "id": 3,
  "number": 3,
  "name": "Good Health and Well-Being",
  "description": "Ensure healthy lives..."
}
```

### Activity
```python
{
  "id": 1,
  "title": "Research Project",
  "description": "Description...",
  "activity_type": "research",  # research, project, curriculum, outreach
  "evidence_file": "/media/evidence/file.pdf",
  "lead_author_detail": {"id": 1, "username": "admin"},
  "date_created": "2024-01-20T10:30:00Z",
  "ai_classified": true,
  "sdg_impacts": [...]
}
```

### SDGImpact (Junction)
```python
{
  "id": 42,
  "activity": 1,
  "sdg_goal": 3,
  "score": 95,  # 0-100
  "justification": "This activity helps with..."
}
```

## 🎨 Activity Types

```
research    → Academic research
project     → Implementation project
curriculum  → Educational curriculum
outreach    → Community outreach
```

## 🧮 SDG Numbers & Names

```
1: No Poverty
2: Zero Hunger
3: Good Health and Well-Being
4: Quality Education
5: Gender Equality
6: Clean Water and Sanitation
7: Affordable and Clean Energy
8: Decent Work and Economic Growth
9: Industry, Innovation and Infrastructure
10: Reduced Inequalities
11: Sustainable Cities and Communities
12: Responsible Consumption and Production
13: Climate Action
14: Life Below Water
15: Life on Land
16: Peace, Justice and Strong Institutions
17: Partnerships for the Goals
```

## 📦 Environment Variables

```bash
# Required for setup
DATABASE_URL=postgres://user:pass@localhost/db  # or sqlite:///db.sqlite3
SECRET_KEY=your-secret-key

# Required for frontend
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Optional for AI features
GEMINI_API_KEY=your-api-key
```

## ⚡ Performance Tips

- Use `select_related()` and `prefetch_related()` (already implemented)
- Cache dashboard summary if heavy queries
- Implement pagination for activity lists
- Compress uploaded files before sending

## 📖 Reading Order

1. This file (Quick Reference)
2. [SETUP_GUIDE.md](SETUP_GUIDE.md) - Get running
3. [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - All endpoints
4. [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) - Integration patterns

## 🔄 Full Request/Response Example

```bash
# 1. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"pass"}' \
  -i

# Returns header: "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."

# 2. List SDGs
curl http://localhost:8000/api/sdg/ \
  -H "Accept: application/json"

# 3. Get dashboard
curl http://localhost:8000/api/dashboard/summary/ \
  -H "Accept: application/json"

# 4. Upload activity (using token from step 1)
curl -X POST http://localhost:8000/api/activities/upload/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -F "title=My Activity" \
  -F "description=Description" \
  -F "activity_type=research" \
  -F "evidence_file=@/path/to/file.pdf"
```

## 🔧 Debugging Commands

```bash
# Check if API is running
curl http://localhost:8000/api/ -v

# Get server logs
python manage.py runserver  # Shows logs in console

# Test database
python manage.py dbshell

# Check configurations
python manage.py check --deploy

# Create test data
python manage.py shell < fixtures.py
```

## 📱 Frontend Stack Compatibility

Tested with:
- ✅ React
- ✅ Vue.js
- ✅ Angular
- ✅ Vanilla JavaScript
- ✅ Fetch API
- ✅ Axios
- ✅ jQuery

Works with any framework using standard HTTP requests.

## 🆘 Quick Troubleshooting Flowchart

```
API not responding?
├─ Is backend running? → python manage.py runserver
└─ Check localhost:8000/api/

Getting CORS error?
└─ Update CORS_ALLOWED_ORIGINS in .env

Authentication failing?
├─ Login first to get token
└─ Include "Authorization: Bearer TOKEN" header

File upload failing?
├─ Use FormData, not JSON
└─ Include file in multipart/form-data

Still stuck?
└─ See full guides in documentation folder
```

---

**Keep this handy while developing!**

For full details, see:
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete reference
- [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) - Integration guide
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Setup instructions
