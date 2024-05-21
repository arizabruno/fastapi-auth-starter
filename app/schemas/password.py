from pydantic import BaseModel

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str
