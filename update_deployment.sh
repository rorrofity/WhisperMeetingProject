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
echo "=== Preparando actualización y protegiendo bases de datos ==="
cd /var/www/whisper-meeting

# Crear copia de seguridad de la base de datos antes de cualquier operación
timestamp=$(date +"%Y%m%d_%H%M%S")
echo "Creando copia de seguridad de la base de datos actual..."
cp -f transcriptions.db "transcriptions.db.pre_update_${timestamp}" 2>/dev/null || echo "No se encontró base de datos para respaldar"

# Proteger archivos de base de datos para que no sean sobrescritos por git
echo "Configurando Git para ignorar cambios en bases de datos..."
git update-index --skip-worktree transcriptions.db 2>/dev/null || echo "No se encontró transcriptions.db en git"
git update-index --skip-worktree transcriptions.db.backup* 2>/dev/null || echo "No se encontraron backups en git"

echo "=== Actualizando desde GitHub ==="
git pull

# Restaurar protección después del pull
echo "Verificando integridad de la base de datos después de actualizar..."
if [ ! -f transcriptions.db ] && [ -f "transcriptions.db.pre_update_${timestamp}" ]; then
  echo "Restaurando base de datos desde copia de seguridad..."
  cp -f "transcriptions.db.pre_update_${timestamp}" transcriptions.db
fi

# Si hay cambios en el backend
cd /var/www/whisper-meeting/backend
source venv/bin/activate
pip install -r requirements.txt


# Si hay cambios en el frontend
cd /var/www/whisper-meeting/frontend
npm install
npm run build

# NOTA: La configuración de Nginx ya está personalizada en el servidor con soporte HTTPS
# Se ha comentado el código que sobrescribe esta configuración para evitar perder los cambios
# ===============================================================================
# Actualizar configuración de Nginx
echo "=== Verificando configuración de Nginx (NO sobrescribiendo) ==="
# if [ -d "/var/www/whisper-meeting/nginx/conf" ]; then
#   sudo cp /var/www/whisper-meeting/nginx/conf/whisper-meeting /etc/nginx/sites-available/whisper-meeting
#   sudo nginx -t && sudo systemctl reload nginx
# fi

# Reiniciar servicios
systemctl restart whisper-backend
systemctl restart nginx

echo "=== Actualización completada! ==="
echo "Tu aplicación actualizada está disponible en: http://134.199.218.48"
ENDSSH

echo "=== Proceso de actualización finalizado ==="
