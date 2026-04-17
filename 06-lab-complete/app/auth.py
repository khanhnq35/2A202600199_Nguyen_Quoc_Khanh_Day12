import jwt
import time
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from app.config import settings

# ─────────────────────────────────────────────
# JWT Configuration
# ─────────────────────────────────────────────
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Demo users (In production, replace with Database)
DEMO_USERS = {
    "student": {"password": "demo123", "role": "user"},
    "teacher": {"password": "teach456", "role": "admin"},
}

# ─────────────────────────────────────────────
# JWT Functions
# ─────────────────────────────────────────────
def create_token(username: str, role: str) -> str:
    """Generate a JWT token with an expiry time."""
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Dependency to verify JWT token from Authorization header."""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Use: Authorization: Bearer <token>",
        )

    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[ALGORITHM])
        return {
            "username": payload["sub"],
            "role": payload["role"],
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please login again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token.")

def authenticate_user(username: str, password: str) -> dict:
    """Check credentials and return user info if valid."""
    user = DEMO_USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": username, "role": user["role"]}

# ─────────────────────────────────────────────
# API Key Verification
# ─────────────────────────────────────────────
def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Validate the X-API-Key header."""
    if not api_key or api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-API-Key. Access denied.",
        )
    return api_key
