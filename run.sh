#!/bin/bash

# Colores para la salida en terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== Iniciando Whisper Meeting Transcriber =====${NC}"

# Verificar si FFmpeg está instalado
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}FFmpeg no está instalado. Por favor, instálalo con:${NC}"
    echo "sudo apt update && sudo apt install -y ffmpeg"
    exit 1
fi

# Crear directorios temporales si no existen
mkdir -p backend/temp

# Comprobar si Python y PIP están instalados
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python3 no está instalado. Por favor, instálalo con:${NC}"
    echo "sudo apt update && sudo apt install -y python3 python3-pip"
    exit 1
fi

# Comprobar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js no está instalado. Por favor, instálalo con:${NC}"
    echo "curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -"
    echo "sudo apt-get install -y nodejs"
    exit 1
fi

# Comprobar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creando entorno virtual de Python...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias del backend
echo -e "${GREEN}Instalando dependencias del backend...${NC}"
pip install -r backend/requirements.txt

# Instalar dependencias del frontend
echo -e "${GREEN}Instalando dependencias del frontend...${NC}"
cd frontend
npm install
cd ..

# Eliminar procesos anteriores si existen
echo -e "${GREEN}Limpiando procesos previos...${NC}"
# Intentar matar cualquier proceso de uvicorn o vite en ejecución
pkill -f "uvicorn backend.main:app" || true
pkill -f "npm run dev" || true
sleep 2  # Esperar a que los procesos terminen

# Iniciar el backend
echo -e "${GREEN}Iniciando el servidor backend...${NC}"
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend_log.txt 2>&1 &
BACKEND_PID=$!
cd ..

# Esperar a que el backend esté listo
echo -e "${YELLOW}Esperando a que el servidor backend esté listo...${NC}"
sleep 5

# Iniciar el frontend
echo -e "${GREEN}Iniciando el servidor frontend...${NC}"
cd frontend
npm run dev > ../frontend_log.txt 2>&1 &
FRONTEND_PID=$!
cd ..

# Función de limpieza al cerrar
cleanup() {
    echo -e "${YELLOW}Deteniendo servidores...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}¡Servidores detenidos!${NC}"
    exit 0
}

# Registrar la función de limpieza para señales de interrupción
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}Servidores iniciados:${NC}"
echo -e "Backend: ${YELLOW}http://localhost:8000${NC}"
echo -e "Frontend: ${YELLOW}http://localhost:5173${NC}"
echo -e "${GREEN}Presiona Ctrl+C para detener los servidores${NC}"

# Mantener el script en ejecución
wait
