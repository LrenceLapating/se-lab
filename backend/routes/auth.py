from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid
from typing import Optional

# Import from main app - update to absolute imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import (
    get_db_connection,
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(tags=["authentication"])

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    full_name: str
    email: str
    role: str
    requires_approval: bool
    is_approved: bool
    is_active: bool

class UserSignUp(BaseModel):
    id: str
    full_name: str
    email: str
    password: str
    role: str

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn = Depends(get_db_connection)
):
    print(f"LOGIN ATTEMPT: Username: {form_data.username}")
    
    # First, check if user exists in the database
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s", 
            (form_data.username, form_data.username)
        )
        db_user = cursor.fetchone()
    
    if db_user:
        print(f"User found in DB: {db_user['id']}, {db_user['email']}")
        print(f"User status: is_approved={db_user.get('is_approved', 'Not set')}, requires_approval={db_user.get('requires_approval', 'Not set')}, is_active={db_user.get('is_active', 'Not set')}")
    else:
        print(f"User not found in database: {form_data.username}")
    
    user = authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        print(f"Authentication failed: Incorrect username or password for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Authentication successful for {user.id}, checking approval status")
    print(f"User status after auth: is_approved={user.is_approved}, requires_approval={user.requires_approval}, is_active={user.is_active}")
    
    # If the user requires approval and is not approved yet
    if user.requires_approval and not user.is_approved:
        print(f"APPROVAL FAILURE: User {user.id} requires approval but is not approved yet")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval by an administrator",
        )
    
    # If the user account has been deactivated
    if not user.is_active:
        print(f"ACTIVATION FAILURE: User {user.id} account is deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator.",
        )
    
    # All checks passed, generate token
    print(f"All checks PASSED for {user.id}, generating token")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "requires_approval": user.requires_approval,
        "is_approved": user.is_approved,
        "is_active": user.is_active
    }

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserSignUp, request: Request, conn = Depends(get_db_connection)):
    # Check if user with this ID or email already exists
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s",
            (user_data.id, user_data.email)
        )
        existing_user = cursor.fetchone()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this ID or email already exists"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_data.password)
    
    # Determine if user requires approval based on role
    requires_approval = True
    is_approved = False
    
    # Students don't require approval
    if user_data.role.lower() == 'student':
        requires_approval = False
        is_approved = True
    
    # Insert new user
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users 
                (id, full_name, email, password, role, is_approved, requires_approval, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_data.id,
                    user_data.full_name,
                    user_data.email,
                    hashed_password,
                    user_data.role,
                    is_approved,
                    requires_approval,
                    True  # Set is_active to True for all new users
                )
            )
            
            # Log the signup event
            client_ip = request.client.host if request.client else "unknown"
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address) 
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_data.id,
                    "SIGNUP",
                    f"User signed up with role: {user_data.role}", 
                    client_ip
                )
            )
            
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )
    
    return {
        "message": "User registered successfully",
        "requires_approval": requires_approval,
        "is_approved": is_approved
    }

class LoginRequest(BaseModel):
    id_or_email: str
    password: str

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    conn = Depends(get_db_connection)
):
    print(f"LOGIN ATTEMPT via /login endpoint: Username: {login_data.id_or_email}")
    
    # First, check if user exists in the database
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s OR email = %s", 
            (login_data.id_or_email, login_data.id_or_email)
        )
        db_user = cursor.fetchone()
    
    if db_user:
        print(f"User found in DB: {db_user['id']}, {db_user['email']}")
        print(f"User status: is_approved={db_user.get('is_approved', 'Not set')}, requires_approval={db_user.get('requires_approval', 'Not set')}, is_active={db_user.get('is_active', 'Not set')}")
    else:
        print(f"User not found in database: {login_data.id_or_email}")
    
    user = authenticate_user(conn, login_data.id_or_email, login_data.password)
    if not user:
        print(f"Authentication failed: Incorrect username or password for {login_data.id_or_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Authentication successful for {user.id}, checking approval status")
    print(f"User status after auth: is_approved={user.is_approved}, requires_approval={user.requires_approval}, is_active={user.is_active}")
    
    # If the user requires approval and is not approved yet
    if user.requires_approval and not user.is_approved:
        print(f"APPROVAL FAILURE: User {user.id} requires approval but is not approved yet")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval by an administrator",
        )
    
    # If the user account has been deactivated
    if not user.is_active:
        print(f"ACTIVATION FAILURE: User {user.id} account is deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact an administrator.",
        )
    
    # All checks passed, generate token
    print(f"All checks PASSED for {user.id}, generating token")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "requires_approval": user.requires_approval,
        "is_approved": user.is_approved,
        "is_active": user.is_active
    } 