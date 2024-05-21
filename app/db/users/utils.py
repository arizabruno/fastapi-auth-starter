from app.db.users.models import User, UserPublic


###################################################
# Conversion Functions
###################################################

def convert_to_user_public(user: User) -> UserPublic:
    return UserPublic(
        user_id=user.user_id,
        email=user.email,
        username=user.username,
        created_at=user.created_at.isoformat(),
        roles=user.roles
    )
