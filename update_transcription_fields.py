#!/usr/bin/env python3
"""
Script para actualizar las referencias a los campos de transcripciones en main.py
después de la migración del modelo de datos.
"""

import re
import sys
from pathlib import Path

def update_main_py():
    """Actualiza el archivo main.py para usar los nuevos nombres de campos."""
    main_py_path = Path("backend/main.py")
    
    if not main_py_path.exists():
        print(f"Error: No se encontró el archivo {main_py_path}")
        return False
    
    # Leer el contenido del archivo
    with open(main_py_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Patrones para reemplazar
    patterns = [
        # Patrón 1: En upload_file_simple
        (r'db_transcription = DBTranscription\(\s+title=f"Transcripción de {Path\(file\.filename\)\.name}",\s+original_filename=file\.filename,\s+file_path=str\(file_path\),\s+content="",\s+user_id=current_user\.id\s+\)',
         'db_transcription = DBTranscription(\n            title=f"Transcripción de {Path(file.filename).name}",\n            original_filename=file.filename,\n            audio_path=str(file_path),\n            transcription="",\n            user_id=current_user.id\n        )'),
        
        # Patrón 2: En process_audio_file_simple
        (r'db_transcription = DBTranscription\(\s+title=f"Transcripción de {Path\(file_path\)\.name}",\s+original_filename=job\.get\("original_filename", Path\(file_path\)\.name\),\s+file_path=file_path,\s+content=transcription,\s+user_id=job\["user_id"\]\s+\)',
         'db_transcription = DBTranscription(\n                            title=f"Transcripción de {Path(file_path).name}",\n                            original_filename=job.get("original_filename", Path(file_path).name),\n                            audio_path=file_path,\n                            transcription=transcription,\n                            user_id=job["user_id"]\n                        )'),
        
        # Patrón 3: En process_audio_file
        (r'db_transcription = DBTranscription\(\s+title=f"Transcripción de {Path\(file_path\)\.name}",\s+original_filename=job\.get\("original_filename", Path\(file_path\)\.name\),\s+file_path=file_path,\s+content=transcription,\s+user_id=job\["user_id"\]\s+\)',
         'db_transcription = DBTranscription(\n                            title=f"Transcripción de {Path(file_path).name}",\n                            original_filename=job.get("original_filename", Path(file_path).name),\n                            audio_path=file_path,\n                            transcription=transcription,\n                            short_summary=short_summary,\n                            key_points=key_points,\n                            action_items=action_items,\n                            user_id=job["user_id"]\n                        )'),
        
        # Patrón 4: En upload_file
        (r'db_transcription = DBTranscription\(\s+title=f"Transcripción de {Path\(file\.filename\)\.name}",\s+original_filename=file\.filename,\s+file_path=str\(file_path\),\s+content="",\s+user_id=current_user\.id\s+\)',
         'db_transcription = DBTranscription(\n            title=f"Transcripción de {Path(file.filename).name}",\n            original_filename=file.filename,\n            audio_path=str(file_path),\n            transcription="",\n            user_id=current_user.id\n        )'),
        
        # Patrón 5: Verificación de existencia de transcripción
        (r'existing = db\.query\(DBTranscription\)\.filter\(\s+DBTranscription\.file_path == file_path\s+\)\.first\(\)',
         'existing = db.query(DBTranscription).filter(\n                        DBTranscription.audio_path == file_path\n                    ).first()'),
    ]
    
    # Aplicar los reemplazos
    updated_content = content
    for pattern, replacement in patterns:
        updated_content = re.sub(pattern, replacement, updated_content, flags=re.DOTALL)
    
    # Guardar el archivo actualizado
    with open(main_py_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"Se ha actualizado el archivo {main_py_path}")
    return True

if __name__ == "__main__":
    update_main_py()
