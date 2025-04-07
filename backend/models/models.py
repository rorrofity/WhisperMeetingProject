from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Manejar diferentes formatos de importación para compatibilidad entre entornos
try:
    # Primero intentamos importación relativa (servidor)
    from database.connection import Base
except ModuleNotFoundError:
    try:
        # Segundo intento: importación absoluta desde backend (local)
        from backend.database.connection import Base
    except ModuleNotFoundError:
        # Tercer intento: importación relativa diferente (por si acaso)
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from backend.database.connection import Base

class User(Base):
    """Modelo para almacenar información de usuarios."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con las transcripciones
    transcriptions = relationship("Transcription", back_populates="owner")

class Transcription(Base):
    """Modelo para almacenar transcripciones."""
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    original_filename = Column(String)
    file_path = Column(String)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relación con el usuario
    owner = relationship("User", back_populates="transcriptions")
