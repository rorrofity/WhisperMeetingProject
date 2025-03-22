# Whisper Meeting Transcriber

Sistema local para transcribir archivos de audio y exportar resultados utilizando Deepgram.

## Características Principales

- Carga de archivos de audio (.mp3, .mp4, .wav, .m4a)
- Transcripción automática con la API de Deepgram 
- Procesamiento directo de archivos grandes sin segmentación
- Procesamiento y normalización de audio con FFmpeg
- Descarga de resultados en formato TXT
- Interfaz web moderna con React, Vite y TailwindCSS

## Estructura del Proyecto

```
WhisperMeetingProject/
├── backend/              # API FastAPI para procesamiento
│   ├── main.py           # Punto de entrada principal de la API
│   ├── requirements.txt  # Dependencias de Python
│   ├── .env              # Variables de entorno (API keys, etc.)
│   ├── temp/             # Almacenamiento temporal de archivos
│   └── utils/            # Utilidades para procesamiento
│       ├── __init__.py   
│       ├── audio_processor.py  # Procesamiento de archivos de audio
│       └── transcriber.py      # Transcripción con Deepgram
│
├── frontend/             # Aplicación React con Vite y TailwindCSS
│   ├── src/              # Código fuente de React
│   │   ├── components/   # Componentes de la interfaz
│   │   │   ├── Header.jsx       # Encabezado de la aplicación
│   │   │   ├── Footer.jsx       # Pie de página
│   │   │   └── TranscriptionView.jsx  # Vista de transcripción
│   │   ├── App.jsx       # Componente principal
│   │   ├── main.jsx      # Punto de entrada de React
│   │   └── index.css     # Estilos globales con TailwindCSS
│   ├── index.html        # Plantilla HTML
│   ├── vite.config.js    # Configuración de Vite
│   ├── tailwind.config.js # Configuración de TailwindCSS
│   ├── postcss.config.js # Configuración de PostCSS
│   └── package.json      # Dependencias y scripts
│
├── run.sh                # Script para iniciar todo el sistema
├── start_backend.sh      # Script para iniciar solo el backend
├── start_frontend.sh     # Script para iniciar solo el frontend
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

2. Hacer ejecutable el script de inicio:
   ```bash
   chmod +x run.sh start_backend.sh start_frontend.sh
   ```

3. Ejecutar el script de inicio (instalará todas las dependencias automáticamente):
   ```bash
   ./run.sh
   ```

Si prefieres instalar manualmente:

1. Instalar dependencias del backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Instalar dependencias del frontend:
   ```bash
   cd frontend
   npm install
   ```

## Uso

1. Iniciar el sistema completo con el script:
   ```bash
   ./run.sh
   ```

   O iniciar por separado backend y frontend:
   ```bash
   ./start_backend.sh
   ./start_frontend.sh
   ```

2. Abrir el navegador web y acceder a:
   ```
   http://localhost:5173
   ```

3. Subir un archivo de audio usando la interfaz
4. Esperar a que se complete la transcripción
5. Ver y descargar los resultados

## Configuración de Deepgram

Para utilizar la aplicación, necesitas una clave API de Deepgram:

1. Crear una cuenta en [Deepgram](https://console.deepgram.com/signup)
2. Generar una API key en tu dashboard
3. Añadir la API key en el archivo `backend/.env`:
   ```
   DEEPGRAM_API_KEY=tu_clave_api_aqui
   ```

- Menores costos por hora de audio procesada

**Importante**: Se requiere una clave API de Deepgram para usar el servicio de transcripción.

### Modelos de Transcripción

- **Nova-2**: Recomendado para casos multilingües, tiene excelente soporte para español y otros idiomas. Según la documentación oficial de Deepgram, Nova-2 tiene una tasa de preferencia 34% mayor que Whisper en pruebas de usuarios.
- **Nova-3**: Modelo más reciente y preciso, pero con limitaciones en soporte multilingüe (solo disponible en beta para idiomas diferentes al inglés).
- **Whisper-large**: Buena opción para casos multilingües, pero es menos eficiente y más lento que los modelos nativos de Deepgram.
- **Enhanced**: Modelo balanceado en velocidad y precisión.
- **Base**: Más rápido pero menos preciso.

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
```

## API REST

El sistema proporciona una API REST para integraciones. Los endpoints principales:

- `POST /upload-file/`: Sube un archivo y obtiene transcripción
- `GET /status/{process_id}`: Verifica el estado de la transcripción
- `GET /results/{process_id}`: Obtiene resultados de la transcripción
- `GET /download/{process_id}?format={txt}`: Descarga resultados

Ver [API_REFERENCE.md](./API_REFERENCE.md) para documentación completa.

## Personalización y Extensión

### Frontend

- Modificar estilos: Editar `frontend/src/index.css` y `tailwind.config.js`
- Añadir componentes: Crear nuevos componentes en `frontend/src/components/`

### Backend

- Cambiar modelos de Deepgram: Editar `TRANSCRIPTION_MODEL` en `.env`
- Optimizar procesamiento de audio: Modificar `backend/utils/audio_processor.py`
- Ajustar parámetros de Deepgram: Editar configuraciones en `backend/utils/transcriber.py`

## Solución de Problemas

- **Error de FFmpeg**: Instalar FFmpeg si no está presente
  ```bash
  sudo apt update && sudo apt install -y ffmpeg
  ```

- **Error de transcripción**: Asegúrate de que la API key de Deepgram sea válida y está configurada en el archivo `.env`

- **Error "Nova-3 multilingual support is currently available only in beta"**: Este error ocurre porque el modelo Nova-3 no tiene soporte completo para idiomas distintos al inglés en la API estándar. Cambia a Nova-2 en el archivo `.env`:
  ```
  TRANSCRIPTION_MODEL=nova-2
  ```

- **Error "not found"**: Si obtienes un error 404, verifica que los servidores de backend y frontend estén ejecutándose correctamente

## Tecnologías Utilizadas

- **Backend**: FastAPI, Deepgram, FFmpeg
- **Frontend**: React, Vite, TailwindCSS, FilePond
- **Procesamiento**: Python, FFmpeg, Deepgram API

## Créditos

- Deepgram: [Deepgram API](https://developers.deepgram.com/)
- Frontend desarrollado con React, Vite y TailwindCSS

## Notas sobre Rendimiento

Según la documentación de Deepgram y las pruebas realizadas:

1. **Nova-2** ofrece una excelente precisión multilingüe con soporte completo para español y otros idiomas.
   - Se utiliza la variante "es-419" específica para Latinoamérica, que mejora significativamente el reconocimiento de acentos y expresiones regionales.
2. **Whisper-large** es una alternativa viable para transcripción multilingüe, pero es menos eficiente y más lento que los modelos nativos de Deepgram.
3. **Nova-3** tiene la mejor precisión general pero actualmente solo ofrece soporte completo para inglés en la API estándar (soporte multilingüe solo en beta).

Nova-2 es actualmente la mejor opción para transcribir contenido en español latinoamericano, combinando buena precisión con velocidad de procesamiento.
