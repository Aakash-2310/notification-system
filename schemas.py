from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class NotificationOut(BaseModel):
    id: int
    message: str
    is_read: bool

    class Config:
        from_attributes = True
