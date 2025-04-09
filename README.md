# Whisper Meeting Transcriber

Sistema local para transcribir archivos de audio y exportar resultados utilizando Deepgram.

## Características Principales

- Carga de archivos de audio (.mp3, .mp4, .wav, .m4a)
- Transcripción automática con la API de Deepgram 
- Procesamiento directo de archivos grandes sin segmentación
- Procesamiento y normalización de audio con FFmpeg
- Descarga de resultados en formato TXT
- Interfaz web moderna con React, Vite y TailwindCSS
- **Sistema de autenticación con JWT**
- **Historial de transcripciones por usuario**
- **Manejo robusto de estados de transcripción con notificaciones claras**
- **Redirección automática a login al expirar el token JWT**
- **Modelo de datos mejorado con soporte para proyectos, destacados y etiquetas**

## Estructura del Proyecto

```
WhisperMeetingProject/
├── backend/              # API FastAPI para procesamiento
│   ├── main.py           # Punto de entrada principal de la API
│   ├── requirements.txt  # Dependencias de Python
│   ├── .env              # Variables de entorno (API keys, etc.)
│   ├── temp/             # Almacenamiento temporal de archivos
│   ├── utils/            # Utilidades para procesamiento
│   │   ├── __init__.py   
│   │   ├── audio_processor.py  # Procesamiento de archivos de audio
│   │   └── transcriber.py      # Transcripción con Deepgram
│   ├── auth/             # Sistema de autenticación
│   │   ├── __init__.py
│   │   ├── jwt.py        # Autenticación con JWT
│   │   └── utils.py      # Utilidades para hash de contraseñas
│   ├── database/         # Conexión y modelos de base de datos
│   │   ├── __init__.py
│   │   ├── connection.py # Configuración de SQLite
│   │   └── init_db.py    # Inicialización de la base de datos
│   ├── models/           # Modelos de datos
│   │   ├── __init__.py
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   └── schemas.py    # Esquemas Pydantic
│   └── routers/          # Routers de la API
│       ├── __init__.py
│       ├── users.py      # Endpoints de usuarios
│       └── transcriptions.py # Endpoints de transcripciones
│
├── frontend/             # Aplicación React con Vite y TailwindCSS
│   ├── src/              # Código fuente de React
│   │   ├── components/   # Componentes de la interfaz
│   │   │   ├── Header.jsx       # Encabezado de la aplicación
│   │   │   ├── Footer.jsx       # Pie de página
│   │   │   ├── Login.jsx        # Componente de inicio de sesión
│   │   │   ├── Register.jsx     # Componente de registro
│   │   │   ├── Auth.jsx         # Contenedor de autenticación
│   │   │   ├── TranscriptionHistory.jsx # Historial de transcripciones
│   │   │   └── TranscriptionView.jsx  # Vista de transcripción
│   │   ├── contexts/     # Contextos de React
│   │   │   └── AuthContext.jsx  # Contexto de autenticación
│   │   ├── App.jsx       # Componente principal
│   │   ├── main.jsx      # Punto de entrada de React
│   │   └── index.css     # Estilos globales con TailwindCSS
│   ├── index.html        # Plantilla HTML
│   ├── vite.config.js    # Configuración de Vite
│   ├── tailwind.config.js # Configuración de TailwindCSS
│   ├── postcss.config.js # Configuración de PostCSS
│   └── package.json      # Dependencias y scripts
│
├── initialize_app.py     # Script para inicializar la base de datos y crear usuario
├── start_app.py          # Script para iniciar todo el sistema
├── dev_setup.py          # Script para configuración de desarrollo local en WSL
├── AUTH_GUIDE.md         # Guía del sistema de autenticación
├── DEEPGRAM_GUIDE.md     # Guía para configurar Deepgram
├── API_REFERENCE.md      # Documentación de la API
└── README.md             # Documentación del proyecto
```

## Requisitos 

- Python 3.8+
- Node.js 14+
- FFmpeg instalado en el sistema
- Conexión a internet (obligatoria para la API de Deepgram)
- Clave API de Deepgram (necesaria para la transcripción)

## Instalación

1. Clonar el repositorio o ir al directorio del proyecto:
   ```bash
   cd ~/WhisperMeetingProject
   ```

2. Instalar dependencias del backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Instalar dependencias del frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Inicializar la base de datos y crear un usuario (opcional):
   ```bash
   python initialize_app.py --create-user
   ```
   
   Puedes personalizar los datos del usuario:
   ```bash
   python initialize_app.py --create-user --username miusuario --email correo@ejemplo.com --password micontraseña
   ```

## Uso

1. Iniciar el sistema con el script:
   ```bash
   python start_app.py
   ```

2. **Para desarrollo en entorno WSL (Windows Subsystem for Linux):**
   ```bash
   python dev_setup.py
   ```
   
   Este script está diseñado específicamente para solucionar problemas de importación en entornos WSL:
   - Configura automáticamente el PYTHONPATH para que las importaciones relativas funcionen correctamente
   - Evita errores comunes en el entorno local sin modificar el código fuente
   - Es la opción recomendada para desarrolladores que trabajan con WSL

3. Alternativamente, puedes iniciar manualmente los servidores:
   
   Backend:
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Frontend:
   ```bash
   cd frontend
   npm run dev
   ```

4. Abrir el navegador web y acceder a:
   ```
   http://localhost:5173
   ```

5. Iniciar sesión con tus credenciales o registrar una nueva cuenta
6. Subir un archivo de audio usando la interfaz
7. Esperar a que se complete la transcripción
8. Ver y descargar los resultados

## Despliegue en Producción

Para desplegar esta aplicación en un servidor de producción, sigue los pasos detallados en [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

### Consideraciones Importantes para el Despliegue

- Asegúrate de que tu archivo `.env` contenga todas las variables necesarias
- Sigue al pie de la letra la configuración del servicio systemd, incluyendo la variable `PYTHONPATH`
- Ejecuta correctamente los pasos de inicialización de la base de datos

Para el mantenimiento continuo del sistema desplegado, consulta [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md).

## Sistema de Autenticación

La aplicación utiliza un sistema de autenticación basado en tokens JWT (JSON Web Tokens):

- **Registro de usuario**: Los usuarios pueden crear una cuenta con correo electrónico, nombre de usuario y contraseña
- **Inicio de sesión**: Genera un token JWT que se usa para autenticar solicitudes a la API
- **Protección de rutas**: Sólo los usuarios autenticados pueden acceder a ciertos endpoints
- **Historial de transcripciones**: Cada transcripción se asocia al usuario que la creó

Para obtener más información sobre el sistema de autenticación, consulta [AUTH_GUIDE.md](./AUTH_GUIDE.md).

## Configuración de Deepgram

Para utilizar la aplicación, necesitas una clave API de Deepgram:

1. Crear una cuenta en [Deepgram](https://console.deepgram.com/signup)
2. Generar una API key en tu dashboard
3. Añadir la API key en el archivo `backend/.env`:
   ```
   DEEPGRAM_API_KEY=tu_clave_api_aqui
   ```

**Importante**: Se requiere una clave API de Deepgram para usar el servicio de transcripción.

Para más detalles sobre la configuración de Deepgram, consulta [DEEPGRAM_GUIDE.md](./DEEPGRAM_GUIDE.md).

### Variables de Entorno (.env)

```
# Clave API de Deepgram (REQUERIDA para la transcripción de audio)
DEEPGRAM_API_KEY=tu_clave_api_aqui

# Configuración del modelo de transcripción
# Opciones: base, enhanced, nova, nova-2, whisper-large, etc.
# Nota: Si necesitas soporte multilingüe, usa whisper-large o nova-2
# Nova-3 tiene mejor precisión pero solo está disponible en inglés en la API estándar
TRANSCRIPTION_MODEL=nova-2

# Configuración del idioma (es-419 es específico para español de Latinoamérica)
# Esta configuración proporciona mejor reconocimiento de acentos latinoamericanos
LANGUAGE=es-419

# Configuración del servidor
HOST=0.0.0.0
PORT=8000

# Configuración JWT (generada automáticamente por initialize_app.py)
JWT_SECRET_KEY=clave_secreta_generada_automaticamente
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API REST

El sistema proporciona una API REST para integraciones. Los endpoints principales:

- **Autenticación**:
  - `POST /users/register`: Registro de usuarios
  - `POST /users/token`: Inicio de sesión y obtención de token

- **Transcripciones**:
  - `POST /upload-file/`: Sube un archivo y obtiene transcripción
  - `GET /status/{process_id}`: Verifica el estado de la transcripción
  - `GET /results/{process_id}`: Obtiene resultados de la transcripción
  - `GET /download/{process_id}?format={txt}`: Descarga resultados

- **Historial de transcripciones**:
  - `GET /transcriptions/`: Obtiene todas las transcripciones del usuario
  - `GET /transcriptions/{id}`: Obtiene una transcripción específica
  - `POST /transcriptions/`: Crea una transcripción manualmente
  - `DELETE /transcriptions/{id}`: Elimina una transcripción

Ver [API_REFERENCE.md](./API_REFERENCE.md) para documentación completa.

## Consideraciones de Desarrollo Importantes

### Reglas de Importación
Para asegurar que la aplicación funcione correctamente tanto en desarrollo como en producción, sigue estas reglas para las importaciones de Python en el backend:

- **Importaciones absolutas sin prefijo "backend"**: Usa `from models.models import User` en lugar de `from backend.models.models import User`
- **Evita importaciones relativas con ".."**: No uses `from ..database.connection import get_db`
- **Importaciones relativas del mismo directorio**: Puedes usar `from .utils import verify_password` para importar del mismo directorio

Esta configuración funciona con la variable `PYTHONPATH=/var/www/whisper-meeting/backend` establecida en el servicio systemd del servidor de producción.

## Personalización y Extensión

### Frontend

- Modificar estilos: Editar `frontend/src/index.css` y `tailwind.config.js`
- Añadir componentes: Crear nuevos componentes en `frontend/src/components/`
- Personalizar autenticación: Modificar `frontend/src/contexts/AuthContext.jsx`

### Backend

- Cambiar modelos de Deepgram: Editar `TRANSCRIPTION_MODEL` en `.env`
- Optimizar procesamiento de audio: Modificar `backend/utils/audio_processor.py`
- Ajustar parámetros de Deepgram: Editar configuraciones en `backend/utils/transcriber.py`
- Personalizar sistema de autenticación: Modificar `backend/auth/jwt.py`

## Solución de Problemas

- **Error de FFmpeg**: Instalar FFmpeg si no está presente
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install ffmpeg
  
  # macOS
  brew install ffmpeg
  ```

- **Error de autenticación**: Verificar que se haya inicializado correctamente la base de datos
  ```bash
  python initialize_app.py
  ```

- **Token expirado**: Los tokens JWT expiran después de 30 minutos por defecto. La aplicación redirigirá automáticamente a la pantalla de inicio de sesión cuando el token expire.

- **Error en la API de Deepgram**: Verificar que la clave API esté correctamente configurada en el archivo `.env` y que la ruta al archivo sea correcta.

- **Mensaje de error persistente en la transcripción**: Si ves mensajes de error incluso cuando la transcripción fue exitosa, reinicia la aplicación o limpia la caché del navegador. Estos problemas han sido solucionados en la última versión.

- **Problemas con la carga de variables de entorno**: Asegúrate de que el archivo `.env` está en la ubicación correcta y que los archivos `transcriber.py` y `main.py` hacen referencia a la ruta absoluta del archivo.

## Contribución

Las contribuciones son bienvenidas. Para cambios importantes, abre primero un issue para discutir lo que te gustaría cambiar.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.
