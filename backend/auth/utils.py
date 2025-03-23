from passlib.context import CryptContext

# Configuración de la encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verifica que la contraseña en texto plano coincida con la contraseña hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera un hash seguro para la contraseña en texto plano."""
    return pwd_context.hash(password)
