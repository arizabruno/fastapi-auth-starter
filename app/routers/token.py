from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth.logic import authenticate_user, create_access_token
from dotenv import load_dotenv
import os
from app.schemas.token import Token
from datetime import datetime, timedelta, timezone
from app.db.users.access import UsersRepository
from app.db.users.models import UserPublic, UserCreate, UserUpdate
from app.db.repositories import get_users_repository

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), users_repo: UsersRepository = Depends(get_users_repository)) -> Token:
    user = authenticate_user(form_data.username, form_data.password, users_repo)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires =  timedelta(days=1)
    access_token = create_access_token(
        data={"user":{"user_id":user.user_id, "username":user.username, "email":user.email, "roles":user.roles}}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
