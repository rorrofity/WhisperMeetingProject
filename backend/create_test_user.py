from backend.database.init_db import init_db
from backend.database.connection import SessionLocal
from backend.models.models import User
from backend.auth.utils import get_password_hash

def create_test_user(
    username="testuser", 
    email="test@example.com", 
    password="password123"
):
    # Inicializar la base de datos
    init_db()
    
    # Crear la sesión de base de datos
    db = SessionLocal()
    
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"El usuario con username '{username}' o email '{email}' ya existe")
            return
        
        # Crear el usuario de prueba
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        # Agregar a la base de datos
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"Usuario de prueba creado con éxito:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        
    except Exception as e:
        print(f"Error al crear el usuario de prueba: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
