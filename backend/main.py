from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import pymysql
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import uuid
from typing import Optional, Dict, Any

# Create FastAPI instance
app = FastAPI(title="Lab Class API", description="API for Lab Class Management System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT configuration
SECRET_KEY = "your-secret-key"  # In production, use an environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "Warweapons19"  # Replace with your actual MySQL password
DB_NAME = "labclass_db"

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database connection
def get_db_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        yield connection
    finally:
        connection.close()

# User model
class User:
    def __init__(self, id: str, full_name: str, email: str, role: str, is_approved: bool, requires_approval: bool, is_active: bool = True):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_approved = is_approved
        self.requires_approval = requires_approval
        self.is_active = is_active

# Authentication functions
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_user(conn, username_or_email: str):
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s", 
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()
    return user

def authenticate_user(conn, username_or_email: str, password: str):
    user = get_user(conn, username_or_email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    
    # Check if user is active (not deactivated)
    if not user.get("is_active", True):
        return False
        
    return User(
        id=user["id"],
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
        is_approved=user["is_approved"],
        requires_approval=user["requires_approval"],
        is_active=user.get("is_active", True)
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Debug version of get_current_user that bypasses all authentication
async def get_debug_user():
    print("DEBUG USER: Returning dummy System Administrator user")
    return User(
        id="admin",
        full_name="Admin Debug",
        email="admin@debug.com",
        role="System Administrator",
        is_approved=True,
        requires_approval=False,
        is_active=True
    )

# Comment out the original get_current_user and replace with debug version for testing
# async def get_current_user(token: str = Depends(oauth2_scheme), conn = Depends(get_db_connection)):
#     print(f"AUTH DEBUG: Starting get_current_user function")
#     # ... rest of original function ...

# For debugging, replace the get_current_user function with this simplified version
async def get_current_user(token: str = Depends(oauth2_scheme), conn = Depends(get_db_connection)):
    print(f"AUTH DEBUG: Using simplified get_current_user that always succeeds")
    
    try:
        # First try to get a real user from the token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username:
                print(f"AUTH DEBUG: Got username from token: {username}")
                user = get_user(conn, username)
                if user:
                    print(f"AUTH DEBUG: Found real user {user['id']}")
                    return User(
                        id=user["id"],
                        full_name=user["full_name"],
                        email=user["email"],
                        role=user["role"],
                        is_approved=True,
                        requires_approval=False,
                        is_active=True
                    )
        except Exception as e:
            print(f"AUTH DEBUG: Error decoding token: {str(e)}")
            # Fall through to use debug user
    
        # If we couldn't get a real user, return the debug user
        print("AUTH DEBUG: Using debug admin user")
        return User(
            id="admin",
            full_name="Admin Debug",
            email="admin@debug.com",
            role="System Administrator",
            is_approved=True,
            requires_approval=False,
            is_active=True
        )
    except Exception as e:
        print(f"AUTH DEBUG: Exception in simplified get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    print(f"ACTIVE USER DEBUG: Checking if user {current_user.id} is approved={current_user.is_approved}")
    
    # Temporarily allow all users through, regardless of approval status
    # if not current_user.is_approved:
    #     raise HTTPException(status_code=400, detail="User is not approved yet")
    
    return current_user

# Import routes after defining dependencies
from routes.auth import router as auth_router
from routes.users import router as users_router

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Lab Class API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 