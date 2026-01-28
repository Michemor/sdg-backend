# Frontend Integration Guide

## 🎯 What Frontend Developers Need to Know

### 1. Base API URL
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

### 2. Authentication (JWT)
Frontend must handle token storage and refresh:

```javascript
// Login
const response = await fetch(`${API_BASE_URL}/token/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: email,
    password: password
  })
});

const { access, refresh } = await response.json();

// Store tokens
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);

// Use in requests
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
};
```

### 3. CORS Setup
The backend allows requests from:
- `http://localhost:3000` (default React/Vue)
- `http://localhost:8000` (Django dev server)

**For production:** Update `CORS_ALLOWED_ORIGINS` in `.env`

### 4. Error Handling
```javascript
const handleApiError = (error) => {
  if (error.status === 401) {
    // Token expired - refresh or redirect to login
    refreshToken();
  } else if (error.status === 403) {
    // Forbidden - user doesn't have permission
    showError('Access denied');
  } else if (error.status === 404) {
    // Not found
    showError('Resource not found');
  } else if (error.status >= 500) {
    // Server error
    showError('Server error - try again later');
  }
};
```

### 5. File Upload
For activities with evidence files:

```javascript
const formData = new FormData();
formData.append('title', 'Activity Title');
formData.append('description', 'Description');
formData.append('activity_type', 'research');
formData.append('evidence_file', fileInput.files[0]); // File object

const response = await fetch(`${API_BASE_URL}/activities/upload/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`
    // Don't set Content-Type - browser will set it with boundary
  },
  body: formData
});
```

### 6. Pagination
```javascript
// Fetch with pagination
const response = await fetch(`${API_BASE_URL}/activities/?page=1`);
const data = await response.json();

// Response structure
{
  "count": 100,        // Total items
  "next": "http://...",    // Next page URL
  "previous": null,    // Previous page URL
  "results": [...]     // Items on this page
}
```

### 7. Activity Types
Valid values for `activity_type`:
- `'research'` - Research publications/projects
- `'project'` - Implementation projects
- `'curriculum'` - Educational programs
- `'outreach'` - Community engagement

### 8. SDG Numbers (1-17)
```javascript
const SDG_NUMBERS = {
  1: 'No Poverty',
  2: 'Zero Hunger',
  3: 'Good Health and Well-Being',
  4: 'Quality Education',
  5: 'Gender Equality',
  6: 'Clean Water and Sanitation',
  7: 'Affordable and Clean Energy',
  8: 'Decent Work and Economic Growth',
  9: 'Industry, Innovation and Infrastructure',
  10: 'Reduced Inequalities',
  11: 'Sustainable Cities and Communities',
  12: 'Responsible Consumption and Production',
  13: 'Climate Action',
  14: 'Life Below Water',
  15: 'Life on Land',
  16: 'Peace, Justice and Strong Institutions',
  17: 'Partnerships for the Goals'
};
```

### 9. Response Data Structure

**Activity object:**
```javascript
{
  id: 1,
  title: "Research Title",
  description: "...",
  activity_type: "research",
  lead_author_detail: {
    username: "john_doe",
    email: "john@university.edu",
    first_name: "John",
    last_name: "Doe"
  },
  ai_classified: true,
  date_created: "2026-01-20T10:00:00Z",
  sdg_impacts: [
    {
      sdg_goal: 7,
      sdg_goal_detail: {
        number: 7,
        name: "Affordable and Clean Energy"
      },
      score: 92,  // 0-100
      justification: "This activity..."
    }
  ]
}
```

**SDG object:**
```javascript
{
  number: 7,
  name: "Affordable and Clean Energy",
  description: "Ensure access to...",
  icon_url: "https://..."
}
```

### 10. Common API Patterns

**Get all SDGs:**
```javascript
const sdgs = await fetch(`${API_BASE_URL}/sdg/`);
```

**Get activities for specific SDG:**
```javascript
const activities = await fetch(`${API_BASE_URL}/sdg/7/activities/`);
```

**Get dashboard summary:**
```javascript
const summary = await fetch(`${API_BASE_URL}/dashboard/summary/`);
```

**Get trends data:**
```javascript
const trends = await fetch(`${API_BASE_URL}/analytics/trends/`);
// Optional: filter by SDG
const trends = await fetch(`${API_BASE_URL}/analytics/trends/?sdg_number=7`);
```

**Create activity (with auto AI classification):**
```javascript
const activity = await fetch(`${API_BASE_URL}/activities/upload/`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
// Response includes sdg_impacts automatically populated
```

---

## 🚨 Important Gotchas

### ⚠️ CORS Headers
- The backend handles CORS automatically
- Don't send `Content-Type: application/json` with file uploads
- Let browser set it automatically with multipart boundary

### ⚠️ Token Management
- Access tokens expire after some time
- Implement token refresh logic
- Store refresh token securely (httpOnly cookie preferred)
- Handle 401 responses to trigger re-login

### ⚠️ Lead Author Auto-Set
- Don't send `lead_author` in activity creation
- It's automatically set to the authenticated user
- This prevents users from creating activities as other users

### ⚠️ Pagination
- Default page size: 100 items
- Always check `response.count` for total items
- Use `next`/`previous` URLs, don't hardcode page numbers

### ⚠️ File Upload
- Max file size depends on Django configuration (default 2.5MB)
- Only PDF/Image formats recommended
- Store in `/media/evidence/` folder

### ⚠️ AI Classification
- Happens automatically when activity is created
- Requires `GEMINI_API_KEY` in backend `.env`
- If API fails, activity is still created with `ai_classified: false`
- Can manually re-trigger with `/api/activities/{id}/classify/`

---

## 🔐 Security Considerations

1. **Never log tokens** - They contain user info
2. **Use HTTPS in production** - Never send tokens over HTTP
3. **Store tokens securely** - Prefer httpOnly cookies over localStorage
4. **Validate user input** - Sanitize before sending to API
5. **Handle 403 responses** - Respect permission boundaries
6. **Implement CSRF tokens** - If using cookies (not needed with JWT)

---

## 📱 Recommended Frontend Libraries

### For API calls:
- **Axios** - HTTP client with interceptors for token management
- **Fetch API** - Built-in, native JavaScript
- **React Query** - Caching and state management
- **SWR** - Data fetching with cache invalidation

### For state management:
- **Redux** - Store tokens and user state
- **Pinia/Vuex** - Vue state management
- **Zustand** - Lightweight alternative

### Example with Axios:
```javascript
import axios from 'axios';

// Create instance with defaults
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Refresh token logic
      const refreshToken = localStorage.getItem('refresh_token');
      const newAccessToken = await refreshAccessToken(refreshToken);
      localStorage.setItem('access_token', newAccessToken);
      
      // Retry original request
      return api.request(error.config);
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 🧪 Test Endpoints Before Integration

Use Postman or curl to test:

```bash
# Get all SDGs
curl http://localhost:8000/api/sdg/

# Get dashboard summary
curl http://localhost:8000/api/dashboard/summary/

# Get trends
curl http://localhost:8000/api/analytics/trends/

# Get token (replace with real credentials)
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Create activity (replace with real token)
curl -X POST http://localhost:8000/api/activities/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Test Activity" \
  -F "description=Test" \
  -F "activity_type=research"
```

---

## 📋 Frontend Checklist

- [ ] JWT token storage & refresh logic implemented
- [ ] CORS errors resolved (check backend `.env`)
- [ ] Error handling for all status codes (400, 401, 403, 404, 500)
- [ ] Pagination implemented for activity lists
- [ ] File upload form validates file type/size
- [ ] Loading states shown during API calls
- [ ] Token expiration handled gracefully
- [ ] API endpoints tested with real data
- [ ] Responsive design works on mobile
- [ ] Accessibility (ARIA labels, keyboard navigation)

---

## 🔗 Related Documentation

- [Full API Documentation](./API_DOCUMENTATION.md)
- [Backend README](./README.md)
- [Database Schema](./MODELS.md) *(optional - to be created)*

---

**Last Updated:** January 20, 2026
