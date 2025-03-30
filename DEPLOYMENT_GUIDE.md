# Guía de Despliegue en DigitalOcean

Esta guía proporciona instrucciones sobre cómo desplegar el proyecto Whisper Meeting Transcriber en un Droplet de DigitalOcean y cómo mantenerlo.

## Información del Servidor

- **Proveedor**: DigitalOcean
- **Tipo**: Droplet (Ubuntu 22.04 LTS)
- **IP**: 134.199.218.48
- **Puerto SSH**: 2222
- **Usuario**: root

## Conectarse al Servidor

Para conectarse al servidor desde WSL o Linux/macOS:

```bash
ssh -p 2222 root@134.199.218.48
```

## Iniciar los Servicios

Si necesitas reiniciar el servidor o los servicios se han detenido, sigue estos pasos:

### 1. Iniciar el Backend

```bash
# Navegar al directorio del backend
cd /var/www/whisper-meeting/backend

# Activar el entorno virtual
source venv/bin/activate

# Iniciar el servicio con systemd
sudo systemctl start whisper-backend
sudo systemctl status whisper-backend  # Verificar estado
```

### 2. Reiniciar Nginx (Frontend)

```bash
sudo systemctl restart nginx
sudo systemctl status nginx  # Verificar estado
```

## Verificar Logs

Si algo no funciona correctamente, revisa los logs:

```bash
# Logs del backend
sudo journalctl -u whisper-backend -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Actualizar el Proyecto

Para actualizar el proyecto con nuevos cambios:

```bash
# Navegar al directorio del proyecto
cd /var/www/whisper-meeting

# Si usas git
git pull

# Si actualizas manualmente
# (Desde tu máquina local)
scp -P 2222 -r ./archivos_actualizados root@134.199.218.48:/var/www/whisper-meeting

# Reiniciar servicios después de actualizar
sudo systemctl restart whisper-backend
sudo systemctl restart nginx
```

## Base de Datos

La base de datos SQLite se encuentra en:

```
/var/www/whisper-meeting/backend/database/data.db
```

Para hacer un backup:

```bash
cp /var/www/whisper-meeting/backend/database/data.db /var/backups/whisper-meeting/data_$(date +"%Y%m%d").db
```

## Archivos Temporales

Los archivos de audio cargados se almacenan temporalmente en:

```
/var/www/whisper-meeting/backend/temp/
```

Para limpiar archivos antiguos:

```bash
find /var/www/whisper-meeting/backend/temp/ -type f -mtime +7 -delete
```

## Certificado SSL (HTTPS)

Si has configurado SSL con Certbot, puedes renovar los certificados con:

```bash
sudo certbot renew
```

## Problemas Comunes y Soluciones

### El sitio web no carga:
```bash
sudo systemctl restart nginx
sudo systemctl restart whisper-backend
```

### Errores en las subidas de archivos:
```bash
# Verificar permisos
sudo chown -R www-data:www-data /var/www/whisper-meeting/backend/temp
sudo chmod 755 /var/www/whisper-meeting/backend/temp
```

### Problemas con la API de Deepgram:
```bash
# Verificar la clave API en .env
nano /var/www/whisper-meeting/backend/.env
```

## Contacto y Soporte

Si necesitas ayuda adicional, puedes:
- Revisar la documentación del proyecto
- Verificar la configuración en los archivos de entorno
- Consultar los logs para información detallada sobre los errores
