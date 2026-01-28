# API Documentation - SDG Impact Dashboard

## Base URL
```
http://localhost:8000/api
```

## Authentication

### JWT Tokens
All protected endpoints require Bearer token in Authorization header:
```
Authorization: Bearer <access_token>
```

### Token Endpoints

#### Get Token
**POST** `/api/token/`

Request body:
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Refresh Token
**POST** `/api/token/refresh/`

Request body:
```json
{
  "refresh": "<refresh_token>"
}
```

Response (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## SDG Goals (Public)

### List All SDG Goals
**GET** `/api/sdg/`

Query parameters:
- `page` (integer): Page number for pagination
- `limit` (integer): Items per page

Response (200 OK):
```json
[
  {
    "id": 1,
    "number": 1,
    "name": "No Poverty",
    "description": "End poverty in all its forms everywhere.",
    "icon_url": "https://example.com/sdg1.png",
    "created_at": "2026-01-20T10:00:00Z",
    "updated_at": "2026-01-20T10:00:00Z"
  }
]
```

### Get Specific SDG
**GET** `/api/sdg/{number}/`

Parameters:
- `number` (integer, 1-17): SDG number

Response (200 OK):
```json
{
  "id": 1,
  "number": 1,
  "name": "No Poverty",
  "description": "End poverty in all its forms everywhere.",
  "icon_url": "https://example.com/sdg1.png"
}
```

Response (404 Not Found):
```json
{
  "error": "SDG Goal with number 1 not found"
}
```

### Get Activities for SDG
**GET** `/api/sdg/{number}/activities/`

Parameters:
- `number` (integer, 1-17): SDG number

Response (200 OK):
```json
[
  {
    "id": 5,
    "title": "Clean Water Initiative",
    "description": "Project to provide clean water...",
    "activity_type": "project",
    "lead_author": 2,
    "lead_author_detail": {
      "id": 2,
      "username": "jane_smith",
      "email": "jane@university.edu",
      "first_name": "Jane",
      "last_name": "Smith"
    },
    "date_created": "2026-01-15T08:30:00Z",
    "sdg_impacts": [
      {
        "id": 12,
        "sdg_goal": 6,
        "score": 95,
        "justification": "Direct focus on clean water and sanitation..."
      }
    ]
  }
]
```

### Get SDG Summary Statistics
**GET** `/api/sdg/{number}/summary/`

Parameters:
- `number` (integer, 1-17): SDG number

Response (200 OK):
```json
{
  "sdg": {
    "id": 3,
    "number": 3,
    "name": "Good Health and Well-Being",
    "description": "..."
  },
  "statistics": {
    "total_activities": 12,
    "average_score": 78.5,
    "max_score": 95,
    "min_score": 45
  }
}
```

---

## Activities (Protected - Requires Auth)

### List Activities
**GET** `/api/activities/`

**Authentication:** Required

Query parameters:
- `activity_type` (string): Filter by type (research, project, curriculum, outreach)
- `author` (integer): Filter by author user ID
- `ai_classified` (boolean): Filter by classification status
- `page` (integer): Page number

Response (200 OK):
```json
[
  {
    "id": 1,
    "title": "Renewable Energy Research",
    "description": "Study on solar energy efficiency",
    "activity_type": "research",
    "activity_type_display": "Research",
    "lead_author": 1,
    "lead_author_detail": {
      "id": 1,
      "username": "john_doe",
      "email": "john@university.edu"
    },
    "date_created": "2026-01-20T09:15:00Z",
    "ai_classified": true,
    "evidence_file": "/media/evidence/solar_study.pdf"
  }
]
```

### Get Activity Details
**GET** `/api/activities/{id}/`

**Authentication:** Required

Parameters:
- `id` (integer): Activity ID

Response (200 OK):
```json
{
  "id": 1,
  "title": "Renewable Energy Research",
  "description": "Study on solar energy efficiency",
  "activity_type": "research",
  "activity_type_display": "Research",
  "lead_author": 1,
  "lead_author_detail": {
    "id": 1,
    "username": "john_doe",
    "email": "john@university.edu",
    "first_name": "John",
    "last_name": "Doe"
  },
  "date_created": "2026-01-20T09:15:00Z",
  "updated_at": "2026-01-20T09:15:00Z",
  "ai_classified": true,
  "evidence_file": "/media/evidence/solar_study.pdf",
  "sdg_impacts": [
    {
      "id": 1,
      "activity": 1,
      "sdg_goal": 7,
      "sdg_goal_detail": {
        "id": 1,
        "number": 7,
        "name": "Affordable and Clean Energy",
        "description": "..."
      },
      "score": 92,
      "justification": "Directly addresses renewable energy solutions..."
    },
    {
      "id": 2,
      "activity": 1,
      "sdg_goal": 13,
      "sdg_goal_detail": {
        "id": 2,
        "number": 13,
        "name": "Climate Action",
        "description": "..."
      },
      "score": 85,
      "justification": "Contributes to climate change mitigation..."
    }
  ]
}
```

### Create Activity (AI Classification)
**POST** `/api/activities/upload/`

**Authentication:** Required

Request (multipart/form-data):
```
title: "Renewable Energy Research"
description: "Study on solar energy efficiency"
activity_type: "research"
evidence_file: <file> (optional)
```

Response (201 Created):
```json
{
  "id": 2,
  "title": "Renewable Energy Research",
  "description": "Study on solar energy efficiency",
  "activity_type": "research",
  "lead_author": 1,
  "lead_author_detail": {
    "id": 1,
    "username": "john_doe",
    "email": "john@university.edu"
  },
  "date_created": "2026-01-20T10:30:00Z",
  "ai_classified": true,
  "sdg_impacts": [
    {
      "sdg_goal": 7,
      "score": 92,
      "justification": "..."
    }
  ]
}
```

Response (400 Bad Request):
```json
{
  "title": ["This field is required."],
  "description": ["This field is required."],
  "activity_type": ["This field is required."]
}
```

### Update Activity
**PUT** `/api/activities/{id}/`

**Authentication:** Required

Request body:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "activity_type": "project"
}
```

Response (200 OK):
```json
{
  "id": 1,
  "title": "Updated Title",
  ...
}
```

### Delete Activity
**DELETE** `/api/activities/{id}/`

**Authentication:** Required

Response (204 No Content)

### Re-classify Activity
**POST** `/api/activities/{id}/classify/`

**Authentication:** Required

Clears existing impacts and re-runs AI classification.

Response (200 OK):
```json
{
  "id": 1,
  "ai_classified": true,
  "sdg_impacts": [...]
}
```

### Get Your Activities
**GET** `/api/activities/by_author/`

**Authentication:** Required

Response (200 OK):
```json
[
  {
    "id": 1,
    "title": "My Activity",
    ...
  }
]
```

---

## Dashboard & Analytics (Public)

### Dashboard Summary
**GET** `/api/dashboard/summary/`

Response (200 OK):
```json
{
  "total_activities": 45,
  "total_impacts": 128,
  "top_performing_sdg": {
    "sdg_goal__number": 3,
    "sdg_goal__name": "Good Health and Well-Being",
    "avg_score": 87.5,
    "total_impacts": 18
  },
  "activities_by_type": [
    {
      "activity_type": "research",
      "count": 25,
      "avg_score": 82.3
    },
    {
      "activity_type": "project",
      "count": 15,
      "avg_score": 78.9
    }
  ],
  "top_authors": [
    {
      "lead_author__username": "john_doe",
      "lead_author__id": 1,
      "activity_count": 12
    }
  ]
}
```

### Analytics Trends
**GET** `/api/analytics/trends/`

Query parameters:
- `sdg_number` (integer, 1-17): Filter by specific SDG

Response (200 OK):
```json
{
  "trends": [
    {
      "year": 2024,
      "sdg_number": 3,
      "sdg_name": "Good Health and Well-Being",
      "average_score": 82.5,
      "count": 12
    },
    {
      "year": 2025,
      "sdg_number": 3,
      "sdg_name": "Good Health and Well-Being",
      "average_score": 85.2,
      "count": 15
    }
  ],
  "date_range": {
    "start": 2020,
    "end": 2026
  }
}
```

---

## Reports (Public)

### Generate SDG Report (PDF)
**GET** `/api/reports/generate/{sdg_id}/`

Parameters:
- `sdg_id` (integer): SDG ID

Response (200 OK): PDF file download
- Content-Type: `application/pdf`
- Headers include: `Content-Disposition: attachment; filename="SDG_3_Good_Health...Report.pdf"`

### Generate Comprehensive Report (PDF)
**GET** `/api/reports/comprehensive/`

Response (200 OK): PDF file download
- Includes summary of all SDGs with activities
- Content-Type: `application/pdf`

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"],
  "another_field": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "error": "Not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to process request"
}
```

---

## Pagination

List endpoints support pagination:

```
GET /api/activities/?page=2
```

Response includes:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/activities/?page=3",
  "previous": "http://localhost:8000/api/activities/?page=1",
  "results": [...]
}
```

---

## Rate Limiting

No rate limiting currently implemented. Contact DevOps for production configuration.

---

## Versioning

API version: v1 (default)

Future versions: `/api/v2/...`

---

**Last Updated:** January 20, 2026
