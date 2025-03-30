#!/bin/bash
# Script para actualizar WhisperMeetingProject en DigitalOcean

echo "=== Sincronizando con GitHub ==="
# Commit y push de los cambios locales
git add .
git commit -m "Actualización: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin master

echo "=== Conectando al servidor para actualizar ==="
# Conexión SSH y comandos remotos para actualizar
ssh -p 2222 root@134.199.218.48 << 'ENDSSH'
echo "=== Actualizando desde GitHub ==="
cd /var/www/whisper-meeting
git pull

# Si hay cambios en el backend
cd /var/www/whisper-meeting/backend
source venv/bin/activate
pip install -r requirements.txt

# Si hay cambios en el frontend
cd /var/www/whisper-meeting/frontend
npm install
npm run build

# Reiniciar servicios
systemctl restart whisper-backend
systemctl restart nginx

echo "=== Actualización completada! ==="
echo "Tu aplicación actualizada está disponible en: http://134.199.218.48"
ENDSSH

echo "=== Proceso de actualización finalizado ==="
