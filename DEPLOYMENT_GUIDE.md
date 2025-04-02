# Guía de Despliegue en DigitalOcean

Esta guía proporciona instrucciones sobre cómo desplegar el proyecto Whisper Meeting Transcriber en un Droplet de DigitalOcean y cómo mantenerlo.

## Información del Servidor

- **Proveedor**: DigitalOcean
- **Tipo**: Droplet (Ubuntu 22.04 LTS)
- **IP**: 134.199.218.48
- **Puerto SSH**: 2222
- **Usuario**: root

## Método de Despliegue Automatizado (Recomendado)

Para un despliegue completo y automatizado, utiliza el script de despliegue incluido:

```bash
# Desde tu máquina local con WSL
ssh -p 2222 root@134.199.218.48 << 'ENDSSH'
echo "=== Conexión establecida con el servidor ==="

# Crear directorio del proyecto
mkdir -p /var/www/whisper-meeting
cd /var/www/whisper-meeting

# Eliminar contenido previo si existe
rm -rf *

# Clonar repositorio
git clone https://github.com/rorrofity/WhisperMeetingProject.git .

# Configurar backend
cd /var/www/whisper-meeting/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Crear archivo .env
cat > .env << 'ENDENV'
DEEPGRAM_API_KEY=tu_clave_api_aqui
TRANSCRIPTION_MODEL=nova-2
LANGUAGE=es-419
HOST=0.0.0.0
PORT=8000
JWT_SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENDENV

# Configurar frontend
cd /var/www/whisper-meeting/frontend
npm install
npm run build

# Configurar servicio para el backend
cat > /etc/systemd/system/whisper-backend.service << 'ENDSERVICE'
[Unit]
Description=Whisper Meeting Transcriber Backend
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/whisper-meeting/backend
Environment="PATH=/var/www/whisper-meeting/backend/venv/bin"
Environment="PYTHONPATH=/var/www/whisper-meeting/backend"
ExecStart=/var/www/whisper-meeting/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
ENDSERVICE

# Configurar Nginx
cat > /etc/nginx/sites-available/whisper-meeting << 'ENDNGINX'
server {
    listen 80;
    server_name _;

    location / {
        root /var/www/whisper-meeting/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
}
ENDNGINX

# Activar configuración de Nginx
ln -sf /etc/nginx/sites-available/whisper-meeting /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Iniciar servicio backend
systemctl daemon-reload
systemctl enable whisper-backend
systemctl restart whisper-backend

# Inicializar la base de datos y crear usuario
cd /var/www/whisper-meeting
python initialize_app.py --create-user --username nuevouser --email tu@ejemplo.com --password TuContraseña123!

# Configurar permisos para archivos temporales
mkdir -p /var/www/whisper-meeting/backend/temp
chown -R www-data:www-data /var/www/whisper-meeting/backend/temp
chmod 755 /var/www/whisper-meeting/backend/temp

echo "=== Despliegue completado! ==="
echo "Tu aplicación ahora está disponible en: http://134.199.218.48"
ENDSSH
```

## Actualizaciones de la Aplicación 

Para futuras actualizaciones, utiliza el script `update_deployment.sh` incluido en el repositorio:

```bash
# Desde tu máquina local en el directorio del proyecto
chmod +x update_deployment.sh
./update_deployment.sh
```

Este script automatiza todo el proceso de actualización:
1. Sincroniza cambios locales con GitHub
2. Conecta con el servidor
3. Actualiza el código desde GitHub
4. Reinstala dependencias si es necesario
5. Reconstruye el frontend
6. Reinicia los servicios

## Método de Despliegue Manual (Alternativo)

Si prefieres hacer el despliegue paso a paso, sigue estas instrucciones:

### 1. Conectarse al Servidor

```bash
ssh -p 2222 root@134.199.218.48
```

### 2. Iniciar los Servicios

Si necesitas reiniciar el servidor o los servicios se han detenido:

#### Iniciar el Backend

```bash
# Navegar al directorio del backend
cd /var/www/whisper-meeting/backend

# Activar el entorno virtual
source venv/bin/activate

# Iniciar el servicio con systemd
systemctl start whisper-backend
systemctl status whisper-backend  # Verificar estado
```

#### Reiniciar Nginx (Frontend)

```bash
systemctl restart nginx
systemctl status nginx  # Verificar estado
```

## Configuración de PYTHONPATH para Backend

```bash
sudo sed -i '/ExecStart/i Environment="PYTHONPATH=/var/www/whisper-meeting/backend"' /etc/systemd/system/whisper-backend.service
sudo systemctl daemon-reload
```

> **IMPORTANTE**: La variable PYTHONPATH es crítica para que el backend funcione. Esta configuración permite que todas las importaciones absolutas sin prefijo "backend" funcionen correctamente. Asegúrate de que todos los archivos Python sigan las reglas de importación explicadas en el README.md.

## Verificar Logs

Si algo no funciona correctamente, revisa los logs:

```bash
# Logs del backend
journalctl -u whisper-backend -f

# Logs de Nginx
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

## Problemas Comunes y Soluciones

### El sitio web no carga:
```bash
systemctl restart nginx
systemctl restart whisper-backend
```

### Errores en las subidas de archivos:
```bash
# Verificar permisos
chown -R www-data:www-data /var/www/whisper-meeting/backend/temp
chmod 755 /var/www/whisper-meeting/backend/temp
```

### Problemas con la API de Deepgram:
```bash
# Verificar la clave API en .env
nano /var/www/whisper-meeting/backend/.env
```

### Problemas de autenticación/inicio de sesión:
```bash
# Crear un nuevo usuario
cd /var/www/whisper-meeting
python initialize_app.py --create-user --username nuevouser --email tu@ejemplo.com --password NuevaContraseña123!
