from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os
import sys

# Manejar diferentes formatos de importación para compatibilidad entre entornos
try:
    # Primero intentamos importación relativa (servidor)
    from database.connection import get_db
    from models.models import Transcription, User
    from models.schemas import Transcription as TranscriptionSchema, TranscriptionCreate
    from auth.jwt import get_current_active_user
except ModuleNotFoundError:
    try:
        # Segundo intento: importación absoluta desde backend (local)
        from backend.database.connection import get_db
        from backend.models.models import Transcription, User
        from backend.models.schemas import Transcription as TranscriptionSchema, TranscriptionCreate
        from backend.auth.jwt import get_current_active_user
    except ModuleNotFoundError:
        # Tercer intento: importación relativa diferente (por si acaso)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.abspath(os.path.join(current_dir, '../..'))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        from backend.database.connection import get_db
        from backend.models.models import Transcription, User
        from backend.models.schemas import Transcription as TranscriptionSchema, TranscriptionCreate
        from backend.auth.jwt import get_current_active_user

router = APIRouter(
    prefix='/transcriptions',
    tags=['transcriptions'],
    responses={404: {'description': 'Not found'}},
)

@router.get('/', response_model=List[TranscriptionSchema])
def get_user_transcriptions(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    "
