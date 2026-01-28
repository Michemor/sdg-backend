# PRE-GITHUB-PUSH-CHECKLIST.md

## Security Check ✓

### Environment & Secrets
- [ ] Verify `.env` is in `.gitignore` and NOT committed
- [ ] Verify `.env.example` has NO real secrets (only template values)
- [ ] Verify `SECRET_KEY` in `.env.example` is a placeholder
- [ ] Verify `GEMINI_API_KEY` is empty in `.env.example`
- [ ] Verify database credentials are NOT in any committed files
- [ ] Search repo for hardcoded passwords: `grep -r "password" --include="*.py" | grep -v ".pyc"`
- [ ] Verify no API keys in code: `grep -r "sk-" --include="*.py"`

### Django Settings
- [ ] Verify `DEBUG = False` is documented for production
- [ ] Verify `ALLOWED_HOSTS` requirement is documented
- [ ] Verify `SECRET_KEY` must be regenerated in production
- [ ] Verify CSRF and CORS whitelist requirements are clear

### Code Safety
- [ ] Run: `python manage.py check --deploy`
- [ ] Check for SQL injection vulnerabilities (use ORM exclusively)
- [ ] Verify file uploads have proper validation
- [ ] Verify JWT tokens aren't leaked in logs

---

## Code Quality Check ✓

### Python Style
- [ ] Code follows PEP 8 (use `flake8` or `black`)
- [ ] No unused imports
- [ ] No debug print statements
- [ ] No commented-out code blocks
- [ ] Type hints present where possible

### Django Best Practices
- [ ] Model validation proper (MinValueValidator, MaxValueValidator)
- [ ] Foreign keys have proper cascade/protect choices
- [ ] Database indexes on frequently queried fields
- [ ] Proper error handling with try/except blocks
- [ ] Efficient database queries (select_related, prefetch_related used)

### API Quality
- [ ] Proper HTTP status codes used
- [ ] Consistent error response format
- [ ] Request/response properly documented
- [ ] Input validation on all endpoints
- [ ] Rate limiting noted (even if not implemented)

---

## Documentation Check ✓

### Files Created
- [ ] ✓ `README.md` - Project overview and features
- [ ] ✓ `SETUP_GUIDE.md` - Detailed setup instructions
- [ ] ✓ `API_DOCUMENTATION.md` - Complete endpoint reference
- [ ] ✓ `FRONTEND_INTEGRATION.md` - Frontend developer guide
- [ ] ✓ `DEPLOYMENT.md` - Production deployment guide
- [ ] ✓ `.env.example` - Environment template

### Documentation Content
- [ ] README explains what the project does
- [ ] README lists technology stack
- [ ] README has quick start instructions
- [ ] API docs list all endpoints
- [ ] API docs show request/response examples
- [ ] API docs explain authentication flow
- [ ] FRONTEND_INTEGRATION has JavaScript examples
- [ ] DEPLOYMENT has production checklist
- [ ] SETUP_GUIDE explains both SQLite and PostgreSQL

### Code Comments
- [ ] Complex functions have docstrings
- [ ] Unclear business logic is commented
- [ ] API views document their purpose
- [ ] Models document field purposes

---

## Dependencies Check ✓

### requirements.txt
- [ ] All dependencies are listed with versions
- [ ] No local/relative paths
- [ ] Version pinning prevents breaking changes
- [ ] `pip freeze > requirements.txt` matches file content
- [ ] Test dependencies noted separately (if any)

### Current Stack
- [ ] Django 5.1.4 ✓
- [ ] Django REST Framework 3.14.0 ✓
- [ ] djangorestframework-simplejwt 5.5.1 ✓
- [ ] django-cors-headers 4.3.1 ✓
- [ ] psycopg2-binary 2.9.9 (PostgreSQL) ✓
- [ ] python-dotenv 1.0.0 ✓
- [ ] google-generativeai 0.3.0 ✓
- [ ] dj-database-url 2.1.0 ✓
- [ ] reportlab 4.0.9 ✓

---

## Database Schema Check ✓

### Models Present
- [ ] ✓ SDGGoal (17 UN Sustainable Development Goals)
- [ ] ✓ Activity (university activities with evidence)
- [ ] ✓ SDGImpact (junction table linking activities to goals)
- [ ] ✓ InstitutionMetric (yearly metrics per institution)

### Model Structure
- [ ] Proper foreign keys with correct on_delete behavior
- [ ] Unique constraints where needed (SDGGoal.number 1-17)
- [ ] Field validators present (MinValueValidator, MaxValueValidator)
- [ ] Timestamps (created_at, updated_at) if needed
- [ ] All fields have help_text or verbose_name

### Migrations
- [ ] All migrations are in version control
- [ ] Migration files have descriptive names
- [ ] No manual SQL migrations
- [ ] Fresh database can be created from migrations: `python manage.py migrate`

---

## API Endpoints Check ✓

### Required Endpoints
- [ ] ✓ POST `/api/auth/login/` - Get JWT token
- [ ] ✓ POST `/api/auth/logout/` - Logout
- [ ] ✓ POST `/api/activities/upload/` - Upload new activity
- [ ] ✓ GET `/api/activities/` - List activities
- [ ] ✓ GET `/api/activities/{id}/` - Get activity details
- [ ] ✓ PUT `/api/activities/{id}/` - Update activity
- [ ] ✓ GET `/api/sdg/` - List SDG goals
- [ ] ✓ GET `/api/sdg/{id}/` - Get SDG details
- [ ] ✓ GET `/api/dashboard/summary/` - Dashboard metrics
- [ ] ✓ GET `/api/analytics/trends/` - Analytics data
- [ ] ✓ GET `/api/reports/generate/{sdg_id}/` - Generate PDF report

### Endpoint Details
- [ ] Authentication requirement documented
- [ ] Query parameters documented
- [ ] Response format shown with examples
- [ ] Error responses documented
- [ ] CORS headers explained

---

## File Structure Check ✓

### Required Files
- [ ] ✓ `manage.py` - Django management
- [ ] ✓ `requirements.txt` - Dependencies
- [ ] ✓ `.gitignore` - Version control ignore
- [ ] ✓ `daystar_sdg/settings.py` - Configuration
- [ ] ✓ `daystar_sdg/urls.py` - Routing
- [ ] ✓ `impact_tracker/models.py` - Database models
- [ ] ✓ `impact_tracker/views.py` - API views
- [ ] ✓ `impact_tracker/serializers.py` - Data serialization
- [ ] ✓ `impact_tracker/admin.py` - Admin interface
- [ ] ✓ `services/classifier.py` - AI integration
- [ ] ✓ `.vscode/settings.json` - IDE configuration

### Excluded Files (Should NOT be in repo)
- [ ] `.env` file
- [ ] `db.sqlite3`
- [ ] `__pycache__/` directories
- [ ] `.pyc` files
- [ ] `*.egg-info/`
- [ ] `venv/` or `virtualenv/`
- [ ] `.pytest_cache/`
- [ ] `media/` (with real uploads)

---

## Frontend Integration Check ✓

### CORS Configuration
- [ ] CORS_ALLOWED_ORIGINS includes frontend URL
- [ ] Documentation explains CORS setup
- [ ] Headers allow credentials (if needed)
- [ ] Preflight requests handled

### Authentication
- [ ] JWT token flow documented
- [ ] Example frontend code provided
- [ ] Token refresh mechanism explained
- [ ] Common auth errors documented

### Data Format
- [ ] Consistent JSON response format
- [ ] Error response format specified
- [ ] File upload multipart/form-data documented
- [ ] Nested relationships explained

### Examples Provided
- [ ] cURL examples for endpoints
- [ ] JavaScript Fetch examples
- [ ] Axios configuration example
- [ ] Authentication example
- [ ] File upload example

---

## Testing Check ⚠️

### Note: Tests are not yet implemented (optional for initial release)

For future versions:
- [ ] Unit tests for models
- [ ] Unit tests for serializers
- [ ] Unit tests for views/viewsets
- [ ] Integration tests for API flow
- [ ] Test data fixtures
- [ ] Mock Gemini API responses

Run tests with: `python manage.py test`

---

## Git Setup Check ✓

### Repository State
- [ ] Repository initialized: `git init`
- [ ] `.gitignore` properly configured
- [ ] No `.env` file in git status
- [ ] No `__pycache__` in git status
- [ ] No media uploads in git status

### Initial Commit
```bash
git add .
git commit -m "Initial backend setup: Django API with SDG impact tracking"
git remote add origin <your-repo-url>
git push -u origin main
```

---

## README.md Sections Check ✓

- [ ] Project title and description
- [ ] Feature list
- [ ] Technology stack
- [ ] Quick start instructions
- [ ] Project structure explanation
- [ ] Database schema overview
- [ ] API overview
- [ ] Contribution guidelines
- [ ] License information
- [ ] Contact/Support information

---

## Gemini API Setup Note

The project is ready for Gemini API integration but doesn't require it to run:

- [ ] Documented that `GEMINI_API_KEY` is optional
- [ ] Explained what happens without the key (activities created but not classified)
- [ ] Provided link to get API key: https://aistudio.google.com/app/apikeys
- [ ] Documented fallback behavior

**Status:** ⚠️ Not configured in `.env` (intentional)

---

## Common Issues to Document

### ✓ Documented in guides:
1. **Port Already in Use** - How to change port or kill process
2. **Database Connection** - SQLite vs PostgreSQL instructions
3. **CORS Errors** - How to configure CORS_ALLOWED_ORIGINS
4. **Authentication Errors** - Token format and JWT explanation
5. **File Upload Errors** - multipart/form-data requirement
6. **Import Errors** - pip reinstall command
7. **PostgreSQL Not Running** - Service start commands
8. **Permission Denied** - chmod/chown commands

---

## Production Deployment Check ✓

Documented in DEPLOYMENT.md:
- [ ] Security settings for production
- [ ] Database setup (PostgreSQL)
- [ ] Gunicorn configuration
- [ ] Nginx reverse proxy setup
- [ ] SSL/TLS certificates (Let's Encrypt)
- [ ] Systemd service file
- [ ] Backup procedures
- [ ] Monitoring setup
- [ ] Troubleshooting guide

---

## Final Checklist

### Before Pushing to GitHub:
1. [ ] All security checks passed
2. [ ] All dependencies in requirements.txt
3. [ ] All documentation files created
4. [ ] .env NOT in git (only .env.example)
5. [ ] No debug code or print statements
6. [ ] Models have proper validation
7. [ ] API endpoints tested and working
8. [ ] CORS configured for development
9. [ ] Database migrations applied
10. [ ] Test with fresh `python manage.py runserver`

### After Pushing to GitHub:
1. [ ] Repository is public/private as intended
2. [ ] README is visible on repo home
3. [ ] All documentation files appear in repo
4. [ ] Clone fresh copy and test: `git clone <url>` → setup → run
5. [ ] Share repo with frontend team
6. [ ] Send link to API_DOCUMENTATION.md
7. [ ] Send link to SETUP_GUIDE.md
8. [ ] Send link to DEPLOYMENT.md (if doing production)

---

## Summary

✅ **Backend Ready for GitHub**

All critical components are in place:
- Secure configuration with no leaked secrets
- Complete API documentation with examples
- Clear setup instructions for developers
- Production deployment guidance
- Frontend integration guidelines
- Comprehensive troubleshooting

⚠️ **Optional for future versions:**
- Unit/integration tests
- Docker containerization
- Swagger/OpenAPI documentation
- Rate limiting implementation
- Structured logging

---

**Status:** Ready to push to GitHub  
**Date:** January 20, 2026  
**Version:** 1.0
