#!/usr/bin/env python3
import os
import re

# Directorio raíz del proyecto backend
backend_dir = os.path.join(os.getcwd(), 'backend')

# Patrón para buscar importaciones absolutas que comiencen con 'backend.'
pattern = re.compile(r'from backend\.(\S+)')

# Recorrer recursivamente todos los archivos .py en el directorio backend
for root, _, files in os.walk(backend_dir):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, backend_dir)
            print(f"Procesando {rel_path}...")
            
            # Leer el contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar importaciones absolutas
            if 'from backend.' in content:
                print(f"  Encontradas importaciones para corregir")
                
                # Modificar las importaciones
                # 1. Determinar la ruta relativa desde el archivo actual hasta backend
                path_depth = len(rel_path.split(os.sep)) - 1
                
                def replace_import(match):
                    module_path = match.group(1)
                    parts = module_path.split('.')
                    
                    # Si el archivo está importando desde su propio directorio
                    if parts[0] == os.path.dirname(rel_path).replace(os.sep, '.'):
                        return f"from {'.'.join(parts[1:])}"
                    
                    # Para importaciones de otros directorios, usar importaciones relativas
                    if path_depth > 1:  # Si el archivo no está directamente en backend/
                        return f"from {'.' * (path_depth-1)}.{module_path}"
                    else:
                        return f"from {module_path}"
                
                # Aplicar el reemplazo
                new_content = pattern.sub(replace_import, content)
                
                # Guardar el archivo modificado
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"  ✓ Importaciones corregidas")

print("Proceso completado. Revisa los archivos para asegurarte de que las importaciones sean correctas.")
