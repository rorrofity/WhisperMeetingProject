# Guía de Flujo de Desarrollo para Whisper Meeting Transcriber

Este documento describe el flujo de trabajo recomendado para el desarrollo continuo de la aplicación Whisper Meeting Transcriber, desde el desarrollo local hasta el despliegue en producción.

## 1. Entorno de Desarrollo Local

### Configuración Inicial

1. **Clonar el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd WhisperMeetingProject
   ```

2. **Configurar variables de entorno**:
   - Crea un archivo `.env` en la raíz del proyecto.
   - Copia el contenido de `.env.example` (si existe) o asegúrate de incluir:
     ```
     DEEPGRAM_API_KEY=tu_clave_api
     TRANSCRIPTION_MODEL=nova-2
     LANGUAGE=es
     JWT_SECRET_KEY=un_secreto_seguro
     ACCESS_TOKEN_EXPIRE_MINUTES=30
     ```

3. **Iniciar el entorno de desarrollo**:
   - En entorno WSL:
     ```bash
     python3 dev_setup.py
     ```
   - Este script:
     - Configura automáticamente PYTHONPATH
     - Verifica/inicializa la base de datos
     - Inicia el servidor backend y frontend

### Desarrollo de Nuevas Funcionalidades

1. **Crear una rama para la nueva funcionalidad**:
   ```bash
   git checkout -b feature/nombre-de-la-funcionalidad
   ```

2. **Desarrollar y probar localmente**:
   - Utiliza `dev_setup.py` para mantener tu entorno de desarrollo activo
   - Realiza cambios progresivos y prueba constantemente
   - Mantén tu código limpio y bien documentado

3. **Pruebas antes de hacer commit**:
   - Verifica que todas las funcionalidades existentes siguen funcionando
   - Prueba la nueva funcionalidad en diferentes escenarios
   - Verifica que no hay errores en la consola

## 2. Pruebas Pre-Despliegue

Antes de desplegar a producción, realiza estas verificaciones:

1. **Pruebas de integración**:
   - Verifica que los componentes frontend y backend trabajan correctamente juntos
   - Prueba los flujos completos de usuarios (registro, login, transcripción)

2. **Pruebas de compatibilidad**:
   - Verifica que cualquier nueva dependencia es compatible con el entorno de producción
   - Documenta cualquier nueva dependencia en `requirements.txt` o `package.json`

3. **Revisión de código**:
   - Realiza una auto-revisión del código para identificar problemas potenciales
   - Si trabajas en equipo, solicita una revisión de código de otro desarrollador

4. **Lista de verificación final**:
   - [ ] El código está bien documentado
   - [ ] No hay credenciales hardcodeadas
   - [ ] Se han actualizado los archivos README si es necesario
   - [ ] Los nuevos endpoints están protegidos adecuadamente
   - [ ] La aplicación maneja correctamente los errores
   - [ ] La nueva funcionalidad es compatible con el resto de la aplicación

## 3. Proceso de Despliegue

### Preparación para el Despliegue

1. **Fusionar cambios a la rama principal**:
   ```bash
   git checkout main
   git merge feature/nombre-de-la-funcionalidad
   git push origin main
   ```

2. **Actualizar la documentación si es necesario**:
   - Actualiza README.md, MAINTENANCE_GUIDE.md u otros documentos relevantes
   - Documenta cualquier nuevo proceso o configuración necesaria

### Despliegue al Servidor

1. **Utiliza el script de despliegue**:
   ```bash
   ./update_deployment.sh
   ```
   Este script:
   - Sincroniza los archivos actualizados con el servidor
   - Reinicia los servicios necesarios

2. **Verificación post-despliegue**:
   - Accede a la aplicación en producción (http://134.199.218.48)
   - Verifica que todas las funcionalidades (nuevas y existentes) funcionan correctamente
   - Revisa los logs del servidor para detectar posibles errores:
     ```bash
     ssh -p 2222 usuario@134.199.218.48 "tail -f /var/log/whisper-meeting/app.log"
     ```

3. **Rollback en caso de problemas**:
   - Si detectas problemas graves, considera restaurar una versión anterior:
     ```bash
     ssh -p 2222 usuario@134.199.218.48 "cd /path/to/app && git reset --hard <commit-anterior>"
     ```
   - Reinicia los servicios después del rollback

## 4. Mejores Prácticas para el Desarrollo Continuo

### Importaciones en Python

- **Utiliza las importaciones flexibles implementadas**:
  - Las importaciones están configuradas para funcionar tanto en entorno local como en servidor
  - Ejemplo:
    ```python
    try:
        from models.models import User
    except ImportError:
        try:
            from backend.models.models import User
        except ImportError:
            from WhisperMeetingProject.backend.models.models import User
    ```

### Gestión de la Base de Datos

- **Evolución del esquema**:
  - Si necesitas modificar el esquema de la base de datos, considera usar Alembic para migraciones
  - Documenta cualquier cambio en el esquema

### Seguridad

- **Autenticación y Autorización**:
  - Utiliza siempre el sistema JWT implementado para proteger rutas sensibles
  - No almacenes secretos en el código fuente
  - Utiliza variables de entorno para configuraciones sensibles

### Depuración

- **Logs**:
  - Utiliza el sistema de logging implementado
  - Añade logs informativos y de errores donde sea necesario
  - No dejes logs de depuración en el código de producción

### Frontend

- **Componentes React**:
  - Mantén los componentes pequeños y reutilizables
  - Utiliza el contexto de autenticación para gestionar el estado de usuario
  - Implementa interceptores para manejar errores de JWT

## 5. Consejos Específicos para WSL

- **Problemas de permisos**:
  - Si encuentras problemas de permisos en WSL, verifica los permisos de archivos
  - Utiliza `chmod` cuando sea necesario

- **Reinicio del entorno**:
  - Si encuentras problemas con el entorno WSL, considera:
    ```bash
    wsl --shutdown
    wsl
    ```

## 6. Colaboración

- **Control de versiones**:
  - Mantén commits pequeños y descriptivos
  - Utiliza ramas para nuevas funcionalidades y correcciones de errores
  - Considera implementar un flujo de GitFlow para proyectos más grandes

- **Documentación**:
  - Documenta todas las APIs nuevas
  - Actualiza la documentación existente cuando cambies el comportamiento

---

Siguiendo este flujo de trabajo, podrás desarrollar nuevas funcionalidades de manera segura y eficiente, manteniendo la estabilidad del sistema en producción.
