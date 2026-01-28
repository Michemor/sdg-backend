# SETUP_GUIDE.md - Complete Backend Setup Instructions

## Quick Start (Development)

### Prerequisites
- Python 3.12+
- PostgreSQL 12+ (optional, SQLite used by default)
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd impactDashboard
```

### 2. Create Virtual Environment
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Key settings:**
- `DEBUG=True` (for development)
- `SECRET_KEY` - Keep the default or generate a new one
- `DATABASE_URL` - Use sqlite:///db.sqlite3 for quick start
- `GEMINI_API_KEY` - Optional; leave blank if not setting up AI features

### 5. Initialize Database
```bash
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

### 6. (Optional) Create Sample SDG Data
```bash
python manage.py shell

# In Python shell:
from impact_tracker.models import SDGGoal

sdg_data = [
    ("No Poverty", "End poverty in all its forms everywhere"),
    ("Zero Hunger", "End hunger, achieve food security"),
    ("Good Health and Well-Being", "Ensure healthy lives and promote well-being"),
    ("Quality Education", "Ensure inclusive and equitable quality education"),
    ("Gender Equality", "Achieve gender equality and empower women"),
    ("Clean Water and Sanitation", "Ensure access to water and sanitation"),
    ("Affordable and Clean Energy", "Ensure access to affordable energy"),
    ("Decent Work and Economic Growth", "Promote sustained economic growth"),
    ("Industry, Innovation and Infrastructure", "Build resilient infrastructure"),
    ("Reduced Inequalities", "Reduce inequality within and among countries"),
    ("Sustainable Cities and Communities", "Make cities sustainable"),
    ("Responsible Consumption and Production", "Ensure sustainable consumption"),
    ("Climate Action", "Take urgent action on climate change"),
    ("Life Below Water", "Conserve and sustainably use oceans"),
    ("Life on Land", "Protect, restore and promote sustainable use of ecosystems"),
    ("Peace, Justice and Strong Institutions", "Promote peaceful societies"),
    ("Partnerships for the Goals", "Strengthen implementation partnerships"),
]

for i, (name, description) in enumerate(sdg_data, 1):
    SDGGoal.objects.create(
        number=i,
        name=name,
        description=description
    )

print("Created 17 SDG Goals!")
exit()
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Server starts at `http://localhost:8000`

---

## Environment Variables Reference

### Database Configuration

**SQLite (Development - Quick Start)**
```
DATABASE_URL=sqlite:///db.sqlite3
```

**PostgreSQL (Production-Like)**
```
DATABASE_URL=postgres://username:password@localhost:5432/daystar_sdg
```

### Google Gemini API Setup (Optional)

The AI classification feature is optional. To enable it:

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy the API key
4. Add to `.env`:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

**Note:** Without this key, the API works normally but won't auto-classify activities. Activities can still be created without classification.

### CORS Configuration

For frontend running on different port/domain:

```
# For localhost development (default)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# For production
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## PostgreSQL Setup (Optional)

Use PostgreSQL if you want a production-like database for local development.

### Linux/macOS
```bash
# Install PostgreSQL
brew install postgresql  # macOS
# or
sudo apt install postgresql postgresql-contrib  # Ubuntu

# Start PostgreSQL
brew services start postgresql  # macOS
# or
sudo systemctl start postgresql  # Ubuntu

# Create database and user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE daystar_sdg;
CREATE USER daystar_user WITH PASSWORD 'daystar_pass_123';
ALTER ROLE daystar_user SET client_encoding TO 'utf8';
ALTER ROLE daystar_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE daystar_user SET default_transaction_deferrable TO on;
ALTER ROLE daystar_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE daystar_sdg TO daystar_user;
\q
```

### Windows
```powershell
# Download PostgreSQL installer from https://www.postgresql.org/download/windows/
# Run installer, note the password you create
# PostgreSQL runs as Windows service

# Open PostgreSQL command line:
# Start menu > PostgreSQL > SQL Shell (psql)
# Connect using admin user and password

# Create database and user:
CREATE DATABASE daystar_sdg;
CREATE USER daystar_user WITH PASSWORD 'daystar_pass_123';
GRANT ALL PRIVILEGES ON DATABASE daystar_sdg TO daystar_user;
```

### Update .env
```
DATABASE_URL=postgres://daystar_user:daystar_pass_123@localhost:5432/daystar_sdg
```

### Run Migrations
```bash
python manage.py migrate
```

---

## Project Structure

```
impactDashboard/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── README.md                    # Project overview
├── API_DOCUMENTATION.md         # API reference
├── FRONTEND_INTEGRATION.md      # Frontend guide
├── DEPLOYMENT.md                # Production setup
│
├── daystar_sdg/                 # Main Django project
│   ├── settings.py              # Django configuration
│   ├── urls.py                  # URL routing
│   ├── wsgi.py                  # WSGI entry point
│   ├── asgi.py                  # ASGI entry point
│   └── __init__.py
│
├── impact_tracker/              # Main application
│   ├── models.py                # Database models
│   ├── views.py                 # API views/viewsets
│   ├── serializers.py           # DRF serializers
│   ├── admin.py                 # Django admin config
│   ├── reports.py               # PDF generation
│   ├── tests.py                 # Unit tests
│   ├── apps.py                  # App configuration
│   ├── py.typed                 # Type checking marker
│   │
│   └── migrations/              # Database migrations
│       ├── 0001_initial.py
│       └── __init__.py
│
├── services/                    # Business logic
│   ├── classifier.py            # Gemini AI integration
│   └── __init__.py
│
└── media/                       # User uploads (created at runtime)
    └── evidence/                # Activity evidence files
```

---

## Testing the API

### Using cURL
```bash
# Login and get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/activities/
```

### Using Python
```python
from rest_framework.test import APIClient

client = APIClient()

# Login
response = client.post('/api/auth/login/', {
    'username': 'admin',
    'password': 'your_password'
})
token = response.data['access']

# Authenticated request
client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
response = client.get('/api/activities/')
print(response.json())
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
python manage.py runserver 8001
```

### Database Errors
```bash
# Reset database (DELETES ALL DATA!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission Errors on Media Upload
```bash
# Ensure media directory is writable
chmod -R 755 media/
sudo chown -R $USER:$USER media/
```

---

## Next Steps

1. **Read API Documentation**: See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Frontend Integration**: See [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
3. **For Production**: See [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Add Tests**: Create `tests/` directory with test files
5. **Set Gemini API**: Optional but enables AI classification

---

## Common Commands

```bash
# Run development server
python manage.py runserver

# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run tests
python manage.py test

# Create admin user
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic

# Clear sessions/cache (if configured)
python manage.py clearsessions

# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json
```

---

**Version:** 1.0  
**Last Updated:** January 20, 2026  
**Maintained by:** Development Team
