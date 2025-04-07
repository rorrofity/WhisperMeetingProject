"""
Archivo puente para compatibilidad entre entornos local y servidor.
Permite que las importaciones funcionen de manera consistente.
"""

# Re-exportar los módulos desde backend.models.models para que "from models.models import X" funcione
from backend.models.models import User, Transcription
