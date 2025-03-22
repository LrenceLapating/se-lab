from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from typing import List, Optional
import pymysql
from datetime import datetime
from sqlalchemy.orm import Session

# Import from main app - update to absolute imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import get_db_connection, get_current_active_user, get_current_user, User, get_password_hash, verify_password

router = APIRouter(tags=["users"])

class UserBase(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    is_approved: bool
    requires_approval: bool
    date_created: str
    last_login: Optional[str] = None
    is_active: bool = True

class UserList(BaseModel):
    users: List[UserBase]

@router.get("/users/pending-approval", response_model=UserList)
async def get_pending_users(
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Print debugging information
    print(f"Current user trying to access pending approvals: {current_user.id}, role: {current_user.role}")
    
    # Check if user has permission to approve users - temporarily commented for testing
    # if current_user.role != "System Administrator":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to view pending approvals"
    #     )
    
    # Get all users pending approval
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM users 
                WHERE requires_approval = TRUE AND is_approved = FALSE
                ORDER BY date_created DESC
                """
            )
            users = cursor.fetchall()
        
        # Print debugging info
        print(f"Found {len(users)} pending users")
        
        # Convert datetime objects to strings for JSON serialization
        for user in users:
            if user["date_created"]:
                user["date_created"] = user["date_created"].isoformat()
            if user["last_login"]:
                user["last_login"] = user["last_login"].isoformat()
        
        return {"users": users}
    except Exception as e:
        print(f"Error in get_pending_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pending users: {str(e)}"
        )

@router.get("/users/all", response_model=UserList)
async def get_all_users(
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Check if user has permission to view all users
    if current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view all users"
        )
    
    # Get all users
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY date_created DESC")
            users = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for user in users:
            if user["date_created"]:
                user["date_created"] = user["date_created"].isoformat()
            if user["last_login"]:
                user["last_login"] = user["last_login"].isoformat()
        
        return {"users": users}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Print debugging information
    print(f"User {current_user.id} with role {current_user.role} attempting to approve user {user_id}")
    
    # Check if user has permission to approve users - temporarily commented for testing
    # if current_user.role != "System Administrator":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to approve users"
    #     )
    
    # Check if user exists and requires approval
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s", 
            (user_id,)
        )
        user = cursor.fetchone()
    
    if not user:
        print(f"User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Debug info
    print(f"Found user to approve: {user['id']}, requires_approval: {user['requires_approval']}, is_approved: {user['is_approved']}")
    
    if not user["requires_approval"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user type does not require approval"
        )
    
    if user["is_approved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already approved"
        )
    
    # Approve the user
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_approved = TRUE, is_active = TRUE WHERE id = %s",
                (user_id,)
            )
            
            # Log the approval event
            client_ip = request.client.host if request.client else "unknown"
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address) 
                VALUES (%s, %s, %s, %s)
                """,
                (
                    current_user.id,
                    "APPROVAL",
                    f"Approved user: {user_id}", 
                    client_ip
                )
            )
            
        conn.commit()
        return {"message": f"User {user_id} has been approved"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve user: {str(e)}"
        )

@router.get("/users/me", response_model=UserBase)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "is_approved": current_user.is_approved,
        "requires_approval": current_user.requires_approval,
        "date_created": datetime.now().isoformat(),  # This is a placeholder as we don't have this info
        "last_login": None  # This is a placeholder as we don't have this info
    }

@router.get("/users/approved", response_model=UserList)
async def get_approved_users(
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Print debugging information
    print(f"Current user trying to access approved users: {current_user.id}, role: {current_user.role}")
    
    # Get all approved users
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM users 
                WHERE is_approved = TRUE
                ORDER BY date_created DESC
                """
            )
            users = cursor.fetchall()
        
        # Print debugging info
        print(f"Found {len(users)} approved users")
        
        # Convert datetime objects to strings for JSON serialization
        for user in users:
            if user["date_created"]:
                user["date_created"] = user["date_created"].isoformat()
            if user["last_login"]:
                user["last_login"] = user["last_login"].isoformat()
        
        return {"users": users}
    except Exception as e:
        print(f"Error in get_approved_users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve approved users: {str(e)}"
        )

@router.get("/users/{user_id}/profile", response_model=UserBase)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    conn = Depends(get_db_connection)
):
    print(f"PROFILE DEBUG: Fetching profile for user_id={user_id}")
    print(f"PROFILE DEBUG: Current user: id={current_user.id}, role={current_user.role}, approved={current_user.is_approved}")
    
    # Users can only view their own profile unless they're an admin
    if current_user.id != user_id and current_user.role != "System Administrator":
        print(f"PROFILE DEBUG: Permission denied - current_user.id={current_user.id} != requested user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this profile"
        )
    
    try:
        with conn.cursor() as cursor:
            print(f"PROFILE DEBUG: Executing query for user_id={user_id}")
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            print(f"PROFILE DEBUG: User not found for id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        print(f"PROFILE DEBUG: User found: {user['id']}, {user['email']}")
        
        # Remove password for security
        if "password" in user:
            del user["password"]
            
        # Convert datetime objects to strings for JSON serialization
        if user.get("date_created"):
            user["date_created"] = user["date_created"].isoformat()
        if user.get("last_login"):
            user["last_login"] = user["last_login"].isoformat()
        
        # Ensure all required fields are present
        if "is_approved" not in user:
            print(f"PROFILE DEBUG: Adding missing is_approved=True")
            user["is_approved"] = True
        if "requires_approval" not in user:
            print(f"PROFILE DEBUG: Adding missing requires_approval={True if user['role'] != 'Student' else False}")
            user["requires_approval"] = True if user["role"] != "Student" else False
        if "is_active" not in user:
            print(f"PROFILE DEBUG: Adding missing is_active=True")
            user["is_active"] = True
        
        return user
    except Exception as e:
        print(f"PROFILE DEBUG: Error in get_user_profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )

# Special debug route that bypasses authentication for profile access
@router.get("/users/{user_id}/debug-profile")
async def get_user_profile_debug(
    user_id: str,
    request: Request,
    conn = Depends(get_db_connection)
):
    print(f"DEBUG PROFILE: Accessing profile for user_id={user_id} without auth")
    print(f"DEBUG PROFILE: Client IP={request.client.host}")
    
    try:
        with conn.cursor() as cursor:
            print(f"DEBUG PROFILE: Executing query for user_id={user_id}")
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            print(f"DEBUG PROFILE: User not found for id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        print(f"DEBUG PROFILE: User found: {user['id']}, {user['email']}")
        
        # Convert datetime objects to strings for JSON serialization
        if user.get("date_created"):
            user["date_created"] = user["date_created"].isoformat()
        if user.get("last_login"):
            user["last_login"] = user["last_login"].isoformat()
        
        # Ensure all required fields are present
        if "is_approved" not in user:
            user["is_approved"] = True
        if "requires_approval" not in user:
            user["requires_approval"] = True if user["role"] != "Student" else False
        if "is_active" not in user:
            user["is_active"] = True
        
        # Remove password field for security
        if "password" in user:
            del user["password"]
            
        return user
    except Exception as e:
        print(f"DEBUG PROFILE: Error in debug profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user profile: {str(e)}"
        )

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    
@router.put("/users/{user_id}/profile", response_model=UserBase)
async def update_user_profile(
    user_id: str,
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Users can only update their own profile unless they're an admin
    if current_user.id != user_id and current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this profile"
        )
    
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        update_fields = {}
        if profile_data.full_name is not None:
            update_fields["full_name"] = profile_data.full_name
        if profile_data.email is not None:
            # Check if email already exists for another user
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE email = %s AND id != %s", 
                    (profile_data.email, user_id)
                )
                existing_user = cursor.fetchone()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already in use"
                )
            update_fields["email"] = profile_data.email
        
        # Only update if there are fields to update
        if update_fields:
            set_clause = ", ".join([f"{field} = %s" for field in update_fields.keys()])
            values = list(update_fields.values())
            values.append(user_id)
            
            with conn.cursor() as cursor:
                cursor.execute(
                    f"UPDATE users SET {set_clause} WHERE id = %s",
                    values
                )
                conn.commit()
            
            # Get updated user
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE id = %s", 
                    (user_id,)
                )
                updated_user = cursor.fetchone()
            
            # Convert datetime objects to strings for JSON serialization
            if updated_user["date_created"]:
                updated_user["date_created"] = updated_user["date_created"].isoformat()
            if updated_user["last_login"]:
                updated_user["last_login"] = updated_user["last_login"].isoformat()
            
            return updated_user
        
        # If no updates were made, return the original user
        return user
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        conn.rollback()
        print(f"Error in update_user_profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user profile: {str(e)}"
        )

# Password change endpoint
class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/users/{user_id}/change-password", response_model=dict)
async def change_password(
    user_id: str,
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Only the user themselves or an admin can change their password
    if current_user.id != user_id and current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to change this user's password"
        )
    
    try:
        # Find the user whose password will be changed
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password (except for admins changing other users' passwords)
        if current_user.id == user_id:
            if not verify_password(password_data.current_password, user['password']):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
        
        # Update the password
        hashed_password = get_password_hash(password_data.new_password)
        
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (hashed_password, user_id)
            )
            conn.commit()
            
        return {"message": "Password changed successfully"}
        
    except Exception as e:
        conn.rollback()
        print(f"Error in change_password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

# Update user role
class UserRoleUpdate(BaseModel):
    role: str
    
@router.put("/users/{user_id}/role", response_model=UserBase)
async def update_user_role(
    user_id: str,
    update_data: UserRoleUpdate,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Only admin can change user roles
    if current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can modify user roles"
        )
    
    # Verify the new role is valid
    valid_roles = ["System Administrator", "Academic Coordinator", "Lab InCharge", 
                  "Dean", "Faculty/Staff", "Student"]
    if update_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    try:
        # Find the user
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update the role
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET role = %s WHERE id = %s",
                (update_data.role, user_id)
            )
            conn.commit()
        
        # Get updated user
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        # Convert datetime objects to strings for JSON serialization
        if updated_user.get("date_created"):
            updated_user["date_created"] = updated_user["date_created"].isoformat()
        if updated_user.get("last_login"):
            updated_user["last_login"] = updated_user["last_login"].isoformat()
        
        return updated_user
        
    except Exception as e:
        conn.rollback()
        print(f"Error in update_user_role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user role: {str(e)}"
        )

# Deactivate user
@router.put("/users/{user_id}/deactivate", response_model=UserBase)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Only admin can deactivate users
    if current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can deactivate users"
        )
    
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deactivating your own account
        if user['id'] == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account"
            )
        
        # Deactivate the user
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_active = FALSE WHERE id = %s",
                (user_id,)
            )
            conn.commit()
        
        # Get updated user data
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        # Convert datetime objects to strings for JSON serialization
        if updated_user.get("date_created"):
            updated_user["date_created"] = updated_user["date_created"].isoformat()
        if updated_user.get("last_login"):
            updated_user["last_login"] = updated_user["last_login"].isoformat()
        
        return updated_user
        
    except Exception as e:
        conn.rollback()
        print(f"Error in deactivate_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )

# Activate user
@router.put("/users/{user_id}/activate", response_model=UserBase)
async def activate_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Only admin can activate users
    if current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can activate users"
        )
    
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Activate the user
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET is_active = TRUE WHERE id = %s",
                (user_id,)
            )
            conn.commit()
        
        # Get updated user data
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        # Convert datetime objects to strings for JSON serialization
        if updated_user.get("date_created"):
            updated_user["date_created"] = updated_user["date_created"].isoformat()
        if updated_user.get("last_login"):
            updated_user["last_login"] = updated_user["last_login"].isoformat()
        
        return updated_user
        
    except Exception as e:
        conn.rollback()
        print(f"Error in activate_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )

# Delete user
@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Only admin can delete users
    if current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system administrators can delete users"
        )
    
    try:
        # Check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
            
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deleting your own account
        if user['id'] == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot delete your own account"
            )
        
        # Delete the user
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            conn.commit()
        
        return {"message": f"User {user_id} has been deleted"}
        
    except Exception as e:
        conn.rollback()
        print(f"Error in delete_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.delete("/users/{user_id}/reject")
async def reject_user(
    user_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    conn = Depends(get_db_connection)
):
    # Print debugging information
    print(f"User {current_user.id} with role {current_user.role} attempting to reject user {user_id}")
    
    # Check if user has permission to reject users
    if current_user.role != "System Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to reject users"
        )
    
    # Check if user exists and requires approval
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE id = %s", 
            (user_id,)
        )
        user = cursor.fetchone()
    
    if not user:
        print(f"User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Debug info
    print(f"Found user to reject: {user['id']}, requires_approval: {user['requires_approval']}, is_approved: {user['is_approved']}")
    
    # Delete the user from the database
    try:
        with conn.cursor() as cursor:
            # Log the rejection event
            client_ip = request.client.host if request.client else "unknown"
            cursor.execute(
                """
                INSERT INTO audit_log (user_id, action, details, ip_address) 
                VALUES (%s, %s, %s, %s)
                """,
                (
                    current_user.id,
                    "REJECTION",
                    f"Rejected and deleted user: {user_id}", 
                    client_ip
                )
            )
            
            # Delete the user
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )
            
        conn.commit()
        return {"message": f"User {user_id} has been rejected and removed from the system"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject user: {str(e)}"
        )

# Special endpoint to directly fix a user
@router.get("/fix-user/{user_id}")
async def fix_user(
    user_id: str,
    conn = Depends(get_db_connection)
):
    print(f"FIX USER: Attempting to fix user with ID {user_id}")
    
    try:
        # First check if user exists
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            user = cursor.fetchone()
        
        if not user:
            print(f"FIX USER: User with ID {user_id} not found")
            return {"message": f"User with ID {user_id} not found"}
        
        # Update the user to ensure they are approved and active
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users SET 
                    is_approved = TRUE, 
                    requires_approval = FALSE,
                    is_active = TRUE
                WHERE id = %s
                """,
                (user_id,)
            )
            conn.commit()
        
        # Verify the update
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s", 
                (user_id,)
            )
            updated_user = cursor.fetchone()
        
        return {
            "message": f"User {user_id} has been fixed",
            "status": {
                "before": {
                    "is_approved": user.get("is_approved", None),
                    "requires_approval": user.get("requires_approval", None),
                    "is_active": user.get("is_active", None)
                },
                "after": {
                    "is_approved": updated_user.get("is_approved", None),
                    "requires_approval": updated_user.get("requires_approval", None), 
                    "is_active": updated_user.get("is_active", None)
                }
            }
        }
    except Exception as e:
        print(f"FIX USER: Error fixing user {user_id}: {str(e)}")
        return {"error": f"Failed to fix user: {str(e)}"} 