from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Esquemas para Usuario
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# Esquemas para Transcripción
class TranscriptionBase(BaseModel):
    title: Optional[str] = None
    original_filename: Optional[str] = None

class TranscriptionCreate(TranscriptionBase):
    content: str
    file_path: str

class Transcription(TranscriptionBase):
    id: int
    content: str
    file_path: str
    created_at: datetime
    user_id: int
    
    class Config:
        orm_mode = True

# Esquemas para Token de autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
