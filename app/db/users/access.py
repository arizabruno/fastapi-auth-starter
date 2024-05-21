from app.auth.password import get_password_hash
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.users.models import User, UserPublic, UserCreate, UserUpdate
from app.db.users.utils import convert_to_user_public

###################################################
# Users Repository Class
###################################################

class UsersRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserPublic]:
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [convert_to_user_public(user) for user in users]

    def create_user(self, user: UserCreate) -> UserPublic:
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=get_password_hash(user.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return convert_to_user_public(db_user)

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserPublic]:
        db_user = self.get_user(user_id)
        if db_user is None:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'password' and value is not None:
                db_user.hashed_password = get_password_hash(value)
            elif key == "roles":
                continue
            else:
                setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)
        return convert_to_user_public(db_user)

    def delete_user(self, user_id: int) -> Optional[UserPublic]:
        db_user = self.get_user(user_id)
        if db_user is None:
            return None
        self.db.delete(db_user)
        self.db.commit()
        return convert_to_user_public(db_user)

    def get_user_public(self, user_id: int) -> Optional[UserPublic]:
        db_user = self.get_user(user_id)
        if db_user is None:
            return None
        return convert_to_user_public(db_user)

    def get_user_public_by_username(self, username: str) -> Optional[UserPublic]:
        db_user = self.get_user_by_username(username)
        if db_user is None:
            return None
        return convert_to_user_public(db_user)

    def update_user_roles(self, user_id: int, new_roles: str) -> Optional[UserPublic]:
        db_user = self.get_user(user_id)
        if db_user is None:
            return None
        db_user.roles = new_roles
        self.db.commit()
        self.db.refresh(db_user)
        return convert_to_user_public(db_user)
