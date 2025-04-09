"""
Configuración de CORS para la aplicación.
"""
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    """
    Configura CORS para la aplicación FastAPI.
    
    Args:
        app: Aplicación FastAPI
    """
    # Orígenes permitidos
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://134.199.218.48",  # Servidor de producción
    ]
    
    # Configurar middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,  # 24 horas
    )
    
    return app
