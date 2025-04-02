#!/bin/bash
# Script para arreglar el servicio whisper-backend modificando el archivo de servicio systemd

# Crear archivo de servicio actualizado en el home del usuario
cat > ~/whisper-backend.service << 'EOF'
[Unit]
Description=Whisper Meeting Transcriber Backend
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/whisper-meeting/backend
Environment="PATH=/var/www/whisper-meeting/backend/venv/bin"
Environment="PYTHONPATH=/var/www/whisper-meeting/backend"
ExecStart=/var/www/whisper-meeting/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Mover el archivo al directorio de systemd y reiniciar el servicio
mv ~/whisper-backend.service /etc/systemd/system/
systemctl daemon-reload
systemctl restart whisper-backend
systemctl status whisper-backend
