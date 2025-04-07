#!/usr/bin/env python3
import subprocess
import os
import sys
import time
from pathlib import Path
import webbrowser
import signal
import atexit

# Detectar si estamos en entorno local y configurar el entorno si es necesario
is_local_env = False
if os.path.exists('/proc/version'):
    with open('/proc/version', 'r') as f:
        if 'Microsoft' in f.read():  # Detectar WSL
            print("Detectado entorno WSL, configurando entorno para desarrollo local...")
            try:
                # Configurar el PYTHONPATH para que las importaciones relativas funcionen
                project_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.join(project_dir, 'backend')
                
                # Solo añadir estos directorios si no están ya en el PYTHONPATH
                if backend_dir not in sys.path:
                    sys.path.insert(0, backend_dir)
                if project_dir not in sys.path:
                    sys.path.insert(0, project_dir)
                    
                is_local_env = True
                print("Entorno de desarrollo local configurado correctamente.")
            except Exception as e:
                print(f"Error al configurar entorno local: {str(e)}")

# Colores para la salida en consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Rutas principales
PROJECT_DIR = Path(__file__).parent
BACKEND_DIR = PROJECT_DIR / "backend"
FRONTEND_DIR = PROJECT_DIR / "frontend"

# Variables para almacenar los procesos
backend_process = None
frontend_process = None

def print_banner():
    """Imprime un banner para la aplicación."""
    banner = f"""
    {Colors.BLUE}{Colors.BOLD}========================================================={Colors.ENDC}
    {Colors.GREEN}{Colors.BOLD}   WHISPER MEETING TRANSCRIBER - MODO DESARROLLO   {Colors.ENDC}
    {Colors.BLUE}{Colors.BOLD}========================================================={Colors.ENDC}
    
    {Colors.BOLD}Iniciando la aplicación...{Colors.ENDC}
    
    {Colors.WARNING}* Asegúrate de haber configurado tu clave API de Deepgram{Colors.ENDC}
    {Colors.WARNING}* Para detener la aplicación presiona Ctrl+C{Colors.ENDC}
    
    {Colors.BLUE}{Colors.BOLD}========================================================={Colors.ENDC}
    """
    print(banner)

def initialize_database():
    """Inicializa la base de datos si es necesario."""
    print(f"{Colors.BOLD}Inicializando base de datos...{Colors.ENDC}")
    
    # Intenta ejecutar el script de inicialización
    try:
        subprocess.run(
            [sys.executable, "initialize_app.py"],
            cwd=PROJECT_DIR,
            check=True
        )
        print(f"{Colors.GREEN}✓ Base de datos inicializada correctamente{Colors.ENDC}")
    except subprocess.CalledProcessError:
        print(f"{Colors.FAIL}✗ Error al inicializar la base de datos{Colors.ENDC}")
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
            bufsize=1
        )
        
        # Esperar a que el servidor esté listo - ahora con más tiempo y mensajes
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
                
                # Ahora detectamos varios mensajes posibles que indican que el servidor está listo
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
