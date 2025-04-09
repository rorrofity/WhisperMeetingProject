# Referencias de la API de Whisper Meeting Transcriber

Este documento describe los endpoints disponibles en la API del backend.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Verificar estado del servidor

```
GET /
```

**Respuesta:**
```json
{
  "message": "Whisper Meeting Transcriber API is running"
}
```

### Cargar archivo de audio para transcripción

```
POST /upload-file/
```

**Parámetros:**
- `file`: Archivo de audio en formato .mp3, .mp4, o .wav (requerido)
- `model_size`: Modelo de transcripción a utilizar (opciones: 'nova-3', 'nova-2', 'enhanced', 'base', 'whisper-large')
- `summary_method`: Tipo de modelo para generar resúmenes (opciones: 'local', 'gpt')

**Respuesta:**
```json
{
  "process_id": "uuid-string",
  "message": "Audio file uploaded successfully. Processing..."
}
```

### Verificar estado del proceso

```
GET /status/{process_id}
```

**Respuesta:**
```json
{
  "status": "completed | processing | error",
  "error": "Mensaje de error (si ocurrió alguno)"
}
```

### Obtener resultados

```
GET /results/{process_id}
```

**Respuesta:**
```json
{
  "transcription": "Texto transcrito del audio...",
  "short_summary": "Resumen corto generado",
  "key_points": ["Punto clave 1", "Punto clave 2", ...],
  "action_items": ["Acción 1", "Acción 2", ...]
}
```

### Descargar resultados

```
GET /download/{process_id}
```

**Parámetros:**
- `format`: Formato del archivo de salida (opciones: 'txt', 'pdf')

**Respuesta:**
- Archivo en el formato solicitado con los resultados de la transcripción y resúmenes

## Endpoints de Autenticación y Usuario

### Iniciar sesión

```
POST /api/users/token
```

**Parámetros:**
- `username`: Nombre de usuario
- `password`: Contraseña

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

### Obtener historial de transcripciones

```
GET /api/transcriptions/
```

**Headers:**
- `Authorization`: Bearer token

**Respuesta:**
```json
[
  {
    "id": "uuid-string",
    "title": "Transcripción de audio.mp3",
    "original_filename": "audio.mp3",
    "created_at": "2025-04-09T12:00:00",
    "content": "Texto de la transcripción...",
    "file_path": "/ruta/al/archivo/audio.mp3"
  },
  ...
]
```

## Endpoints para el Modelo de Datos Release 1 (Nuevo)

### Obtener proyectos del usuario

```
GET /api/projects/
```

**Headers:**
- `Authorization`: Bearer token

**Respuesta:**
```json
[
  {
    "id": "uuid-string",
    "name": "Proyecto 1",
    "description": "Descripción del proyecto",
    "created_at": "2025-04-09T12:00:00",
    "updated_at": "2025-04-09T12:30:00"
  },
  ...
]
```

### Crear nuevo proyecto

```
POST /api/projects/
```

**Headers:**
- `Authorization`: Bearer token

**Parámetros:**
```json
{
  "name": "Nombre del proyecto",
  "description": "Descripción del proyecto"
}
```

**Respuesta:**
```json
{
  "id": "uuid-string",
  "name": "Nombre del proyecto",
  "description": "Descripción del proyecto",
  "created_at": "2025-04-09T12:00:00",
  "updated_at": "2025-04-09T12:00:00"
}
```

### Destacar fragmento de transcripción

```
POST /api/highlights/
```

**Headers:**
- `Authorization`: Bearer token

**Parámetros:**
```json
{
  "transcription_id": "uuid-string",
  "text": "Texto destacado",
  "start_offset": 10,
  "end_offset": 50,
  "note": "Nota sobre este destacado",
  "tags": ["importante", "seguimiento"]
}
```

**Respuesta:**
```json
{
  "id": "uuid-string",
  "transcription_id": "uuid-string",
  "text": "Texto destacado",
  "start_offset": 10,
  "end_offset": 50,
  "note": "Nota sobre este destacado",
  "created_at": "2025-04-09T12:00:00",
  "tags": [
    {
      "id": "uuid-string",
      "name": "importante"
    },
    {
      "id": "uuid-string",
      "name": "seguimiento"
    }
  ]
}
```

## Códigos de Estado

- `200`: Operación exitosa
- `400`: Solicitud inválida
- `401`: No autorizado
- `403`: Prohibido
- `404`: Recurso no encontrado
- `500`: Error interno del servidor

## Ejemplos

### Ejemplo de solicitud de transcripción

```bash
curl -X POST http://localhost:8000/upload-file/ \
  -F "file=@./ruta/a/mi/audio.mp3" \
  -F "model_size=nova-3" \
  -F "summary_method=local"
```

### Ejemplo de verificación de estado

```bash
curl -X GET http://localhost:8000/status/123e4567-e89b-12d3-a456-426614174000
```

### Ejemplo de descarga de resultados

```bash
curl -X GET http://localhost:8000/download/123e4567-e89b-12d3-a456-426614174000?format=pdf -o resultados.pdf
```
