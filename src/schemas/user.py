from pydantic import BaseModel, Field, EmailStr


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserSchema(LoginUserSchema):
    id: str
    name: str = Field(min_length=3, max_length=50)