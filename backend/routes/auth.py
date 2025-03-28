from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import os

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

# Add the password reset request class
class PasswordResetRequest(BaseModel):
    email: str

class VerifyTokenRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Add the forgot password endpoint
@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    request_data: PasswordResetRequest,
    conn = Depends(get_db_connection)
):
    """
    Send a password reset email to the user.
    For this demo, we'll simulate sending an email and return success even if the email is not found.
    This is a security best practice to prevent email enumeration attacks.
    """
    try:
        # Check if the email exists in the database
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (request_data.email,)
            )
            user = cursor.fetchone()
        
        # Generate a reset token, whether or not the user exists
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        
        if user:
            # Store the reset token in the database
            with conn.cursor() as cursor:
                # Check if a reset token already exists for this user
                cursor.execute(
                    "SELECT * FROM password_reset_tokens WHERE user_id = %s",
                    (user["id"],)
                )
                existing_token = cursor.fetchone()
                
                if existing_token:
                    # Update the existing token
                    cursor.execute(
                        """
                        UPDATE password_reset_tokens 
                        SET token = %s, expires_at = %s, created_at = %s
                        WHERE user_id = %s
                        """,
                        (
                            reset_token,
                            reset_token_expiry.isoformat(),
                            datetime.utcnow().isoformat(),
                            user["id"]
                        )
                    )
                else:
                    # Create a new token
                    cursor.execute(
                        """
                        INSERT INTO password_reset_tokens 
                        (user_id, token, expires_at, created_at) 
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            user["id"],
                            reset_token,
                            reset_token_expiry.isoformat(),
                            datetime.utcnow().isoformat()
                        )
                    )
                conn.commit()
            
            # In a real application, send an email here
            # For demo purposes, we'll log what would be sent
            reset_url = f"http://localhost:5173/reset-password?token={reset_token}"
            print(f"[MOCK EMAIL] Password reset link for {request_data.email}: {reset_url}")
            
            # Attempt to send an actual email if configured
            try:
                send_reset_email(request_data.email, reset_url, user["full_name"])
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
        
        # Always return success to prevent email enumeration
        return {
            "message": "If the email exists in our system, a password reset link will be sent.",
            "success": True
        }
    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

def send_reset_email(email, reset_url, name):
    """Helper function to send a password reset email."""
    # If no email configuration exists, just log and return
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    
    if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
        print("Email configuration not found. Would send reset email to:", email)
        return
    
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Request"
        message["From"] = smtp_username
        message["To"] = email
        
        # Plain text version
        text = f"""
        Hello {name},
        
        You recently requested to reset your password. Click the link below to reset it:
        
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        The UIC Lab Class Scheduler Team
        """
        
        # HTML version
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #DD385A; color: white; padding: 10px 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ display: inline-block; background-color: #DD385A; color: white; 
                          padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Password Reset Request</h2>
                </div>
                <div class="content">
                    <p>Hello {name},</p>
                    <p>You recently requested to reset your password. Click the button below to reset it:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p>{reset_url}</p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you did not request a password reset, please ignore this email.</p>
                    <div class="footer">
                        <p>Best regards,<br>The UIC Lab Class Scheduler Team</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, email, message.as_string())
        
        print(f"Password reset email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise 

@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyTokenRequest):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if token exists and is not expired
        cursor.execute("""
            SELECT user_id, expires_at FROM password_reset_tokens 
            WHERE token = %s AND expires_at > NOW()
        """, (request.token,))
        
        result = cursor.fetchone()
        
        if not result:
            # Token doesn't exist or is expired
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid or expired token"}
            )
        
        # Token is valid
        return {"valid": True}
    except Exception as e:
        print(f"Error verifying token: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while verifying the token"}
        )
    finally:
        cursor.close()
        conn.close()

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if token exists and is not expired
        cursor.execute("""
            SELECT user_id, expires_at FROM password_reset_tokens 
            WHERE token = %s AND expires_at > NOW()
        """, (request.token,))
        
        result = cursor.fetchone()
        
        if not result:
            # Token doesn't exist or is expired
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid or expired token"}
            )
        
        user_id = result[0]
        
        # Hash the new password
        hashed_password = get_password_hash(request.new_password)
        
        # Update the user's password
        cursor.execute("""
            UPDATE users SET password = %s WHERE id = %s
        """, (hashed_password, user_id))
        
        # Delete all password reset tokens for this user
        cursor.execute("""
            DELETE FROM password_reset_tokens WHERE user_id = %s
        """, (user_id,))
        
        # Commit the changes
        conn.commit()
        
        return {"message": "Password reset successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Error resetting password: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An error occurred while resetting the password"}
        )
    finally:
        cursor.close()
        conn.close() 