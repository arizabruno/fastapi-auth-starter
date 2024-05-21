from http.client import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

RESET_PASSWORD_SECRET_KEY = os.getenv("RESET_PASSWORD_SECRET_KEY")
RESET_PASSWORD_SECRET_KEY_ALGORITHM = os.getenv("RESET_PASSWORD_SECRET_KEY_ALGORITHM")

def create_reset_password_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, RESET_PASSWORD_SECRET_KEY, algorithm=RESET_PASSWORD_SECRET_KEY_ALGORITHM)
    return encoded_jwt

def get_user_id_from_reset_password_token(token: str):
    try:
        payload = jwt.decode(token, RESET_PASSWORD_SECRET_KEY, algorithms=[RESET_PASSWORD_SECRET_KEY_ALGORITHM])
        user_id: int = payload.get("user_id")
        return user_id
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
