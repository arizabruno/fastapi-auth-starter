from typing import List
from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth.logic import get_current_user, update_user
from dotenv import load_dotenv
import os
from app.db.users.access import UsersRepository
from app.db.users.models import UserPublic, UserCreate, UserUpdate
from app.db.repositories import get_users_repository
from app.schemas.token import Token
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

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
