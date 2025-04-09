"""
Script para migrar la base de datos a la nueva estructura.
Este script:
1. Hace una copia de seguridad de la base de datos actual
2. Crea las nuevas tablas
3. Migra los datos existentes al nuevo esquema
4. Actualiza las referencias y relaciones
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime
import json
from pathlib import Path
import uuid

# Añadir el directorio raíz al path para poder importar módulos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Importar los modelos y la conexión
from backend.database.connection import Base, engine, SQLALCHEMY_DATABASE_URL
from backend.models.models import User, Transcription, Project, Highlight, Tag

# Extraer la ruta de la base de datos del URL
db_path = SQLALCHEMY_DATABASE_URL.replace('sqlite:///', '')

def backup_database():
    """Crear una copia de seguridad de la base de datos actual."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    if os.path.exists(db_path):
        print(f"Creando copia de seguridad en: {backup_path}")
        shutil.copy2(db_path, backup_path)
        return True
    else:
        print(f"No se encontró la base de datos en: {db_path}")
        return False

def connect_to_db():
    """Conectar a la base de datos SQLite."""
    return sqlite3.connect(db_path)

def check_tables_exist():
    """Verificar qué tablas existen en la base de datos actual."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Obtener lista de tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return tables

def create_new_tables():
    """Crear las nuevas tablas en la base de datos."""
    print("Creando nuevas tablas...")
    # Crear todas las tablas definidas en los modelos
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas correctamente.")

def migrate_users_data():
    """Migrar datos de la tabla users al nuevo formato."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Verificar si la tabla users existe y tiene datos
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users';")
    if cursor.fetchone()[0] == 0:
        print("No existe la tabla users. Saltando migración de usuarios.")
        conn.close()
        return
    
    # Verificar la estructura actual de la tabla
    cursor.execute("PRAGMA table_info(users);")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Obtener datos existentes
    cursor.execute("SELECT * FROM users;")
    users_data = cursor.fetchall()
    
    if not users_data:
        print("No hay usuarios para migrar.")
        conn.close()
        return
    
    # Crear tabla temporal para la migración
    cursor.execute("""
    CREATE TABLE users_new (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE,
        username TEXT UNIQUE,
        hashed_password TEXT,
        is_active INTEGER,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        last_login TIMESTAMP
    );
    """)
    
    # Migrar datos a la nueva tabla
    for user in users_data:
        # Crear un diccionario con los datos del usuario
        user_dict = {columns[i]: user[i] for i in range(len(columns))}
        
        # Generar un UUID para el nuevo ID
        new_id = str(uuid.uuid4())
        
        # Insertar en la nueva tabla
        cursor.execute("""
        INSERT INTO users_new (id, email, username, hashed_password, is_active, created_at, updated_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?, NULL, NULL);
        """, (
            new_id,
            user_dict.get('email'),
            user_dict.get('username'),
            user_dict.get('hashed_password'),
            user_dict.get('is_active', 1),
            user_dict.get('created_at')
        ))
        
        # Guardar mapeo de IDs para usar en otras tablas
        if 'id' in user_dict:
            # Guardar el mapeo del ID antiguo al nuevo
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS id_mapping (
                old_id INTEGER,
                new_id TEXT,
                table_name TEXT
            );
            """)
            cursor.execute("INSERT INTO id_mapping VALUES (?, ?, ?);", 
                          (user_dict['id'], new_id, 'users'))
    
    # Reemplazar la tabla antigua con la nueva
    cursor.execute("DROP TABLE users;")
    cursor.execute("ALTER TABLE users_new RENAME TO users;")
    
    # Crear índices
    cursor.execute("CREATE INDEX idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX idx_users_username ON users(username);")
    
    conn.commit()
    conn.close()
    print("Migración de usuarios completada.")

def migrate_transcriptions_data():
    """Migrar datos de la tabla transcriptions al nuevo formato."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Verificar si la tabla transcriptions existe y tiene datos
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='transcriptions';")
    if cursor.fetchone()[0] == 0:
        print("No existe la tabla transcriptions. Saltando migración de transcripciones.")
        conn.close()
        return
    
    # Verificar la estructura actual de la tabla
    cursor.execute("PRAGMA table_info(transcriptions);")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Obtener datos existentes
    cursor.execute("SELECT * FROM transcriptions;")
    transcriptions_data = cursor.fetchall()
    
    if not transcriptions_data:
        print("No hay transcripciones para migrar.")
        conn.close()
        return
    
    # Crear tabla temporal para la migración
    cursor.execute("""
    CREATE TABLE transcriptions_new (
        id TEXT PRIMARY KEY,
        title TEXT,
        original_filename TEXT,
        audio_path TEXT,
        status TEXT,
        transcription TEXT,
        short_summary TEXT,
        key_points TEXT,
        action_items TEXT,
        utterances_json TEXT,
        duration REAL,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        user_id TEXT,
        project_id TEXT
    );
    """)
    
    # Migrar datos a la nueva tabla
    for transcription in transcriptions_data:
        # Crear un diccionario con los datos de la transcripción
        trans_dict = {columns[i]: transcription[i] for i in range(len(columns))}
        
        # Generar un UUID para el nuevo ID
        new_id = str(uuid.uuid4())
        
        # Obtener el nuevo user_id del mapeo
        cursor.execute("SELECT new_id FROM id_mapping WHERE old_id = ? AND table_name = 'users';", 
                      (trans_dict.get('user_id'),))
        result = cursor.fetchone()
        new_user_id = result[0] if result else None
        
        # Preparar los datos para la nueva estructura
        # Convertir el contenido de texto a la nueva estructura
        content = trans_dict.get('content', '')
        
        # Insertar en la nueva tabla
        cursor.execute("""
        INSERT INTO transcriptions_new (
            id, title, original_filename, audio_path, status, transcription, 
            short_summary, key_points, action_items, utterances_json, duration,
            created_at, updated_at, user_id, project_id
        )
        VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, NULL, NULL, ?, NULL, ?, NULL);
        """, (
            new_id,
            trans_dict.get('title'),
            trans_dict.get('original_filename'),
            trans_dict.get('file_path'),  # Renombrado a audio_path
            'completed',  # Estado por defecto
            content,  # Renombrado a transcription
            json.dumps([]),  # key_points vacío
            json.dumps([]),  # action_items vacío
            trans_dict.get('created_at'),
            new_user_id
        ))
        
        # Guardar mapeo de IDs
        if 'id' in trans_dict:
            cursor.execute("INSERT INTO id_mapping VALUES (?, ?, ?);", 
                          (trans_dict['id'], new_id, 'transcriptions'))
    
    # Reemplazar la tabla antigua con la nueva
    cursor.execute("DROP TABLE transcriptions;")
    cursor.execute("ALTER TABLE transcriptions_new RENAME TO transcriptions;")
    
    # Crear índices
    cursor.execute("CREATE INDEX idx_transcriptions_user_id ON transcriptions(user_id);")
    cursor.execute("CREATE INDEX idx_transcriptions_project_id ON transcriptions(project_id);")
    
    conn.commit()
    conn.close()
    print("Migración de transcripciones completada.")

def create_default_project():
    """Crear un proyecto por defecto para cada usuario."""
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Obtener todos los usuarios
    cursor.execute("SELECT id, username FROM users;")
    users = cursor.fetchall()
    
    # Crear un proyecto por defecto para cada usuario
    for user_id, username in users:
        project_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO projects (id, name, description, status, created_at, user_id)
        VALUES (?, ?, ?, ?, datetime('now'), ?);
        """, (
            project_id,
            f"Proyecto por defecto de {username}",
            "Proyecto creado automáticamente durante la migración",
            "active",
            user_id
        ))
        
        # Asignar todas las transcripciones del usuario a este proyecto
        cursor.execute("""
        UPDATE transcriptions SET project_id = ? WHERE user_id = ?;
        """, (project_id, user_id))
    
    conn.commit()
    conn.close()
    print("Proyectos por defecto creados.")

def main():
    """Función principal para ejecutar la migración."""
    print("Iniciando migración de la base de datos...")
    
    # Verificar si la base de datos existe
    if not os.path.exists(db_path):
        print(f"No se encontró la base de datos en: {db_path}")
        print("Creando una nueva base de datos con la estructura actualizada...")
        create_new_tables()
        print("Migración completada. Se ha creado una nueva base de datos.")
        return
    
    # Hacer copia de seguridad
    if backup_database():
        print("Copia de seguridad creada correctamente.")
    else:
        print("No se pudo crear la copia de seguridad. Abortando migración.")
        return
    
    # Verificar tablas existentes
    existing_tables = check_tables_exist()
    print(f"Tablas existentes: {existing_tables}")
    
    # Migrar datos de usuarios
    migrate_users_data()
    
    # Migrar datos de transcripciones
    migrate_transcriptions_data()
    
    # Crear las nuevas tablas (projects, highlights, tags, highlight_tags)
    create_new_tables()
    
    # Crear proyectos por defecto y asignar transcripciones
    create_default_project()
    
    print("Migración completada con éxito.")

if __name__ == "__main__":
    main()
