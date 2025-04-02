from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Obtener la ruta base del proyecto (un nivel arriba de la carpeta backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configuración de la base de datos SQLite
# Se puede sobreescribir con variable de entorno DATABASE_URL
default_db_path = os.path.join(BASE_DIR, "transcriptions.db")
db_url = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")
SQLALCHEMY_DATABASE_URL = db_url

# Crear el motor de base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crear una fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase base para los modelos ORM
Base = declarative_base()

# Función auxiliar para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
