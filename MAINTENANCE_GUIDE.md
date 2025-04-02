# Guía de Mantenimiento para WhisperMeetingProject

Esta guía proporciona consejos, buenas prácticas y procedimientos para el mantenimiento continuado de tu aplicación Whisper Meeting Transcriber desplegada en DigitalOcean.

## Respaldos y Recuperación

### Respaldo de Base de Datos

La base de datos SQLite se encuentra en `/var/www/whisper-meeting/backend/database/data.db`. Es recomendable hacer respaldos periódicos:

```bash
# Configuración inicial (ejecutar una sola vez)
ssh -p 2222 root@134.199.218.48 "mkdir -p /var/backups/whisper-meeting"

# Crear respaldo manual
ssh -p 2222 root@134.199.218.48 "cp /var/www/whisper-meeting/backend/database/data.db /var/backups/whisper-meeting/data_$(date +"%Y%m%d").db"
```

### Respaldo Automatizado

Puedes configurar respaldos automáticos usando cron:

```bash
# En el servidor
echo '#!/bin/bash
cp /var/www/whisper-meeting/backend/database/data.db /var/backups/whisper-meeting/data_$(date +"%Y%m%d").db
find /var/backups/whisper-meeting/ -name "data_*.db" -mtime +30 -delete' > /etc/cron.weekly/backup-whisper-db
chmod +x /etc/cron.weekly/backup-whisper-db
```

### Restauración de Respaldos

Para restaurar un respaldo:

```bash
# En el servidor
systemctl stop whisper-backend
cp /var/backups/whisper-meeting/data_[FECHA].db /var/www/whisper-meeting/backend/database/data.db
systemctl start whisper-backend
```

## Gestión de Archivos Temporales

Los archivos de audio cargados se almacenan en `/var/www/whisper-meeting/backend/temp/`. Para evitar que ocupen demasiado espacio:

```bash
# Eliminar archivos de más de 7 días
ssh -p 2222 root@134.199.218.48 "find /var/www/whisper-meeting/backend/temp/ -type f -mtime +7 -delete"
```

### Limpieza Automatizada

```bash
# En el servidor
echo '#!/bin/bash
find /var/www/whisper-meeting/backend/temp/ -type f -mtime +7 -delete' > /etc/cron.daily/cleanup-whisper-temp
chmod +x /etc/cron.daily/cleanup-whisper-temp
```

## Monitoreo y Solución de Problemas

### Verificar Estado de Servicios

```bash
# Verificar el backend
ssh -p 2222 root@134.199.218.48 "systemctl status whisper-backend"

# Verificar Nginx
ssh -p 2222 root@134.199.218.48 "systemctl status nginx"
```

### Revisar Uso de Recursos

```bash
# Verificar uso de disco
ssh -p 2222 root@134.199.218.48 "df -h"

# Verificar uso de memoria y CPU
ssh -p 2222 root@134.199.218.48 "top -b -n 1"
```

### Logs y Depuración

```bash
# Logs del backend
ssh -p 2222 root@134.199.218.48 "journalctl -u whisper-backend -n 100"

# Logs de Nginx
ssh -p 2222 root@134.199.218.48 "tail -n 100 /var/log/nginx/error.log"
```

## Solución de Problemas

### Errores de Importación de Módulos Python

Si encuentras errores del tipo `ModuleNotFoundError: No module named 'backend'` o similares, es posible que necesites ajustar la configuración del servicio systemd:

```bash
# Verificar que PYTHONPATH esté configurado correctamente
ssh -p 2222 root@134.199.218.48 "grep PYTHONPATH /etc/systemd/system/whisper-backend.service"

# Si no está presente, actualizar el servicio
ssh -p 2222 root@134.199.218.48 "sed -i '/Environment=\"PATH/a Environment=\"PYTHONPATH=\/var\/www\/whisper-meeting\/backend\"' /etc/systemd/system/whisper-backend.service && systemctl daemon-reload && systemctl restart whisper-backend"
```

La variable `PYTHONPATH` es crítica para que Python pueda encontrar módulos en el proyecto, permitiendo tanto importaciones absolutas como relativas.

## Problemas Comunes y Soluciones

### Error 502 Bad Gateway en el inicio de sesión
Si aparece un error 502 Bad Gateway al intentar iniciar sesión, es probable que haya un problema con las importaciones en Python. 

**Solución**: 
1. Asegúrate de que todos los archivos Python usen importaciones absolutas sin el prefijo "backend". 
2. Nunca uses importaciones relativas con ".." en este proyecto cuando se despliega con Gunicorn.
3. El patrón correcto para importaciones es:
   ```python
   # Correcto
   from models.models import User
   from database.connection import get_db
   
   # Incorrecto - no usar
   from backend.models.models import User
   from ..database.connection import get_db
   ```
4. Si necesitas hacer cambios, actualiza el servidor con:
   ```
   ssh -p 2222 root@134.199.218.48 "cd /var/www/whisper-meeting && git pull && systemctl restart whisper-backend"
   ```

### Conflictos con PYTHONPATH
Si encuentras errores del tipo `ModuleNotFoundError: No module named 'backend'` o similares, es posible que necesites ajustar la configuración del servicio systemd:

```bash
# Verificar que PYTHONPATH esté configurado correctamente
ssh -p 2222 root@134.199.218.48 "grep PYTHONPATH /etc/systemd/system/whisper-backend.service"

# Si no está presente, actualizar el servicio
ssh -p 2222 root@134.199.218.48 "sed -i '/Environment=\"PATH/a Environment=\"PYTHONPATH=\/var\/www\/whisper-meeting\/backend\"' /etc/systemd/system/whisper-backend.service && systemctl daemon-reload && systemctl restart whisper-backend"
```

La variable `PYTHONPATH` es crítica para que Python pueda encontrar módulos en el proyecto, permitiendo tanto importaciones absolutas como relativas.

## Actualizaciones de Seguridad

### Actualizar el Sistema

```bash
ssh -p 2222 root@134.199.218.48 "apt update && apt upgrade -y"
```

### Verificar Vulnerabilidades de Dependencias

```bash
# Para el backend
ssh -p 2222 root@134.199.218.48 "cd /var/www/whisper-meeting/backend && source venv/bin/activate && pip list --outdated"

# Para el frontend
ssh -p 2222 root@134.199.218.48 "cd /var/www/whisper-meeting/frontend && npm audit"
```

## Gestión de Usuarios

### Crear Nuevo Usuario

```bash
ssh -p 2222 root@134.199.218.48 "cd /var/www/whisper-meeting && python initialize_app.py --create-user --username nuevousuario --email nuevo@ejemplo.com --password ContraseñaSegura123!"
```

### Cambiar Contraseña (si implementas esta funcionalidad)

Si implementas una función para cambiar contraseñas, podrías hacerlo a nivel de base de datos:

```bash
# Este es un ejemplo conceptual - necesitarías adaptar la consulta SQL al modelo exacto de tu base de datos
ssh -p 2222 root@134.199.218.48 "cd /var/www/whisper-meeting && sqlite3 backend/database/data.db \"UPDATE users SET hashed_password='NUEVO_HASH' WHERE username='usuario';\""
```

## Optimización

### Rendimiento del Servidor

Si notas lentitud:

```bash
# Ajustar trabajadores de Gunicorn
ssh -p 2222 root@134.199.218.48 "sed -i 's/ExecStart=.*gunicorn.*/ExecStart=\/var\/www\/whisper-meeting\/backend\/venv\/bin\/gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000/' /etc/systemd/system/whisper-backend.service && systemctl daemon-reload && systemctl restart whisper-backend"
```

### Caché de Nginx

Para mejorar el rendimiento:

```bash
ssh -p 2222 root@134.199.218.48 "cat > /etc/nginx/conf.d/cache.conf << 'EOL'
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=whisper_cache:10m max_size=100m inactive=60m;
EOL"

ssh -p 2222 root@134.199.218.48 "sed -i '/location \/ {/a\        expires 1d;\n        add_header Cache-Control \"public\";' /etc/nginx/sites-available/whisper-meeting && systemctl restart nginx"
```

## Escalado de Recursos

Si necesitas escalar:

1. Ve al panel de control de DigitalOcean
2. Selecciona tu Droplet
3. Haz clic en "Resize" para aumentar CPU/RAM/Almacenamiento
4. Sigue las instrucciones para redimensionar

## Configuración de Dominio Personalizado

Si quieres usar un dominio propio:

1. Compra un dominio en un registrador (GoDaddy, Namecheap, etc.)
2. Configura los registros DNS para apuntar a tu Droplet:
   - Añade registro A: `tudominio.com` → 134.199.218.48
   - Añade registro A: `www.tudominio.com` → 134.199.218.48

3. Actualiza la configuración de Nginx:
```bash
ssh -p 2222 root@134.199.218.48 "sed -i 's/server_name _;/server_name tudominio.com www.tudominio.com;/' /etc/nginx/sites-available/whisper-meeting && systemctl restart nginx"
```

## Configuración de HTTPS

Para añadir HTTPS con Let's Encrypt:

```bash
# Instalar Certbot
ssh -p 2222 root@134.199.218.48 "apt install -y certbot python3-certbot-nginx"

# Obtener certificado
ssh -p 2222 root@134.199.218.48 "certbot --nginx -d tudominio.com -d www.tudominio.com"
```

## Referencias y Recursos Útiles

- [Documentación de DigitalOcean](https://docs.digitalocean.com)
- [Documentación de Nginx](https://nginx.org/en/docs/)
- [Documentación de SQLite](https://www.sqlite.org/docs.html)
- [Documentación de Deepgram](https://developers.deepgram.com/docs/)
