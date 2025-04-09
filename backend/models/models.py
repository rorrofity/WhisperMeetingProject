from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Float, Table, JSON, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList

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

def generate_uuid():
    """Genera un UUID para usar como clave primaria."""
    return str(uuid.uuid4())

# Tabla de asociación para la relación many-to-many entre highlights y tags
highlight_tags = Table(
    "highlight_tags",
    Base.metadata,
    Column("highlight_id", String, ForeignKey("highlights.id"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    """Modelo para almacenar información de usuarios."""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    transcriptions = relationship("Transcription", back_populates="owner")
    projects = relationship("Project", back_populates="owner")
    highlights = relationship("Highlight", back_populates="owner")
    tags = relationship("Tag", back_populates="owner")

class Project(Base):
    """Modelo para organizar transcripciones en proyectos."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(String, ForeignKey("users.id"))
    
    # Relaciones
    owner = relationship("User", back_populates="projects")
    transcriptions = relationship("Transcription", back_populates="project")

class Transcription(Base):
    """Modelo para almacenar transcripciones."""
    __tablename__ = "transcriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String)
    original_filename = Column(String)
    audio_path = Column(String)
    status = Column(String, default="completed")
    transcription = Column(Text)
    short_summary = Column(Text, nullable=True)
    key_points = Column(MutableList.as_mutable(JSON), default=list)
    action_items = Column(MutableList.as_mutable(JSON), default=list)
    utterances_json = Column(JSON, nullable=True)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(String, ForeignKey("users.id"))
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    
    # Relaciones
    owner = relationship("User", back_populates="transcriptions")
    project = relationship("Project", back_populates="transcriptions")
    highlights = relationship("Highlight", back_populates="transcription")
    
    # Propiedades para compatibilidad con el código existente
    @property
    def content(self):
        """Compatibilidad con el nombre de campo antiguo 'content'."""
        return self.transcription
    
    @content.setter
    def content(self, value):
        """Setter para mantener compatibilidad con el nombre de campo antiguo 'content'."""
        self.transcription = value
    
    @property
    def file_path(self):
        """Compatibilidad con el nombre de campo antiguo 'file_path'."""
        return self.audio_path
    
    @file_path.setter
    def file_path(self, value):
        """Setter para mantener compatibilidad con el nombre de campo antiguo 'file_path'."""
        self.audio_path = value

class Highlight(Base):
    """Modelo para almacenar fragmentos destacados de transcripciones."""
    __tablename__ = "highlights"

    id = Column(String, primary_key=True, default=generate_uuid)
    text = Column(Text)
    start_time = Column(Float)
    end_time = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    transcription_id = Column(String, ForeignKey("transcriptions.id"))
    user_id = Column(String, ForeignKey("users.id"))
    
    # Relaciones
    transcription = relationship("Transcription", back_populates="highlights")
    owner = relationship("User", back_populates="highlights")
    tags = relationship("Tag", secondary=highlight_tags, back_populates="highlights")

class Tag(Base):
    """Modelo para almacenar etiquetas para los fragmentos destacados."""
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, index=True)
    color = Column(String, default="#3498db")  # Color por defecto (azul)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, ForeignKey("users.id"))
    
    # Relaciones
    owner = relationship("User", back_populates="tags")
    highlights = relationship("Highlight", secondary=highlight_tags, back_populates="tags")
