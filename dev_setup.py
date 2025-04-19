#!/usr/bin/env python3
"""
Script para configurar el entorno de desarrollo local.
Este script modifica el PYTHONPATH para permitir que las importaciones relativas
funcionen en el entorno local de WSL sin tener que modificar todos los archivos fuente.
Además, inicializa la base de datos y ejecuta tanto el backend como el frontend.
"""

import os
import sys
import subprocess
import time
import signal
import atexit
import webbrowser
from pathlib import Path

# Colores para la salida en consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Variables para almacenar los procesos
backend_process = None
frontend_process = None

def print_banner():
    """Imprime un banner para la aplicación."""
    banner = f"""
    {Colors.BLUE}{Colors.BOLD}========================================================={Colors.ENDC}
    {Colors.GREEN}{Colors.BOLD}   WHISPER MEETING TRANSCRIBER - MODO DESARROLLO WSL   {Colors.ENDC}
    {Colors.BLUE}{Colors.BOLD}========================================================={Colors.ENDC}
    
    {Colors.BOLD}Iniciando la aplicación en entorno WSL...{Colors.ENDC}
    
    {Colors.WARNING}* PYTHONPATH configurado automáticamente para WSL{Colors.ENDC}
    {Colors.WARNING}* Asegúrate de haber configurado tu clave API de Deepgram{Colors.ENDC}
    {Colors.WARNING}* Para detener la aplicación presiona Ctrl+C{Colors.ENDC}
    
    {Colors.BLUE}{Colors.BOLD}========================================================={Colors.ENDC}
    """
    print(banner)

def setup_environment():
    """Configura el entorno de desarrollo añadiendo las rutas necesarias al PYTHONPATH y verifica .env.development."""
    # Obtener rutas absolutas
    global PROJECT_DIR
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    global BACKEND_DIR
    BACKEND_DIR = os.path.join(PROJECT_DIR, 'backend')
    global FRONTEND_DIR
    FRONTEND_DIR = os.path.join(PROJECT_DIR, 'frontend')

    # Configurar variables de entorno
    os.environ['PYTHONPATH'] = f"{PROJECT_DIR}:{BACKEND_DIR}:{os.environ.get('PYTHONPATH', '')}"
    print(f"PYTHONPATH configurado: {os.environ['PYTHONPATH']}")

    # Verificar .env.development
    env_path = os.path.join(FRONTEND_DIR, '.env.development')
    vite_url = 'VITE_API_URL=http://localhost:8000/api'
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write(vite_url + '\n')
        print(f"{Colors.WARNING}* Se creó .env.development con VITE_API_URL por defecto (sin barra final){Colors.ENDC}")
    else:
        with open(env_path) as f:
            content = f.read()
        # Verifica que la línea esté y no tenga barra final
        import re
        match = re.search(r'^VITE_API_URL=(.+)$', content, re.MULTILINE)
        if match:
            url = match.group(1).strip()
            if url.endswith('/'):
                print(f"{Colors.FAIL}✗ VITE_API_URL en .env.development termina en barra. Corrígelo a: {vite_url}{Colors.ENDC}")
            elif url != 'http://localhost:8000/api':
                print(f"{Colors.WARNING}! VITE_API_URL en .env.development es distinto de lo esperado: {url}{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}! .env.development no contiene VITE_API_URL. Agrégalo como: {vite_url}{Colors.ENDC}")

    # Chequeo de rutas '/api/' hardcodeadas en el frontend
    import glob
    import fnmatch
    js_files = glob.glob(os.path.join(FRONTEND_DIR, 'src', '**', '*.js*'), recursive=True)
    found = False
    for jsfile in js_files:
        with open(jsfile, encoding='utf-8') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            if "/api/" in line and 'VITE_API_URL' not in line and 'import.meta.env' not in line:
                if not found:
                    print(f"{Colors.WARNING}! Posible ruta '/api/' hardcodeada detectada en:{Colors.ENDC}")
                    found = True
                print(f"  {jsfile} (línea {idx+1}): {line.strip()}")
    if not found:
        print(f"{Colors.GREEN}✓ No se detectaron rutas '/api/' hardcodeadas en el frontend.{Colors.ENDC}")


def initialize_database():
    """Inicializa la base de datos si es necesario usando SQLAlchemy directamente."""
    print(f"{Colors.BOLD}Verificando base de datos...{Colors.ENDC}")
    
    # Comprobar si la base de datos ya existe
    db_path = os.path.join(PROJECT_DIR, 'backend', 'app.db')
    
    if os.path.exists(db_path):
        print(f"{Colors.GREEN}✓ Base de datos ya existe, omitiendo inicialización{Colors.ENDC}")
        return True
    
    # Si no existe, inicializar desde este script
    print(f"{Colors.BOLD}Inicializando base de datos...{Colors.ENDC}")
    try:
        # Usar subprocess para ejecutar en un proceso separado
        # Esto evitará problemas con la definición de tablas
        cmd = [
            sys.executable, 
            "-c", 
            "import os; import sys; sys.path.insert(0, ''); "
            "from sqlalchemy import create_engine; "
            "sys.path.insert(0, '/home/olaf/WhisperMeetingProject'); "
            "sys.path.insert(0, '/home/olaf/WhisperMeetingProject/backend'); "
            "from backend.database.connection import Base; "
            "from backend.models.models import User, Transcription; "
            "engine = create_engine('sqlite:///backend/app.db'); "
            "Base.metadata.create_all(bind=engine); "
            "print('Base de datos creada exitosamente')"
        ]
        
        subprocess.run(cmd, cwd=PROJECT_DIR, check=True)
        print(f"{Colors.GREEN}✓ Base de datos inicializada correctamente{Colors.ENDC}")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}✗ Error al inicializar la base de datos: {str(e)}{Colors.ENDC}")
        return False
    
    return True

def start_backend():
    """Inicia el servidor backend con uvicorn."""
    global backend_process
    
    print(f"{Colors.BOLD}Iniciando servidor backend...{Colors.ENDC}")
    
    # Iniciar el servidor backend con uvicorn
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app", 
        "--reload", "--host", "0.0.0.0", "--port", "8000"
    ]
    
    try:
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ
        )
        
        # Esperar a que el servidor esté listo
        backend_ready = False
        print(f"{Colors.BOLD}Esperando a que el servidor backend esté listo...{Colors.ENDC}")
        
        # Aumentamos el tiempo de espera a 15 segundos (150 intentos * 0.1s)
        for i in range(150):
            if backend_process.poll() is not None:
                # El proceso terminó inesperadamente
                print(f"{Colors.FAIL}✗ El servidor backend terminó inesperadamente{Colors.ENDC}")
                return False
                
            try:
                output = backend_process.stdout.readline().strip()
                if output:  # Solo imprimimos líneas no vacías
                    print(f"  Backend: {output}")
                
                # Detectamos varios mensajes posibles que indican que el servidor está listo
                if any(msg in output for msg in [
                    "Application startup complete",
                    "Uvicorn running on",
                    "Waiting for application startup",
                    "Started reloader process",
                    "Started server process"
                ]):
                    # Después de detectar alguno de estos mensajes, damos tiempo adicional
                    # para asegurarnos de que el servidor esté completamente listo
                    time.sleep(2)
                    backend_ready = True
                    break
            except (BrokenPipeError, IOError):
                # Manejo de errores de lectura de la tubería
                break
                
            time.sleep(0.1)
        
        # Incluso si no detectamos el mensaje exacto, consideramos que el servidor está listo
        # si ha pasado suficiente tiempo y el proceso sigue ejecutándose
        if backend_process.poll() is None and i >= 100:
            backend_ready = True
        
        if backend_ready:
            print(f"{Colors.GREEN}✓ Servidor backend iniciado en http://localhost:8000{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.FAIL}✗ El servidor backend no pudo iniciarse correctamente{Colors.ENDC}")
            if backend_process:
                backend_process.terminate()
                backend_process = None
            return False
            
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error al iniciar el servidor backend: {str(e)}{Colors.ENDC}")
        return False

def start_frontend():
    """Inicia el servidor de desarrollo frontend con npm."""
    global frontend_process
    
    print(f"{Colors.BOLD}Iniciando servidor frontend...{Colors.ENDC}")
    
    # Comprobar si node/npm está instalado
    try:
        subprocess.run(["npm", "--version"], check=True, stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{Colors.FAIL}✗ Node.js/npm no está instalado o no está en el PATH{Colors.ENDC}")
        return False
    
    # Iniciar el servidor frontend
    frontend_cmd = ["npm", "run", "dev"]
    
    try:
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Esperar a que el servidor esté listo
        frontend_ready = False
        frontend_url = None
        print(f"{Colors.BOLD}Esperando a que el servidor frontend esté listo...{Colors.ENDC}")
        
        for _ in range(200):  # Aumentamos el tiempo de espera a 20 segundos
            if frontend_process.poll() is not None:
                # El proceso terminó inesperadamente
                print(f"{Colors.FAIL}✗ El servidor frontend terminó inesperadamente{Colors.ENDC}")
                return False
                
            try:
                output = frontend_process.stdout.readline().strip()
                if output:  # Solo imprimimos líneas no vacías
                    print(f"  Frontend: {output}")
                
                if "Local:" in output:
                    frontend_url = output.split("Local:")[1].strip()
                    frontend_ready = True
                    break
            except (BrokenPipeError, IOError):
                break
                
            time.sleep(0.1)
        
        # Incluso si no detectamos el mensaje exacto, consideramos que el servidor está listo
        # si ha pasado suficiente tiempo y el proceso sigue ejecutándose
        if frontend_process.poll() is None and not frontend_url:
            frontend_url = "http://localhost:5173"  # URL por defecto de Vite
            frontend_ready = True
        
        if frontend_ready and frontend_url:
            print(f"{Colors.GREEN}✓ Servidor frontend iniciado en {frontend_url}{Colors.ENDC}")
            
            # Abrir el navegador automáticamente
            try:
                print(f"{Colors.BOLD}Abriendo navegador...{Colors.ENDC}")
                webbrowser.open(frontend_url)
            except:
                print(f"{Colors.WARNING}! No se pudo abrir el navegador automáticamente{Colors.ENDC}")
            
            return True
        else:
            print(f"{Colors.FAIL}✗ El servidor frontend no pudo iniciarse correctamente{Colors.ENDC}")
            if frontend_process:
                frontend_process.terminate()
                frontend_process = None
            return False
            
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error al iniciar el servidor frontend: {str(e)}{Colors.ENDC}")
        return False

def cleanup():
    """Limpia los procesos al salir."""
    if backend_process:
        print(f"{Colors.BOLD}Deteniendo servidor backend...{Colors.ENDC}")
        backend_process.terminate()
        
    if frontend_process:
        print(f"{Colors.BOLD}Deteniendo servidor frontend...{Colors.ENDC}")
        frontend_process.terminate()
        
    print(f"{Colors.GREEN}{Colors.BOLD}¡Aplicación detenida correctamente!{Colors.ENDC}")

def handle_signal(sig, frame):
    """Maneja la señal de interrupción (Ctrl+C)."""
    print(f"\n{Colors.WARNING}Señal de interrupción recibida. Deteniendo la aplicación...{Colors.ENDC}")
    sys.exit(0)

def main():
    """Función principal para iniciar la aplicación."""
    # Configurar el entorno y advertir sobre .env y rutas
    setup_environment()
    
    # Imprimir banner
    print_banner()
    
    # Registrar la función de limpieza
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, handle_signal)
    
    # Inicializar la base de datos
    if not initialize_database():
        return 1
    
    # Iniciar backend
    if not start_backend():
        return 1
    
    # Iniciar frontend
    if not start_frontend():
        return 1
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}¡Aplicación iniciada correctamente!{Colors.ENDC}")
    print(f"{Colors.BOLD}Backend:{Colors.ENDC} http://localhost:8000")
    print(f"{Colors.BOLD}Frontend:{Colors.ENDC} Abierto en tu navegador")
    print(f"\n{Colors.WARNING}Presiona Ctrl+C para detener la aplicación{Colors.ENDC}")
    
    # Mantener el script en ejecución
    try:
        while True:
            # Verificar si alguno de los procesos ha terminado
            if backend_process and backend_process.poll() is not None:
                print(f"{Colors.FAIL}✗ El servidor backend se ha detenido inesperadamente{Colors.ENDC}")
                return 1
                
            if frontend_process and frontend_process.poll() is not None:
                print(f"{Colors.FAIL}✗ El servidor frontend se ha detenido inesperadamente{Colors.ENDC}")
                return 1
                
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupción de usuario. Deteniendo la aplicación...{Colors.ENDC}")
    
    return 0
        
if __name__ == "__main__":
    sys.exit(main())
