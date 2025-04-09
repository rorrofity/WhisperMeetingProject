"""
Middleware personalizado para manejar CORS en la aplicación.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

def setup_cors_middleware(app: FastAPI):
    """
    Configura el middleware CORS para la aplicación FastAPI.
    
    Args:
        app: Instancia de FastAPI
    """
    origins = [
        "http://localhost:5173",  # Frontend en desarrollo
        "http://localhost:3000",
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:8080",
        "http://134.199.218.48",  # Servidor de producción
        "*",  # Permitir todos los orígenes (como último recurso)
    ]
    
    logger.info(f"Configurando CORS middleware con orígenes permitidos: {origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,  # 24 horas
    )
    
    logger.info("CORS middleware configurado correctamente")
    
    return app
