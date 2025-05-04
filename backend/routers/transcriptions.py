from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database.connection import get_db
from models.models import Transcription, User
from models.schemas import Transcription as TranscriptionSchema, TranscriptionCreate
from auth.jwt import get_current_active_user

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/transcriptions",
    tags=["transcriptions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[TranscriptionSchema])
def get_user_transcriptions(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene todas las transcripciones del usuario actual."""
    logger.info(f"Usuario {current_user.username} (ID: {current_user.id}) solicitó transcripciones")
    
    # Primero verificamos cuántas transcripciones hay en total en la base de datos
    total_transcriptions = db.query(Transcription).count()
    logger.info(f"Total de transcripciones en la base de datos: {total_transcriptions}")
    
    # Ahora filtramos por el usuario actual
    transcriptions = db.query(Transcription).filter(
        Transcription.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    logger.info(f"Encontradas {len(transcriptions)} transcripciones para el usuario {current_user.username} (ID: {current_user.id})")
    
    # Si no hay transcripciones, verificamos si hay alguna sin usuario asociado
    if len(transcriptions) == 0 and total_transcriptions > 0:
        orphan_transcriptions = db.query(Transcription).filter(
            Transcription.user_id.is_(None)
        ).all()
        logger.info(f"Transcripciones sin usuario asociado: {len(orphan_transcriptions)}")
    
    return transcriptions

@router.get("/{transcription_id}", response_model=TranscriptionSchema)
def get_transcription(
    transcription_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Obtiene una transcripción específica del usuario."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
        Transcription.user_id == current_user.id
    ).first()
    
    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcripción no encontrada"
        )
    
    return transcription

@router.post("/", response_model=TranscriptionSchema)
def create_transcription(
    transcription: TranscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crea una nueva transcripción para el usuario."""
    db_transcription = Transcription(
        title=transcription.title,
        original_filename=transcription.original_filename,
        audio_path=transcription.audio_path,
        transcription=transcription.transcription,
        short_summary=transcription.short_summary,
        key_points=transcription.key_points,
        action_items=transcription.action_items,
        utterances_json=transcription.utterances_json,
        duration=transcription.duration,
        user_id=current_user.id
    )
    
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)
    
    return db_transcription

@router.delete("/{transcription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcription(
    transcription_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Elimina una transcripción del usuario."""
    transcription = db.query(Transcription).filter(
        Transcription.id == transcription_id,
        Transcription.user_id == current_user.id
    ).first()
    
    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcripción no encontrada"
        )
    
    db.delete(transcription)
    db.commit()
    
    return {"status": "success"}
