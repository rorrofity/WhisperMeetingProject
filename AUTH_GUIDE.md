# Guía del Sistema de Autenticación

En esta guía se detalla cómo utilizar el sistema de autenticación implementado en la aplicación de transcripción de reuniones.

## Características

- Autenticación basada en tokens JWT (JSON Web Tokens)
- Registro de usuarios con validación de correo electrónico y nombre de usuario
- Acceso seguro a los endpoints protegidos
- Almacenamiento del historial de transcripciones por usuario

## Inicialización

Antes de empezar a utilizar el sistema de autenticación, debes inicializar la base de datos y crear un usuario:

```bash
# Para inicializar la base de datos
python3 -m initialize_app

# Para inicializar y crear un usuario administrador
python3 -m initialize_app --create-user

# Para especificar datos personalizados para el usuario
python3 -m initialize_app --create-user --username miusuario --email micorreo@ejemplo.com --password micontraseña
```

## Endpoints de Autenticación

### Registro de Usuario

Para registrar un nuevo usuario:

```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "miusuario",
    "password": "micontraseña"
  }'
```

### Inicio de Sesión

Para iniciar sesión y obtener un token JWT:

```bash
curl -X POST "http://localhost:8000/users/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=miusuario&password=micontraseña"
```

La respuesta incluirá un token de acceso:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Uso del Token para Acceder a Recursos Protegidos

Una vez que tienes el token, debes incluirlo en todas tus solicitudes a endpoints protegidos usando el encabezado `Authorization`:

```bash
curl -X POST "http://localhost:8000/upload-file/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "file=@/ruta/a/tu/archivo.mp3"
```

## Endpoints de Transcripciones Asociadas al Usuario

### Ver todas las transcripciones del usuario actual

```bash
curl -X GET "http://localhost:8000/transcriptions/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Ver una transcripción específica

```bash
curl -X GET "http://localhost:8000/transcriptions/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Crear una transcripción manualmente

```bash
curl -X POST "http://localhost:8000/transcriptions/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Transcripción Manual",
    "original_filename": "audio.mp3",
    "file_path": "/ruta/al/archivo.mp3",
    "content": "Texto de la transcripción..."
  }'
```

### Eliminar una transcripción

```bash
curl -X DELETE "http://localhost:8000/transcriptions/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Integración con el Frontend

Para integrar el sistema de autenticación con el frontend (React), debes:

1. Crear formularios de registro e inicio de sesión
2. Almacenar el token en localStorage o en un estado global (como Redux)
3. Incluir el token en todas las peticiones a la API con axios:

```javascript
import axios from 'axios';

// Configurar axios para incluir el token en todas las peticiones
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Ejemplo de función de inicio de sesión
async function login(username, password) {
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await axios.post('http://localhost:8000/users/token', formData);
    const { access_token } = response.data;
    
    // Guardar el token
    localStorage.setItem('token', access_token);
    
    return true;
  } catch (error) {
    console.error('Error en inicio de sesión:', error);
    return false;
  }
}
```

## Seguridad

- El token JWT expira después de 30 minutos (configurable en las variables de entorno)
- Las contraseñas se almacenan hasheadas con bcrypt
- Se realizan validaciones de email y nombre de usuario para prevenir duplicados

## Solución de problemas comunes

### El token es rechazado

- Verifica que el token no haya expirado
- Asegúrate de incluir el prefijo "Bearer" seguido de un espacio antes del token
- Comprueba que estás usando el token más reciente

### No puedo registrarme

- El email y el nombre de usuario deben ser únicos
- Asegúrate de que el email tenga un formato válido

### No veo mis transcripciones

- Confirma que estás autenticado correctamente
- Verifica que las transcripciones se estén guardando correctamente en la base de datos
