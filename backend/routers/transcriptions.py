from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.connection import get_db
from backend.models.models import Transcription, User
from backend.models.schemas import Transcription as TranscriptionSchema, TranscriptionCreate
from backend.auth.jwt import get_current_active_user

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
    transcriptions = db.query(Transcription).filter(
        Transcription.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return transcriptions

@router.get("/{transcription_id}", response_model=TranscriptionSchema)
def get_transcription(
    transcription_id: int,
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
        file_path=transcription.file_path,
        content=transcription.content,
        user_id=current_user.id
    )
    
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)
    
    return db_transcription

@router.delete("/{transcription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transcription(
    transcription_id: int,
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
