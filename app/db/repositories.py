from app.db.config import get_db
from app.db.users.access import UsersRepository

def get_users_repository() -> UsersRepository:
    db = next(get_db())
    try:
        return UsersRepository(db)
    finally:
        db.close()
