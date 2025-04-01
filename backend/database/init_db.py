from connection import engine, Base
from ..models.models import User, Transcription

def init_db():
    """Inicializa la base de datos creando todas las tablas definidas."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creando tablas en la base de datos...")
    init_db()
    print("¡Base de datos inicializada correctamente!")
