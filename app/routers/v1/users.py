from typing import List
from app.schemas.password import PasswordResetRequest
from app.utils.email_service import send_email
from app.utils.reset_password import create_reset_password_token, get_user_id_from_reset_password_token
from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth.logic import get_current_user, update_user, update_user_password
from dotenv import load_dotenv
import os
from app.db.users.access import UsersRepository
from app.db.users.models import UserPublic, UserCreate, UserUpdate
from app.db.repositories import get_users_repository
from app.schemas.token import Token
from datetime import datetime, timedelta, timezone

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
TEST_SES_RECIPIENT = os.getenv("TEST_SES_RECIPIENT")

RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_PASSWORD_TOKEN_EXPIRE_MINUTES", 15))
FRONTEND_RESET_PASSWORD_URL = os.getenv("FRONTEND_RESET_PASSWORD_URL")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/", response_description="Create a new user", response_model=UserPublic)
async def create_user_endpoint(
    user: UserCreate,
    users_repo: UsersRepository = Depends(get_users_repository)
):
    newUser = UserCreate(email=user.email, username=user.username, password=user.password)
    result = users_repo.create_user(newUser)
    if not result:
        raise HTTPException(status_code=400, detail="User could not be created.")
    return result

@router.get("/", response_description="Read all users", response_model=List[UserPublic])
async def read_all_users_endpoint(
    users_repo: UsersRepository = Depends(get_users_repository)
):
    users = users_repo.get_users()
    if users is None:
        raise HTTPException(status_code=404, detail="No users found.")
    return users

@router.get("/{user_id}", response_description="Read a user by ID", response_model=UserPublic)
async def read_user_by_id_endpoint(
    user_id: int,
    token: str = Depends(oauth2_scheme),
    users_repo: UsersRepository = Depends(get_users_repository)
):
    user = users_repo.get_user_public(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.put("", response_description="Update a user's information")
async def update_user_info_endpoint(
    user: UserUpdate,
    current_user: UserPublic = Depends(get_current_user),
    users_repo: UsersRepository = Depends(get_users_repository)
):
    updated_token = update_user(current_user.user_id, user.email or current_user.email, user.username or current_user.username, user.password, users_repo)
    if updated_token is None:
        raise HTTPException(status_code=400, detail="User update failed.")
    else:
        return Token(access_token=updated_token, token_type="bearer")

@router.delete("/{user_id}", response_description="Delete a user", response_model=UserPublic)
async def delete_user_endpoint(
    user_id: int,
    token: str = Depends(oauth2_scheme),
    users_repo: UsersRepository = Depends(get_users_repository)
):
    success = users_repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=400, detail="User deletion failed.")
    return success


@router.post("/request-password-reset", response_description="Request password reset")
async def request_password_reset(
    email: str,
    background_tasks: BackgroundTasks,
    users_repo: UsersRepository = Depends(get_users_repository)
):
    # Verify if the email exists
    user = users_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a reset token
    expires_delta = timedelta(minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)
    token = create_reset_password_token(data={"user_id": user.user_id}, expires_delta=expires_delta)

    # Construct reset URL
    reset_url = f"{FRONTEND_RESET_PASSWORD_URL}?token={token}"

    email_content = """
    Click the link below to reset your password:
    {url}
    """

    # Send the reset email
    background_tasks.add_task(send_email, recipient=email, subject="Reset Password", body_text=email_content.format(url=reset_url))

    return {"msg": "Password reset email sent"}


@router.post("/reset-password", response_description="Reset password")
async def reset_password(
    request: PasswordResetRequest,
    users_repo: UsersRepository = Depends(get_users_repository)
):
    # Decode the JWT token
    user_id = get_user_id_from_reset_password_token(request.token)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid token")


    # Retrieve user by user_id
    user = users_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = update_user_password(user_id, request.new_password, users_repo)

    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to reset password")
    print("User Password Updated", updated_user)
    return {"msg": "Password successfully reset"}

@router.post("Test AWS SES", response_description="Sendtest email")
async def send_reset_password_email_endpoint(email: str):
    send_email(email, "Namex Test Email", "Email content here...")
    return {"message": "Email sent."}
