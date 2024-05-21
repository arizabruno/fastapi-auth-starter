from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from app.schemas.token import TokenData
from app.db.users.access import UsersRepository
from app.db.users.models import User, UserPublic, UserUpdate
from app.db.repositories import get_users_repository
from app.auth.password import get_password_hash, oauth2_scheme, verify_password
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def authenticate_user(username: str, password: str, users_repo: UsersRepository) -> Optional[UserPublic]:
    user = users_repo.get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_reset_password_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

async def get_current_user(token: str = Depends(oauth2_scheme), users_repo: UsersRepository = Depends(get_users_repository)) -> UserPublic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user")["user_id"]
        username: str = payload.get("user")["username"]
        if user_id is None or username is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id, username=username)
    except JWTError as error:
        print("JWT Error", error)
        raise credentials_exception

    print("Token Data", token_data)
    user = users_repo.get_user_public(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

def update_user(user_id: int, email: str, username: str, password: str, users_repo: UsersRepository) -> Optional[str]:
    update_user = UserUpdate(email=email, username=username, password=password)
    user = users_repo.update_user(user_id, update_user)

    if user is None:
        return None

    access_token_expires = timedelta(days=1)
    access_token = create_access_token(
        data={"user": {"user_id": user.user_id, "username": user.username, "email": user.email, "roles": user.roles}}, expires_delta=access_token_expires
    )

    return access_token

def update_user_password(user_id:int, password: str, users_repo: UsersRepository) -> Optional[UserPublic]:
    user_update = UserUpdate(password=password)
    update_result = users_repo.update_user(user_id, user_update)
    return update_result
