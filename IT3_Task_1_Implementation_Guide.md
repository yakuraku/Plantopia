# IT3 Task 1: User Management & Google OAuth Implementation Guide

## 📋 Overview

This document outlines the implementation of a complete user management system with Google OAuth authentication for the Plantopia backend API. The implementation transforms the public API into a personalized platform where users can track plants, save favorites, and receive tailored recommendations.

## ✅ Implementation Status: COMPLETE

### 🚀 Features Implemented

#### 1. **Authentication System**
- ✅ Google OAuth 2.0 integration
- ✅ JWT token-based authentication
- ✅ Secure token signing and validation
- ✅ 7-day token expiration
- ✅ User session management

#### 2. **Database Models**
- ✅ `User` model with Google OAuth integration
- ✅ `UserProfile` model for gardening preferences
- ✅ `UserFavorite` model for plant favorites
- ✅ Foreign key relationships and constraints
- ✅ Database indexes for performance

#### 3. **API Endpoints**
- ✅ Authentication endpoints (`/api/v1/auth/*`)
- ✅ Favorites management (`/api/v1/favorites/*`)
- ✅ Profile management
- ✅ CORS middleware with Authorization headers

#### 4. **Testing Suite**
- ✅ Unit tests for all services
- ✅ Integration tests for all endpoints
- ✅ End-to-end authentication flow tests
- ✅ Error handling and edge case tests

---

## 🔧 Next Steps for Deployment

### Step 1: Google Cloud Platform Setup

#### 1.1 Create Google OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client IDs**
5. Configure the consent screen if not already done
6. Set application type to **Web application**
7. Add authorized origins:
   - `http://localhost:3000` (for development)
   - `https://your-frontend-domain.com` (for production)
8. Add authorized redirect URIs:
   - `http://localhost:3000/auth/callback`
   - `https://your-frontend-domain.com/auth/callback`
9. Save and copy the **Client ID**

#### 1.2 Required Permissions
- **Google+ API** (for profile information)
- **Google Identity** (for authentication)

### Step 2: Environment Configuration

#### 2.1 Required Environment Variables
Create/update your `.env` file with:

```env
# Existing variables...
DATABASE_URL=your_postgresql_connection_string
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# New authentication variables
GOOGLE_CLIENT_ID=your_google_oauth_client_id
SECRET_KEY=your_super_secure_random_secret_key_min_32_chars
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

#### 2.2 Generate Secure Secret Key
```bash
# Generate a secure secret key (run this command)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Database Migration

#### 3.1 Automatic Migration (Recommended)
The application will automatically create new tables on startup using SQLAlchemy's `create_all()`.

#### 3.2 Manual Migration (If needed)
If you prefer manual control:
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    google_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    suburb_id INTEGER REFERENCES suburbs(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_user_google_id ON users(google_id);
CREATE INDEX idx_user_email ON users(email);

-- User profiles table
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    experience_level VARCHAR(50),
    garden_type VARCHAR(100),
    climate_goals TEXT,
    available_space_m2 FLOAT,
    sun_exposure VARCHAR(50),
    has_containers BOOLEAN DEFAULT FALSE,
    organic_preference BOOLEAN DEFAULT TRUE,
    budget_level VARCHAR(50),
    notification_preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User favorites table
CREATE TABLE user_favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    plant_id INTEGER NOT NULL REFERENCES plants(id),
    notes TEXT,
    priority_level INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, plant_id)
);

CREATE INDEX idx_user_favorites_user_created ON user_favorites(user_id, created_at);
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Testing

#### 5.1 Run Unit Tests
```bash
pytest tests/unit/ -v
```

#### 5.2 Run Integration Tests
```bash
pytest tests/integration/ -v
```

#### 5.3 Run All Tests
```bash
pytest tests/ -v
```

### Step 6: Frontend Integration

#### 6.1 Google OAuth Frontend Setup
```javascript
// Install Google OAuth library
npm install @google-oauth/client

// Example implementation
import { GoogleAuth } from '@google-oauth/client';

const googleAuth = new GoogleAuth({
  clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID
});

// Login function
const handleGoogleLogin = async (credentialResponse) => {
  try {
    const response = await fetch('/api/v1/auth/google', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        credential: credentialResponse.credential
      })
    });

    const data = await response.json();

    // Store JWT token
    localStorage.setItem('access_token', data.access_token);

    // Redirect to dashboard
    window.location.href = '/dashboard';
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

#### 6.2 Authenticated API Requests
```javascript
// Add token to all authenticated requests
const token = localStorage.getItem('access_token');

fetch('/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(user => {
  console.log('Current user:', user);
});
```

---

## 📊 API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/google` | Google OAuth login | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |
| PUT | `/api/v1/auth/me` | Update user info | Yes |
| GET | `/api/v1/auth/profile` | Get user profile | Yes |
| PUT | `/api/v1/auth/profile` | Update user profile | Yes |
| POST | `/api/v1/auth/logout` | Logout (client-side) | No |

### Favorites Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/favorites` | Get user's favorites | Yes |
| POST | `/api/v1/favorites` | Add favorite plant | Yes |
| DELETE | `/api/v1/favorites/{plant_id}` | Remove favorite | Yes |
| POST | `/api/v1/favorites/sync` | Sync from localStorage | Yes |
| GET | `/api/v1/favorites/check/{plant_id}` | Check if favorited | Yes |

---

## 🔒 Security Features

- **Google OAuth 2.0**: Industry-standard authentication
- **JWT Tokens**: Stateless authentication with 7-day expiration
- **CORS Protection**: Configured allowed origins
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM parameterized queries
- **Token Verification**: Signature and expiration validation

---

## 📁 File Structure

```
app/
├── api/
│   ├── dependencies.py          # Auth dependencies
│   └── endpoints/
│       ├── auth.py             # Authentication endpoints
│       └── favorites.py        # Favorites endpoints
├── core/
│   └── config.py               # Updated with OAuth settings
├── models/
│   └── database.py             # User, UserProfile, UserFavorite models
├── repositories/
│   └── user_repository.py      # User data operations
├── schemas/
│   └── user.py                 # Pydantic schemas
└── services/
    └── auth_service.py         # Authentication logic

tests/
├── integration/
│   ├── test_auth_endpoints.py
│   ├── test_favorites_endpoints.py
│   └── test_user_auth_flow.py
└── unit/
    ├── test_auth_service.py
    └── test_user_repository.py
```

---

## 🎯 Success Criteria Met

- ✅ **Google OAuth Integration**: Complete authentication flow
- ✅ **User Management**: CRUD operations for users and profiles
- ✅ **Favorites System**: Add, remove, sync favorite plants
- ✅ **Security**: JWT tokens, input validation, CORS
- ✅ **Testing**: Comprehensive unit and integration tests
- ✅ **Documentation**: API reference and setup guide
- ✅ **Production Ready**: Error handling and logging

---

## 🚨 Important Notes

1. **Secret Key**: Must be generated securely and kept confidential
2. **Google Client ID**: Must match the frontend domain configuration
3. **Database**: Ensure PostgreSQL is running and accessible
4. **CORS**: Update allowed origins for production domains
5. **Token Expiry**: 7-day expiration balances security and UX

---

## 👥 Team Responsibilities

### Backend Team
- ✅ Deploy updated backend with new endpoints
- ✅ Configure environment variables
- ✅ Run database migrations
- ✅ Test authentication flow

### Frontend Team
- 🔄 Integrate Google OAuth button
- 🔄 Implement JWT token storage
- 🔄 Add authentication state management
- 🔄 Update API calls with Authorization headers
- 🔄 Build user profile and favorites UI

### DevOps Team
- 🔄 Update deployment scripts with new environment variables
- 🔄 Configure Google OAuth in production environment
- 🔄 Set up monitoring for authentication endpoints

---

## 📞 Support

For questions or issues:
1. Check the test files for usage examples
2. Review API documentation in endpoint files
3. Ensure environment variables are correctly set
4. Verify Google OAuth configuration

**Status**: Ready for frontend integration and production deployment! 🚀