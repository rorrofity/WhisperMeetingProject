import os
import shutil
import tempfile
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from utils.audio_processor import AudioProcessor
from utils.transcriber import Transcriber

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Whisper Meeting Transcriber")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Store job status and results
jobs = {}  # type: Dict[str, Dict[str, Any]]


class JobStatus(BaseModel):
    status: str
    error: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint to check API status."""
    return {"message": "Whisper Meeting Transcriber API is running"}


@app.post("/upload-file/")
async def upload_file_simple(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Upload an audio file for transcription using configured model from .env.
    
    Args:
        file: Audio file to transcribe
        background_tasks: FastAPI BackgroundTasks for async processing
        
    Returns:
        JSON response with process ID
    """
    try:
        # Generate a process ID
        process_id = str(uuid.uuid4())
        
        # Create a directory for this job
        job_dir = TEMP_DIR / process_id
        job_dir.mkdir(exist_ok=True)
        
        # Save the uploaded file
        temp_file_path = job_dir / file.filename
        logger.info(f"Subiendo archivo: {file.filename}")
        logger.info(f"Ruta temporal completa: {temp_file_path}")
        
        # Save the uploaded file in chunks
        with open(temp_file_path, "wb") as buffer:
            chunk_size = 1024 * 1024  # 1MB chunks
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
        
        logger.info(f"Archivo guardado exitosamente en: {temp_file_path}")
        
        # Initialize job status
        jobs[process_id] = {
            "status": "processing_audio",
            "file_path": str(temp_file_path),
            "original_filename": file.filename,  
            "model_size": default_model,  
            "summary_method": None,  
            "error": None,
            "results": {}
        }
        
        logger.info(f"Job inicializado: {jobs[process_id]}")
        
        # Process the audio file in the background
        if background_tasks:
            background_tasks.add_task(process_audio_file_simple, process_id)
        else:
            # For testing, process synchronously
            await process_audio_file_simple(process_id)
        
        return {
            "process_id": process_id,
            "message": "Audio file uploaded successfully. Processing..."
        }
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")


@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    model_size: str = Form(default_model),
    summary_method: str = Form("local"),
    background_tasks: BackgroundTasks = None
):
    """
    Upload an audio file for transcription.
    
    Args:
        file: Audio file to transcribe
        model_size: Size of the model to use ('base', 'enhanced', 'nova', 'nova-2', 'nova-3', 'whisper-large', etc.)
        summary_method: Method for generating summaries ('local', 'gpt')
        background_tasks: FastAPI BackgroundTasks for async processing
        
    Returns:
        JSON response with process ID
    """
    try:
        # Generate a process ID
        process_id = str(uuid.uuid4())
        
        # Create a directory for this job
        job_dir = TEMP_DIR / process_id
        job_dir.mkdir(exist_ok=True)
        
        # Save the uploaded file
        temp_file_path = job_dir / file.filename
        logger.info(f"Subiendo archivo (upload_file): {file.filename}")
        logger.info(f"Ruta temporal completa (upload_file): {temp_file_path}")
        
        # Save the uploaded file in chunks
        with open(temp_file_path, "wb") as buffer:
            chunk_size = 1024 * 1024  # 1MB chunks
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
        
        logger.info(f"Archivo guardado exitosamente en (upload_file): {temp_file_path}")
        
        # Initialize job status
        jobs[process_id] = {
            "status": "processing_audio",
            "file_path": str(temp_file_path),
            "original_filename": file.filename,  
            "model_size": model_size,
            "summary_method": summary_method,
            "error": None,
            "results": {}
        }
        
        logger.info(f"Job inicializado (upload_file): {jobs[process_id]}")
        
        # Process the audio file in the background
        if background_tasks:
            background_tasks.add_task(process_audio_file, process_id)
        else:
            # For testing, process synchronously
            await process_audio_file(process_id)
        
        return {
            "process_id": process_id,
            "message": "Audio file uploaded successfully. Processing..."
        }
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")


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
        error=job["error"]
    )


@app.get("/results/{process_id}")
async def get_results(process_id: str):
    """
    Get the results of a completed transcription job.
    
    Args:
        process_id: ID of the process to get results for
        
    Returns:
        Transcription and summaries
    """
    if process_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Process {process_id} not found")
    
    job = jobs[process_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Process {process_id} is not completed yet")
    
    return job["results"]


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
            logger.info(f"Processing audio file: {file_path}")
            processed_file = audio_processor.process_audio(file_path)
            
            job["status"] = "transcribing"
            
            logger.info(f"Transcribing audio with model: {model_size}")
            transcriber = Transcriber(model_size=model_size)
            
            logger.info(f"Transcribing audio file: {processed_file}")
            transcription = transcriber.transcribe(processed_file)
            
            job["results"]["transcription"] = transcription
                
            job["status"] = "completed"
            
            job_dir = TEMP_DIR / process_id
            txt_path = job_dir / "transcription.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcription)
            
            logger.info(f"Completed processing for {process_id}")
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            job["status"] = "error"
            job["error"] = f"Error processing audio: {str(e)}"
            raise
            
    except Exception as e:
        logger.error(f"Unhandled error in process_audio_file: {str(e)}")
        job["status"] = "error"
        job["error"] = f"Unhandled error: {str(e)}"


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
            logger.info(f"Processing audio file: {file_path}")
            processed_file = audio_processor.process_audio(file_path)
            
            job["status"] = "transcribing"
            
            logger.info(f"Transcribing audio with model: {model_size}")
            transcriber = Transcriber(model_size=model_size)
            
            logger.info(f"Transcribing audio file: {processed_file}")
            transcription = transcriber.transcribe(processed_file)
            
            job["results"]["transcription"] = transcription
            
            job["status"] = "summarizing"
            
            if summary_method:
                logger.info(f"Generating summaries with method: {summary_method}")
                
                job["results"]["summaries"] = {}
                
            job["status"] = "completed"
            
            job_dir = TEMP_DIR / process_id
            txt_path = job_dir / "transcription.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(transcription)
            
            logger.info(f"Completed processing for {process_id}")
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            job["status"] = "error"
            job["error"] = f"Error processing audio: {str(e)}"
            raise
            
    except Exception as e:
        logger.error(f"Unhandled error in process_audio_file: {str(e)}")
        job["status"] = "error"
        job["error"] = f"Unhandled error: {str(e)}"


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
