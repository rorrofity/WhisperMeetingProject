#!/usr/bin/env python3
"""
Script para configurar el entorno de desarrollo local.
Este script modifica el PYTHONPATH para permitir que las importaciones relativas
funcionen en el entorno local de WSL sin tener que modificar todos los archivos fuente.
"""

import os
import sys
import subprocess

def setup_environment():
    """Configura el entorno de desarrollo añadiendo las rutas necesarias al PYTHONPATH."""
    # Obtener rutas absolutas
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, 'backend')
    
    # Configurar variables de entorno
    os.environ['PYTHONPATH'] = f"{project_dir}:{backend_dir}:{os.environ.get('PYTHONPATH', '')}"
    
    print(f"PYTHONPATH configurado: {os.environ['PYTHONPATH']}")
    
    # Iniciar backend
    try:
        print("Iniciando servidor backend...")
        subprocess.run([
            "python3", "-m", "uvicorn", "backend.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], cwd=project_dir)
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"Error al iniciar el servidor: {str(e)}")
        
if __name__ == "__main__":
    setup_environment()
