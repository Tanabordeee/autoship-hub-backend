from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
    name: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    name: str

    class Config:
        from_attributes = True
