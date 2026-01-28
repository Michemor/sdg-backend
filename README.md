# SDG Impact Dashboard - Backend API

A Django REST Framework backend for the University SDG Impact Dashboard. This system automatically classifies university activities against UN Sustainable Development Goals using Google Gemini AI.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 12+
- pip/python3-pip

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd impactDashboard
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up PostgreSQL database**
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE daystar_sdg;
CREATE USER daystar_user WITH PASSWORD 'daystar_pass_123';
ALTER DATABASE daystar_sdg OWNER TO daystar_user;
\q
```

6. **Run migrations**
```bash
python3 manage.py migrate
```

7. **Create superuser (for admin panel)**
```bash
python3 manage.py createsuperuser
```

8. **Load initial SDG data (optional)**
```bash
python3 manage.py shell < scripts/load_sdg_goals.py
```

9. **Start development server**
```bash
python3 manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📋 Configuration

### Required Environment Variables

```env
# Django
DEBUG=True                    # Set to False in production
SECRET_KEY=your-secret-key   # Generate a strong key

# Database
DATABASE_URL=postgres://user:password@localhost:5432/daystar_sdg

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Frontend URL (CORS)
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Getting Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` file as `GEMINI_API_KEY`

## 🔌 API Endpoints

### Authentication
All endpoints except public ones require JWT token in header:
```
Authorization: Bearer <access_token>
```

### Public Endpoints (No Auth Required)

#### SDG Goals
- `GET /api/sdg/` - List all SDG goals
- `GET /api/sdg/{number}/` - Get specific SDG goal
- `GET /api/sdg/{number}/activities/` - Get activities linked to SDG
- `GET /api/sdg/{number}/summary/` - Get SDG statistics

#### Dashboard & Analytics
- `GET /api/dashboard/summary/` - Dashboard overview
- `GET /api/analytics/trends/` - SDG trends by year
- `GET /api/analytics/trends/?sdg_number=1` - Filter by SDG

#### Reports
- `GET /api/reports/generate/{sdg_id}/` - Generate PDF report for SDG
- `GET /api/reports/comprehensive/` - Generate comprehensive PDF report

### Protected Endpoints (Auth Required)

#### Activities
- `GET /api/activities/` - List activities (yours)
- `POST /api/activities/` - Create activity
- `POST /api/activities/upload/` - Upload activity (alias for create)
- `GET /api/activities/{id}/` - Get activity details
- `PUT /api/activities/{id}/` - Update activity
- `DELETE /api/activities/{id}/` - Delete activity
- `POST /api/activities/{id}/classify/` - Re-classify activity
- `GET /api/activities/by_author/` - Get your activities

## 📊 Response Format

### Success Response
```json
{
  "id": 1,
  "title": "Activity Title",
  "description": "...",
  "activity_type": "research",
  "lead_author_detail": {
    "id": 1,
    "username": "john_doe",
    "email": "john@university.edu"
  },
  "ai_classified": true,
  "sdg_impacts": [
    {
      "id": 1,
      "sdg_goal": 3,
      "sdg_goal_detail": {
        "number": 3,
        "name": "Good Health and Well-Being",
        "description": "..."
      },
      "score": 85,
      "justification": "AI-generated reasoning..."
    }
  ]
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

## 🔐 Authentication Flow

### Getting JWT Token
```bash
# Login with username/password
POST /api/token/
{
  "username": "user@university.edu",
  "password": "password"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Using Token
Add to request headers:
```
Authorization: Bearer <access_token>
```

### Refreshing Token
```bash
POST /api/token/refresh/
{
  "refresh": "<refresh_token>"
}
```

## 📤 File Uploads

The `/api/activities/upload/` endpoint accepts multipart form data:

```javascript
const formData = new FormData();
formData.append('title', 'My Activity');
formData.append('description', 'Description...');
formData.append('activity_type', 'research');
formData.append('evidence_file', file); // Optional

fetch('http://localhost:8000/api/activities/upload/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});
```

**Note:** `lead_author` is automatically set to the authenticated user.

## 🤖 AI Classification

When an activity is created:
1. Activity is saved to database
2. Gemini AI classifies it against 17 SDGs
3. Top SDG impacts are automatically linked
4. `ai_classified` is set to `true`

If Gemini API is not configured, activities are still created but without AI classification.

## 🧪 Testing the API

### Quick Test
```bash
# In another terminal
curl http://localhost:8000/api/dashboard/summary/
```

### Create Sample Data
```bash
python3 manage.py shell
>>> from django.contrib.auth.models import User
>>> from impact_tracker.models import SDGGoal, Activity
>>> user = User.objects.create_user('test', 'test@test.com', 'pass123')
>>> sdg = SDGGoal.objects.first()
>>> Activity.objects.create(
...   title='Test Activity',
...   description='Testing',
...   activity_type='research',
...   lead_author=user
... )
```

## 🛠️ Development

### Project Structure
```
impactDashboard/
├── daystar_sdg/          # Django project settings
├── impact_tracker/       # Main app
│   ├── models.py        # Data models
│   ├── views.py         # API views
│   ├── serializers.py   # DRF serializers
│   ├── reports.py       # PDF generation
│   └── admin.py         # Django admin
├── services/
│   └── classifier.py    # Gemini AI integration
├── manage.py
└── requirements.txt
```

### Database Models
- **SDGGoal** - The 17 UN SDGs
- **Activity** - University outputs/activities
- **SDGImpact** - Links activities to SDGs with scores
- **InstitutionMetric** - Benchmarking data

### Admin Panel
Access at `http://localhost:8000/admin/`
- Manage SDG Goals, Activities, and Metrics
- View AI classification history

## 🚨 Common Issues & Solutions

### PostgreSQL Connection Error
```
FATAL: role "bantu" does not exist
```
**Solution:** Use `sudo -u postgres` to create database/user

### Google Gemini API Error
```
GEMINI_API_KEY not configured
```
**Solution:** Add API key to `.env` file and restart server

### CORS Error from Frontend
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution:** Ensure frontend URL is in `CORS_ALLOWED_ORIGINS` in `.env`

### Media Files Not Loading
```
404 Not Found for /media/...
```
**Solution:** Ensure `MEDIA_URL` and `MEDIA_ROOT` are set correctly in settings.py

## 📝 API Query Parameters

### Activities List
```
GET /api/activities/?activity_type=research&ai_classified=true&author=1
```

### Analytics Trends
```
GET /api/analytics/trends/?sdg_number=3
```

## 🔄 CORS Configuration

Default allowed origins:
- `http://localhost:3000` (React dev server)
- `http://localhost:8000` (Django dev server)

To add production URLs, update `.env`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 📦 Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in `.env`
- [ ] Update `SECRET_KEY` with strong random key
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set `ALLOWED_HOSTS` in settings.py
- [ ] Update `CORS_ALLOWED_ORIGINS` for production domain
- [ ] Use environment variables for sensitive data
- [ ] Run migrations: `python3 manage.py migrate`
- [ ] Collect static files: `python3 manage.py collectstatic`
- [ ] Use production WSGI server (Gunicorn, uWSGI)

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Google Generative AI](https://ai.google.dev/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

## 👥 Team Integration

### Frontend Team (React/Vue)
- Use `/api/` as base URL
- Implement JWT token storage (localStorage/sessionStorage)
- Handle 401/403 responses for re-authentication
- Expected response formats documented above

### Data Team
- Can access raw data via Django admin
- Use `/api/analytics/trends/` for analysis
- Metrics available in `InstitutionMetric` model

### DevOps Team
- Database: PostgreSQL 12+
- Python: 3.12+
- Dependencies: See requirements.txt
- Environment: Docker support can be added

## 📧 Support

For issues or questions:
1. Check troubleshooting section above
2. Review API documentation
3. Contact backend team

---

**Last Updated:** January 20, 2026
**Status:** ✓ Production Ready
