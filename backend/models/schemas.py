from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, UUID4
from uuid import uuid4

# Esquemas para Usuario
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Esquemas para Proyecto
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    status: Optional[str] = None

class Project(ProjectBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: str
    
    class Config:
        from_attributes = True

# Esquemas para Transcripción
class TranscriptionBase(BaseModel):
    title: Optional[str] = None
    original_filename: Optional[str] = None
    status: Optional[str] = "completed"
    project_id: Optional[str] = None

class TranscriptionCreate(TranscriptionBase):
    transcription: str
    audio_path: str
    short_summary: Optional[str] = None
    key_points: Optional[List[str]] = []
    action_items: Optional[List[str]] = []
    utterances_json: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None

class TranscriptionUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[str] = None
    short_summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    action_items: Optional[List[str]] = None

class Transcription(TranscriptionBase):
    id: str
    transcription: str
    audio_path: Optional[str] = ""
    short_summary: Optional[str] = None
    key_points: Optional[List[str]] = []
    action_items: Optional[List[str]] = []
    utterances_json: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user_id: str
    
    # Propiedades para compatibilidad con el código existente
    @property
    def content(self) -> str:
        """Compatibilidad con el nombre de campo antiguo 'content'."""
        return self.transcription
    
    @property
    def file_path(self) -> str:
        """Compatibilidad con el nombre de campo antiguo 'file_path'."""
        return self.audio_path
    
    class Config:
        from_attributes = True

# Esquemas para Destacados
class HighlightBase(BaseModel):
    text: str
    start_time: float
    end_time: float
    transcription_id: str

class HighlightCreate(HighlightBase):
    pass

class HighlightUpdate(BaseModel):
    text: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class Highlight(HighlightBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: str
    
    class Config:
        from_attributes = True

# Esquemas para Etiquetas
class TagBase(BaseModel):
    name: str
    color: Optional[str] = "#3498db"
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

class Tag(TagBase):
    id: str
    created_at: datetime
    user_id: str
    
    class Config:
        from_attributes = True

# Esquemas para relaciones
class HighlightWithTags(Highlight):
    tags: List[Tag] = []

class TranscriptionWithHighlights(Transcription):
    highlights: List[Highlight] = []

class ProjectWithTranscriptions(Project):
    transcriptions: List[Transcription] = []

# Esquemas para Token de autenticación
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
