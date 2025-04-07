import os
import sys
import argparse

# Detectar si estamos en entorno local y configurar el entorno si es necesario
is_local_env = False
if os.path.exists('/proc/version'):
    with open('/proc/version', 'r') as f:
        if 'Microsoft' in f.read():  # Detectar WSL
            # Configurar el PYTHONPATH para que las importaciones relativas funcionen
            try:
                project_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.join(project_dir, 'backend')
                
                # Solo añadir estos directorios si no están ya en el PYTHONPATH
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                if project_dir not in sys.path:
                    sys.path.insert(0, project_dir)
                    
                is_local_env = True
                print("Entorno de desarrollo local configurado correctamente para inicialización.")
            except Exception as e:
                print(f"Error al configurar entorno local: {str(e)}")

from backend.database.init_db import init_db
from backend.database.connection import SessionLocal
from backend.models.models import User
from backend.auth.utils import get_password_hash
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def initialize_database():
    """Inicializa la base de datos creando todas las tablas necesarias."""
    print("Inicializando base de datos...")
    init_db()
    print("Base de datos inicializada correctamente.")

def create_user(username, email, password, is_admin=False):
    """Crea un nuevo usuario en la base de datos."""
    db = SessionLocal()
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"ADVERTENCIA: Ya existe un usuario con el username '{username}' o email '{email}'")
            return False
        
        # Crear el usuario
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        # Guardar en la base de datos
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"Usuario '{username}' creado exitosamente.")
        return True
    except Exception as e:
        print(f"Error al crear el usuario: {str(e)}")
        return False
    finally:
        db.close()

def create_jwt_secret():
    """Crea una clave secreta JWT si no existe en las variables de entorno."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Verificar si el archivo .env existe
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
        
        # Verificar si ya existe JWT_SECRET_KEY
        if 'JWT_SECRET_KEY' in env_content:
            print("La clave JWT_SECRET_KEY ya existe en el archivo .env")
            return
    
    # Generar una nueva clave secreta
    import secrets
    jwt_secret = secrets.token_hex(32)
    
    # Agregar la clave al archivo .env
    with open(env_path, 'a') as f:
        f.write(f"\n# Clave para la generación de tokens JWT\nJWT_SECRET_KEY={jwt_secret}\n")
    
    print("Clave JWT_SECRET_KEY generada y agregada al archivo .env")

def main():
    parser = argparse.ArgumentParser(description='Inicializa la aplicación de transcripción')
    parser.add_argument('--create-user', action='store_true', help='Crear un usuario de prueba')
    parser.add_argument('--username', default='admin', help='Nombre de usuario (default: admin)')
    parser.add_argument('--email', default='admin@example.com', help='Email del usuario (default: admin@example.com)')
    parser.add_argument('--password', default='admin123', help='Contraseña del usuario (default: admin123)')
    
    args = parser.parse_args()
    
    # Inicializar base de datos
    initialize_database()
    
    # Crear clave JWT si no existe
    create_jwt_secret()
    
    # Crear usuario si se especificó
    if args.create_user:
        create_user(args.username, args.email, args.password)

if __name__ == "__main__":
    main()
