# Admin User Authentication Setup

## Overview
Persistent admin authentication system for The Gatekeeper.

## Features
- Secure password hashing (bcrypt)
- Session management
- Token-based authentication
- Role-based access control

## Setup

### 1. Create Admin User
```python
from admin_auth import create_admin_user

create_admin_user(
    username="admin",
    email="admin@example.com",
    password="your_secure_password"
)
```

### 2. Configuration
```python
# config/auth_config.py
AUTH_CONFIG = {
    "session_timeout": 3600,  # 1 hour
    "max_login_attempts": 5,
    "lockout_duration": 900,  # 15 minutes
    "token_expiry": 86400,  # 24 hours
}
```

### 3. Usage
```python
from admin_auth import authenticate, requires_auth

# Login
token = authenticate(username, password)

# Protected route
@requires_auth
def admin_dashboard():
    return "Admin Dashboard"
```

## Security Features
- Password hashing with bcrypt
- Rate limiting on login attempts
- Automatic session expiry
- Audit logging
- 2FA support (optional)

## Best Practices
- Use strong passwords (16+ characters)
- Enable 2FA for admin accounts
- Rotate tokens regularly
- Monitor authentication logs
- Implement IP whitelist for admin access
