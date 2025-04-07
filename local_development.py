#!/usr/bin/env python3
import os
import sys

# Este script configura el entorno para desarrollo local
# sin afectar la configuración del servidor

def setup_environment():
    """
    Modifica el sys.path para permitir importaciones relativas
    en entorno de desarrollo local.
    """
    # Obtener la ruta absoluta del directorio del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Añadir el directorio del proyecto al PYTHONPATH
    sys.path.insert(0, project_dir)
    
    print("Entorno de desarrollo local configurado correctamente.")

if __name__ == "__main__":
    setup_environment()
