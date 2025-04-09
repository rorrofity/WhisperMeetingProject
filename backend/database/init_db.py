from .connection import engine, Base

# Manejar diferentes formatos de importación para compatibilidad entre entornos
try:
    # Primero intentamos importación relativa (servidor)
    from models.models import User, Transcription, Project, Highlight, Tag
except ModuleNotFoundError:
    try:
        # Segundo intento: importación absoluta desde backend (local)
        from backend.models.models import User, Transcription, Project, Highlight, Tag
    except ModuleNotFoundError:
        # Tercer intento: importación relativa diferente (por si acaso)
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from backend.models.models import User, Transcription, Project, Highlight, Tag

def init_db():
    """Inicializa la base de datos creando todas las tablas definidas."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creando tablas en la base de datos...")
    init_db()
    print("¡Base de datos inicializada correctamente!")
