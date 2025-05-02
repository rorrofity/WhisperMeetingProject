from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import shutil
import tempfile
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import asyncio

# Módulos internos de la aplicación - Modificamos las importaciones para que sean relativas
from utils.audio_processor import AudioProcessor
from utils.transcriber import Transcriber

# Importar nuevos módulos para autenticación y base de datos
from database.connection import get_db, SessionLocal
from database.init_db import init_db
from models.models import User, Transcription as DBTranscription
from auth.jwt import get_current_active_user, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from routers import users, transcriptions
from models.schemas import Token, Transcription as TranscriptionSchema

# Load environment variables with explicit path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Whisper Meeting Transcriber")

# Configurar CORS de la manera más permisiva posible
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de prueba simple
@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba simple para verificar que el servidor está funcionando."""
    return {"status": "ok", "message": "El servidor está funcionando correctamente"}

# Incluir los routers para usuarios y transcripciones
app.include_router(users.router)
app.include_router(transcriptions.router)

# Create directories
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# Initialize processors
audio_processor = AudioProcessor(temp_dir=TEMP_DIR)

# Get the transcription model from environment variables
default_model = os.getenv("TRANSCRIPTION_MODEL", "nova-3")
logger.info(f"Using transcription model: {default_model}")

# Initialize database
init_db()

# Store job status and results
jobs = {}  # type: Dict[str, Dict[str, Any]]

class JobStatus(BaseModel):
    status: str
    error: Optional[str] = None
    job_id: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint to check API status."""
    return {"message": "Whisper Meeting Transcriber API is running"}

@app.post("/upload-file/", response_model=JobStatus)
async def upload_file_simple(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload an audio file for transcription using configured model from .env.
    
    Args:
        file: Audio file to transcribe
        background_tasks: FastAPI BackgroundTasks for async processing
        current_user: Usuario actualmente autenticado
        db: Sesión de base de datos
        
    Returns:
        JSON response with process ID
    """
    # Check file type
    if not file.content_type.startswith(('audio/', 'video/')):
        raise HTTPException(status_code=400, detail="File must be an audio or video file.")
    
    # Generate process ID
    process_id = str(uuid.uuid4())
    logger.info(f"Generando ID de proceso: {process_id}")
    
    # Create directory for this job
    job_dir = TEMP_DIR / process_id
    job_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = job_dir / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Store job info
    jobs[process_id] = {
        "status": "uploaded",
        "file_path": str(file_path),
        "original_filename": file.filename,
        "model_size": default_model,
        "summary_method": "deepseek", # Usar Deepseek para resúmenes
        "user_id": current_user.id  # Asociar con el usuario actual
    }
    
    # Process in background
    if background_tasks:
        background_tasks.add_task(process_audio_file, process_id) # Usar process_audio_file en lugar de process_audio_file_simple
    else:
        # For testing without background tasks
        await process_audio_file(process_id) # Usar process_audio_file en lugar de process_audio_file_simple
        
        # Guardar la transcripción en la base de datos cuando esté completa
        if jobs[process_id]["status"] == "completed":
            # Crear entrada en la base de datos
            db_transcription = DBTranscription(
                title=f"Transcripción de {file.filename}",
                original_filename=file.filename,
                file_path=str(file_path),
                content=jobs[process_id]["results"]["transcription"],
                user_id=current_user.id
            )
            db.add(db_transcription)
            db.commit()
    
    logger.info(f"Enviando respuesta con process_id: {process_id}")
    return {"status": "processing", "job_id": process_id}

@app.post("/api/upload-file", response_model=JobStatus)
async def upload_file_with_api_prefix(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Endpoint duplicado para carga de archivos con prefijo /api."""
    # Reutilizamos la lógica del endpoint original con await
    return await upload_file_simple(file, background_tasks, current_user, db)

@app.post("/upload/", response_model=JobStatus)
async def upload_file(
    file: UploadFile = File(...),
    model_size: str = Form(default_model),
    summary_method: str = Form("deepseek"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload an audio file for transcription.
    
    Args:
        file: Audio file to transcribe
        model_size: Size of the model to use ('base', 'enhanced', 'nova', 'nova-2', 'nova-3', 'whisper-large', etc.)
        summary_method: Method for generating summaries ('local', 'gpt')
        background_tasks: FastAPI BackgroundTasks for async processing
        current_user: Usuario actualmente autenticado
        db: Sesión de base de datos
        
    Returns:
        JSON response with process ID
    """
    # Check file type
    if not file.content_type.startswith(('audio/', 'video/')):
        raise HTTPException(status_code=400, detail="File must be an audio or video file.")
    
    # Generate process ID
    process_id = str(uuid.uuid4())
    
    # Create directory for this job
    job_dir = TEMP_DIR / process_id
    job_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = job_dir / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Store job info
    jobs[process_id] = {
        "status": "uploaded",
        "file_path": str(file_path),
        "original_filename": file.filename,
        "model_size": model_size,
        "summary_method": summary_method,
        "user_id": current_user.id  # Asociar con el usuario actual
    }
    
    # Process in background
    if background_tasks:
        background_tasks.add_task(process_audio_file, process_id)
    else:
        # For testing without background tasks
        await process_audio_file(process_id)
        
        # Guardar la transcripción en la base de datos cuando esté completa
        if jobs[process_id]["status"] == "completed":
            # Crear entrada en la base de datos
            db_transcription = DBTranscription(
                title=f"Transcripción de {file.filename}",
                original_filename=file.filename,
                file_path=str(file_path),
                content=jobs[process_id]["results"]["transcription"],
                user_id=current_user.id
            )
            db.add(db_transcription)
            db.commit()
    
    return {"status": "processing", "job_id": process_id}

@app.get("/status/{process_id}")
async def get_status(process_id: str):
    """
    Get the status of a transcription job.
    
    Args:
        process_id: ID of the process to check
        
    Returns:
        Status of the job
    """
    if process_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
    
    job = jobs[process_id]
    
    return JobStatus(
        status=job["status"],
        error=job.get("error"),  # Usar .get() para manejar el caso donde error no existe
        job_id=process_id
    )

@app.get("/api/status/{process_id}")
async def get_status_with_api_prefix(process_id: str):
    """Duplicate endpoint for status with explicit /api prefix."""
    return await get_status(process_id)

@app.get("/results/{process_id}")
async def get_results(process_id: str):
    """
    Get the results of a transcription job.
    
    Args:
        process_id: ID of the process to get results for
        
    Returns:
        Structured response with transcription and summaries
    """
    if process_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
    
    job = jobs[process_id]
    
    # Permitir obtener resultados parciales si el estado es:
    # - completed (proceso finalizado)
    # - transcription_complete (transcripción lista, resumen pendiente)
    # - summarizing (generando resumen)
    valid_states = ["completed", "transcription_complete", "summarizing"]
    if job["status"] not in valid_states:
        raise HTTPException(status_code=400, detail=f"Process {process_id} is not ready yet. Current status: {job['status']}")
    
    # Asegurarse de que el resultado incluya una estructura consistente
    results = job["results"]
    
    # Si es un diccionario, asegurarse de que tenga la estructura esperada
    if isinstance(results, dict):
        # Si tiene 'text' pero no 'transcription', adaptar la estructura
        if "transcription" not in results and "text" in results:
            results["transcription"] = results["text"]
            
        # Asegurar que los campos de resumen existan y tengan formato consistente
        if "short_summary" not in results:
            results["short_summary"] = ""
            
        if "key_points" not in results:
            results["key_points"] = []
        elif isinstance(results["key_points"], str):
            # Si key_points es una cadena, convertirla a lista
            results["key_points"] = [point.strip() for point in results["key_points"].split("\n") if point.strip()]
            
        if "action_items" not in results:
            results["action_items"] = []
        elif isinstance(results["action_items"], str):
            # Si action_items es una cadena, convertirla a lista
            results["action_items"] = [item.strip() for item in results["action_items"].split("\n") if item.strip()]
    
    return results

@app.get("/api/results/{process_id}")
async def get_results_with_api_prefix(process_id: str):
    """Duplicate endpoint for results with explicit /api prefix."""
    return await get_results(process_id)

@app.get("/summary/{process_id}")
async def get_summary(process_id: str):
    """
    Get only the structured summary of a completed transcription job.
    
    Args:
        process_id: ID of the process to get summary for
        
    Returns:
        Structured summary with short_summary, key_points, and action_items
    """
    if process_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
    
    job = jobs[process_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Process {process_id} is not completed yet")
    
    results = job["results"]
    summary = {}
    
    if isinstance(results, dict):
        summary["short_summary"] = results.get("short_summary", "")
        
        key_points = results.get("key_points", [])
        if isinstance(key_points, str):
            key_points = [point.strip() for point in key_points.split("\n") if point.strip()]
        summary["key_points"] = key_points
        
        action_items = results.get("action_items", [])
        if isinstance(action_items, str):
            action_items = [item.strip() for item in action_items.split("\n") if item.strip()]
        summary["action_items"] = action_items
    
    return summary

@app.get("/api/summary/{process_id}")
async def get_summary_with_api_prefix(process_id: str):
    """Endpoint duplicado para obtener resumen con prefijo /api/."""
    return await get_summary(process_id)

@app.get("/download/{process_id}")
async def download_results(process_id: str, format: str = "txt"):
    """
    Download the results of a completed transcription job.
    
    Args:
        process_id: ID of the process to download results for
        format: Format of the results to download ('txt' or 'pdf')
        
    Returns:
        File response with the requested format
    """
    if process_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
    
    job = jobs[process_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Process {process_id} is not completed yet")
    
    job_dir = TEMP_DIR / process_id
    
    # Obtener el nombre original del archivo desde el campo 'original_filename'
    if "original_filename" in job:
        original_filename = Path(job["original_filename"]).stem
    else:
        original_filename = Path(job["file_path"]).stem
    
    if format == "txt":
        txt_path = job_dir / "transcription.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(job["results"]["transcription"])
        
        # Crear respuesta con el nombre de archivo original
        with open(txt_path, "rb") as f:
            content = f.read()
            
        return Response(
            content=content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{original_filename}.txt"',
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
    elif format == "pdf":
        pdf_path = job_dir / "report.pdf"
        # Only generate the PDF if it doesn't exist
        if not pdf_path.exists() and "summaries" in job["results"]:
            summaries = job["results"].get("summaries", {})
            generate_pdf(
                job["results"]["transcription"],
                summaries.get("short", ""),
                summaries.get("key_points", []),
                summaries.get("action_items", []),
                pdf_path
            )
        
        # Crear respuesta con el nombre de archivo original
        with open(pdf_path, "rb") as f:
            content = f.read()
            
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{original_filename}.pdf"',
                "Content-Type": "application/pdf"
            }
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'txt' or 'pdf'")

@app.get("/api/download/{process_id}")
async def download_results_with_api_prefix(process_id: str, format: str = "txt"):
    """Endpoint duplicado para la descarga con prefijo /api/."""
    if process_id not in jobs:
        raise HTTPException(status_code=404, detail="Process not found")
    
    job = jobs[process_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Process not completed")
    
    original_filename = job.get("original_filename", "transcription")
    
    if format == "txt":
        # Return plain text
        content = job["results"]["transcription"]
        
        return Response(
            content=content.encode("utf-8"),
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{original_filename}.txt"',
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
    elif format == "pdf":
        # Generate PDF
        pdf_path = f"results/{process_id}.pdf"
        
        if not os.path.exists(pdf_path):
            # Create PDF
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Add content
            pdf.multi_cell(0, 10, job["results"]["transcription"])
            
            # Save PDF
            pdf.output(pdf_path)
        
        # Return PDF
        with open(pdf_path, "rb") as f:
            content = f.read()
            
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{original_filename}.pdf"',
                "Content-Type": "application/pdf"
            }
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'txt' or 'pdf'")

@app.post("/api/users/token", response_model=Token)
def login_with_api_prefix(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Endpoint duplicado para autenticación con prefijo /api."""
    # Reutilizamos la lógica del endpoint original
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/transcriptions/", response_model=List[Dict[str, Any]])
async def get_user_transcriptions_with_api_prefix(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Endpoint duplicado para historial de transcripciones con prefijo /api/."""
    try:
        logger.info(f"Usuario {current_user.username} solicitó transcripciones (API)")
        
        # Consulta simple para obtener transcripciones del usuario
        transcriptions_list = db.query(DBTranscription).filter(
            DBTranscription.user_id == current_user.id
        ).all()
        
        logger.info(f"Encontradas {len(transcriptions_list)} transcripciones para el usuario {current_user.username}")
        
        # Convertir a formato de respuesta simplificado (diccionarios simples)
        result = []
        for t in transcriptions_list:
            try:
                # Crear un diccionario con solo los campos necesarios para la respuesta
                trans_dict = {
                    "id": str(t.id),
                    "title": t.title or "",
                    "original_filename": t.original_filename or "",
                    "content": t.transcription or "",  # Usar el nombre antiguo para compatibilidad
                    "file_path": t.audio_path or "",   # Usar el nombre antiguo para compatibilidad
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "user_id": str(t.user_id),
                    # Añadir campos de resumen
                    "short_summary": t.short_summary or "",
                    "key_points": t.key_points or [],
                    "action_items": t.action_items or []
                }
                
                result.append(trans_dict)
                
            except Exception as e:
                logger.error(f"Error al procesar transcripción {t.id}: {str(e)}")
                # Continuar con la siguiente transcripción
        
        logger.info(f"Procesadas correctamente {len(result)} transcripciones")
        return result
        
    except Exception as e:
        logger.error(f"Error al obtener transcripciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener transcripciones: {str(e)}"
        )

async def process_audio_file_simple(process_id: str):
    """
    Process an audio file asynchronously without summarization.
    
    Args:
        process_id: ID of the process
    """
    if process_id not in jobs:
        logger.error(f"Process {process_id} not found")
        return
    
    job = jobs[process_id]
    
    try:
        job["status"] = "processing_audio"
        
        file_path = job["file_path"]
        model_size = job["model_size"]
        
        try:
            # Initialize transcriber with the specified model
            transcriber = Transcriber(model_size=model_size)
            
            # Update status
            job["status"] = "transcribing"
            
            # Transcribe audio
            transcription = transcriber.transcribe(file_path)
            
            # Store results
            job["results"] = {
                "transcription": transcription,
            }
            
            # Update status
            job["status"] = "completed"
            
        except Exception as e:
            # Update status to error
            job["status"] = "error"
            job["error"] = str(e)
            logger.error(f"Error transcribing audio: {str(e)}")
            
    except Exception as e:
        # Update status to error
        job["status"] = "error"
        job["error"] = str(e)
        logger.error(f"Error processing audio file: {str(e)}")

async def process_audio_file(process_id: str):
    """
    Process an audio file asynchronously.
    
    Args:
        process_id: ID of the process
    """
    if process_id not in jobs:
        logger.error(f"Process {process_id} not found")
        return
    
    job = jobs[process_id]
    
    try:
        job["status"] = "processing_audio"
        
        file_path = job["file_path"]
        model_size = job["model_size"]
        summary_method = job["summary_method"]
        
        try:
            # Initialize transcriber with the specified model
            transcriber = Transcriber(model_size=model_size)
            
            # Update status
            job["status"] = "transcribing"
            
            # Transcribe audio - Ahora recibimos también los utterances
            transcription, utterances_data = transcriber.transcribe(file_path)
            
            # Asegurar que utterances_data sea una lista
            if not isinstance(utterances_data, list):
                utterances_data = [utterances_data] if utterances_data else []
            
            # Actualizar estado y resultados parciales para que la transcripción sea visible
            # mientras se genera el resumen
            job["status"] = "transcription_complete"
            job["results"] = {
                "transcription": transcription,
                "utterances_json": utterances_data,  # [SF] Guardamos los utterances en los resultados
                "summary_status": "pending",  # Indica que el resumen está en proceso
                "short_summary": "",
                "key_points": [],
                "action_items": []
            }
            
            # Pausa para permitir que el frontend detecte el estado intermedio
            logger.info("Estado actualizado a 'transcription_complete'. Esperando 3 segundos antes de continuar...")
            await asyncio.sleep(3)
            
            # Generate summaries
            job["status"] = "summarizing"
            
            # Generate summaries using the specified method
            short_summary, key_points, action_items = transcriber.generate_summaries(
                transcription,
                method=summary_method
            )
            
            # Update results with summaries
            job["results"].update({
                "summary_status": "complete",  # Indica que el resumen está listo
                "short_summary": short_summary,
                "key_points": key_points,
                "action_items": action_items
            })
            
            # Update status
            job["status"] = "completed"
            
            # Guardar en la base de datos si el job tiene un usuario asociado
            if "user_id" in job and job["user_id"]:
                try:
                    # Crear sesión de base de datos
                    db = SessionLocal()
                    
                    # Verificar si ya existe una transcripción con este process_id
                    existing = db.query(DBTranscription).filter(
                        DBTranscription.audio_path == file_path
                    ).first()
                    
                    if not existing:
                        # Crear entrada en la base de datos con información adicional
                        db_transcription = DBTranscription(
                            title=f"Transcripción de {Path(file_path).name}",
                            original_filename=job.get("original_filename", Path(file_path).name),
                            audio_path=file_path,
                            transcription=transcription,
                            utterances_json=utterances_data,  # [SF] Guardamos los utterances en la base de datos
                            short_summary=job["results"].get("short_summary"),
                            key_points=job["results"].get("key_points", []),
                            action_items=job["results"].get("action_items", []),
                            user_id=job["user_id"],
                            created_at=datetime.utcnow()  # Establecer explícitamente la fecha de creación
                        )
                        db.add(db_transcription)
                    else:
                        # Actualizar la entrada existente con los datos del resumen y utterances
                        existing.short_summary = job["results"].get("short_summary")
                        existing.key_points = job["results"].get("key_points", [])
                        existing.action_items = job["results"].get("action_items", [])
                        existing.utterances_json = utterances_data  # [SF] Actualizar utterances si ya existe la transcripción
                        existing.updated_at = datetime.utcnow()  # Actualizar la fecha de modificación
                    
                    # Commit para guardar los cambios
                    db.commit()
                    
                    # Mantener este log ya que es informativo para operaciones importantes
                    logger.info(f"Transcripción y resumen guardados correctamente en la base de datos para el proceso {process_id}")
                except Exception as db_error:
                    logger.error(f"Error guardando transcripción en la base de datos: {str(db_error)}")
                finally:
                    db.close()
            
        except Exception as e:
            # Update status to error
            job["status"] = "error"
            job["error"] = str(e)
            logger.error(f"Error transcribing audio: {str(e)}")
            
    except Exception as e:
        # Update status to error
        job["status"] = "error"
        job["error"] = str(e)
        logger.error(f"Error processing audio file: {str(e)}")

def generate_pdf(transcription, short_summary, key_points, action_items, output_path):
    """
    Generate a PDF report with the transcription and summaries.
    
    Args:
        transcription: Full transcription text
        short_summary: Short summary of the transcription
        key_points: Key points extracted from the transcription
        action_items: Action items extracted from the transcription
        output_path: Path to save the PDF file
    """
    try:
        from fpdf import FPDF
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'Whisper Meeting Transcriber - Reporte', 0, 1, 'C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
                
            def chapter_title(self, title):
                self.set_font('Arial', 'B', 12)
                self.set_fill_color(200, 220, 255)
                self.cell(0, 10, title, 0, 1, 'L', 1)
                self.ln(5)
                
            def chapter_body(self, body):
                self.set_font('Arial', '', 11)
                self.multi_cell(0, 5, body)
                self.ln()
                
            def bullet_list(self, items):
                self.set_font('Arial', '', 11)
                for item in items:
                    self.cell(10, 5, chr(149), 0, 0)  # Bullet character
                    self.multi_cell(0, 5, item)
        
        pdf = PDF()
        pdf.add_page()
        
        pdf.chapter_title('Transcripción Completa')
        pdf.chapter_body(transcription)
        pdf.ln(10)
        
        if short_summary:
            pdf.chapter_title('Resumen Corto')
            pdf.chapter_body(short_summary)
            pdf.ln(10)
        
        if key_points:
            pdf.chapter_title('Puntos Clave')
            pdf.bullet_list(key_points)
            pdf.ln(10)
        
        if action_items:
            pdf.chapter_title('Elementos de Acción')
            pdf.bullet_list(action_items)
        
        pdf.output(str(output_path))
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
