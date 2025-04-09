# Whisper Product Discovery SaaS – Documentación para Desarrollo (Versión 1)

## 1. Contexto y Visión del Producto

**Whisper Product Discovery SaaS** es una plataforma que ayuda a los equipos de producto, UX e innovación a capturar y estructurar aprendizajes reales desde entrevistas con usuarios. A partir de grabaciones de audio, la herramienta genera transcripciones automáticas enriquecidas, permite destacar frases clave, etiquetar problemas, y agrupar descubrimientos en proyectos.

El objetivo principal es facilitar decisiones basadas en evidencia real, capturada directamente desde la voz del cliente.

Esta primera versión (V1) del producto se centra en ofrecer una experiencia funcional mínima pero valiosa para equipos que están realizando discovery y necesitan una solución para organizar sus entrevistas de usuario y los insights que emergen de ellas.

---

## 2. Historias de Usuario – Versión 1

A continuación se detallan las 9 historias de usuario funcionales a implementar. Se indica en cada caso si la funcionalidad ya está implementada total o parcialmente.

---

### HU1. Subida de audio y transcripción automática

**Estado:** Implementada completamente

**Como** Product Manager  
**Quiero** subir una grabación de una entrevista  
**Para** obtener automáticamente su transcripción y resumen

**Funcionalidad:**
- El usuario carga archivos `.mp3`, `.mp4`, `.wav`, `.m4a`
- El sistema procesa el audio y genera automáticamente una transcripción
- Se asocia un `process_id` para hacer seguimiento del estado

**Criterios de aceptación:**
- El backend acepta los archivos mediante `POST /upload-file/`
- La transcripción se inicia automáticamente al subir el archivo
- Se retorna el `process_id` al usuario
- El estado puede ser consultado en `GET /status/{process_id}`

---

### HU2. Visualización clara de transcripción y resumen

**Estado:** Parcialmente implementada

**Como** usuario  
**Quiero** ver el texto transcrito y el resumen en una interfaz clara  
**Para** entender rápidamente de qué se trató la reunión

**Funcionalidad:**
- Visualización del texto completo transcrito
- Visualización separada de: `short_summary`, `key_points`, `action_items`

**Criterios de aceptación:**
- El resumen debe mostrarse en la parte superior del documento
- Cada sección (`TL;DR`, puntos clave, acciones) debe poder expandirse y colapsarse
- Si no existe resumen, debe indicarse claramente con un mensaje
- El frontend debe consumir `GET /results/{process_id}`

**Falta por implementar:**
- Renderización del resumen en el frontend
- Manejo visual de secciones colapsables

---

### HU3. Destacar fragmentos clave de la transcripción

**Estado:** No implementada

**Como** usuario  
**Quiero** poder marcar frases importantes del texto  
**Para** guardar citas textuales o descubrimientos relevantes

**Funcionalidad:**
- Selección de texto y guardado como “destacado”
- Asociación de fragmentos con su tiempo de inicio y fin

**Criterios de aceptación:**
- El usuario puede seleccionar un fragmento y guardarlo
- Se visualiza el listado de destacados asociados a la transcripción
- El usuario puede eliminar destacados

---

### HU4. Asignar etiquetas a frases destacadas

**Estado:** No implementada

**Como** usuario  
**Quiero** poder etiquetar frases destacadas con categorías  
**Para** organizarlas como "problema", "idea", "necesidad", etc.

**Funcionalidad:**
- Sistema de etiquetas predefinidas al momento de marcar un destacado
- Visualización de etiquetas como chips de color

**Criterios de aceptación:**
- El usuario puede elegir una o más etiquetas al guardar un destacado
- Las etiquetas se muestran visualmente junto al texto destacado
- Debe ser posible editar las etiquetas

---

### HU5. Historial de entrevistas subidas

**Estado:** Implementada completamente

**Como** usuario  
**Quiero** ver una lista de todas las entrevistas que he subido  
**Para** acceder rápidamente a transcripciones pasadas

**Funcionalidad:**
- Visualización de historial de transcripciones del usuario actual
- Acceso directo a cada una

**Criterios de aceptación:**
- Se muestra título, fecha, duración, estado
- El usuario puede hacer clic para abrir cada transcripción

---

### HU6. Organización mínima por proyectos

**Estado:** No implementada

**Como** usuario  
**Quiero** agrupar mis entrevistas por proyecto  
**Para** mantener organizada la información según el contexto

**Funcionalidad:**
- Al subir un archivo se puede asociar a un proyecto existente o crear uno nuevo

**Criterios de aceptación:**
- Cada transcripción debe tener un `project_id` asociado (opcional)
- Se pueden listar los proyectos y ver las transcripciones por proyecto
- Es posible renombrar o eliminar un proyecto vacío

---

### HU7. Autenticación y gestión de sesión

**Estado:** Implementada completamente

**Como** usuario nuevo  
**Quiero** registrarme e iniciar sesión con mis credenciales  
**Para** tener un espacio privado donde gestionar mis descubrimientos

**Funcionalidad:**
- Registro de usuario
- Login con JWT
- Expiración automática del token y redirección al login

**Criterios de aceptación:**
- El sistema usa JWT como mecanismo de autenticación
- Al expirar el token, se redirige automáticamente a login
- Las rutas privadas solo son accesibles si el token está presente

---

### HU8. Exportación de resumen y destacados

**Estado:** Parcialmente implementada

**Como** usuario  
**Quiero** poder exportar el resumen y los fragmentos destacados  
**Para** compartirlos con mi equipo o incluirlos en documentación

**Funcionalidad:**
- Exportación en `.txt` y `.pdf` (texto y resumen incluidos)

**Criterios de aceptación:**
- El archivo exportado incluye:
  - `short_summary`, `key_points`, `action_items`
  - Texto transcrito completo
  - Lista de destacados y etiquetas
- La descarga debe ser directa y sin pasos adicionales

**Falta por implementar:**
- Inclusión de resumen y destacados en el archivo `.txt`
- Opción de exportar en `.pdf` (estilizado básico)

---

### HU9. Visualización de transcripción con marcas de tiempo

**Estado:** No implementada

**Como** usuario  
**Quiero** ver los timestamps junto al texto transcrito  
**Para** poder ubicar fácilmente los momentos clave en la grabación

**Funcionalidad:**
- Mostrar marcas de tiempo de inicio y fin por segmento

**Criterios de aceptación:**
- El texto debe visualizarse agrupado por `utterance`, con timestamp de inicio visible
- Debe poder formatearse como `[mm:ss]`
- Las marcas de tiempo deben venir del backend (estructura `utterances_json`)

---

## 3. Propuesta de Modelo de Datos Actualizado

> **Nota para el desarrollador:** Esta es una **propuesta inicial** del modelo de datos. Puedes validarla o sugerir modificaciones según lo que consideres más conveniente para la implementación y escalabilidad del sistema.

---

### `users`

| Campo             | Tipo       |
|------------------|------------|
| id               | UUID       |
| username         | string     |
| email            | string     |
| hashed_password  | string     |
| created_at       | datetime   |
| updated_at       | datetime   |
| last_login       | datetime   |

---

### `projects`

| Campo         | Tipo     |
|---------------|----------|
| id            | UUID     |
| name          | string   |
| description   | text     |
| user_id       | UUID     |
| status        | string   |
| created_at    | datetime |
| updated_at    | datetime |

---

### `transcriptions`

| Campo               | Tipo     |
|---------------------|----------|
| id                  | UUID     |
| user_id             | UUID     |
| project_id          | UUID     |
| title               | string   |
| original_filename   | string   |
| audio_path          | string   |
| status              | string   |
| transcription       | text     |
| short_summary       | text     |
| key_points          | array    |
| action_items        | array    |
| utterances_json     | JSON     |
| duration            | float    |
| created_at          | datetime |
| updated_at          | datetime |

---

### `highlights`

| Campo           | Tipo     |
|------------------|----------|
| id               | UUID     |
| transcription_id | UUID     |
| user_id          | UUID     |
| text             | text     |
| start_time       | float    |
| end_time         | float    |
| created_at       | datetime |
| updated_at       | datetime |

---

### `tags`

| Campo           | Tipo     |
|-----------------|----------|
| id              | UUID     |
| name            | string   |
| color           | string   |
| description     | text     |
| user_id         | UUID     |
| created_at      | datetime |

---

### `highlight_tags`

| Campo           | Tipo     |
|-----------------|----------|
| highlight_id    | UUID     |
| tag_id          | UUID     |
| created_at      | datetime |

---

### Relaciones

```
User ───┬─── Project ───┬─── Transcription ───┬─── Highlight ───┬─── Tag
        │               │                     │                 │
        └───────────────┴─────────────────────┴─────────────────┘
```

---

## 4. Validación esperada

- Todos los endpoints nuevos deben requerir autenticación JWT
- Toda funcionalidad nueva debe integrarse sin romper la arquitectura actual
- El desarrollador puede modificar el modelo de datos si encuentra una mejor estructura, siempre que cubra los requisitos funcionales detallados

---

## 5. Plan de Implementación Ágil

A continuación se detalla el plan de implementación ágil para el desarrollo del Release 1, organizado por historias de usuario completas (end-to-end) para entregar valor de forma incremental.

### Etapa 0: Actualización del Modelo de Datos ✅ (Completado: 9 de abril de 2025)
- ✅ Implementar el modelo de datos mejorado
- ✅ Crear migraciones para preservar datos existentes
- ✅ Actualizar modelos de SQLAlchemy y esquemas Pydantic
- ✅ Implementar validaciones de datos

### Etapa 1: HU2 - Visualización clara de transcripción y resumen (1 semana)
- **Backend**: 
  - Implementar endpoint para obtener resumen estructurado
  - Mejorar la estructura de respuesta de `/results/{process_id}`
- **Frontend**: 
  - Crear componentes para visualizar resumen con secciones colapsables
  - Implementar visualización separada de `short_summary`, `key_points`, `action_items`
- **Pruebas**: 
  - Validar visualización correcta y comportamiento de colapso/expansión
  - Verificar manejo de casos donde no existe resumen

### Etapa 2: HU9 - Visualización con marcas de tiempo (1 semana)
- **Backend**: 
  - Modificar procesamiento para incluir timestamps formateados
  - Estructurar la respuesta con formato `[mm:ss]`
- **Frontend**: 
  - Crear componente para mostrar timestamps junto al texto
  - Implementar agrupación por `utterance`
- **Pruebas**: 
  - Verificar formato correcto y alineación de timestamps
  - Validar consistencia con el audio original

### Etapa 3: HU6 - Organización por proyectos (1.5 semanas)
- **Backend**: 
  - Crear endpoints CRUD para proyectos
  - Implementar asociación entre proyectos y transcripciones
- **Frontend**: 
  - Implementar componentes de gestión de proyectos
  - Crear navegación y filtrado por proyectos
- **Pruebas**: 
  - Validar creación, edición, eliminación de proyectos
  - Verificar asignación y reasignación de transcripciones a proyectos

### Etapa 4: HU3 - Destacar fragmentos (1 semana)
- **Backend**: 
  - Crear endpoints CRUD para destacados
  - Implementar asociación con transcripciones y timestamps
- **Frontend**: 
  - Implementar selección de texto y guardado como destacados
  - Crear visualización de listado de destacados
- **Pruebas**: 
  - Verificar selección, guardado y visualización de destacados
  - Validar asociación correcta con tiempos de inicio y fin

### Etapa 5: HU4 - Asignar etiquetas a frases (1 semana)
- **Backend**: 
  - Crear endpoints CRUD para etiquetas
  - Implementar asociación entre destacados y etiquetas
- **Frontend**: 
  - Implementar componentes de creación y selección de etiquetas
  - Crear visualización de etiquetas como chips de color
- **Pruebas**: 
  - Validar creación y edición de etiquetas
  - Verificar asignación de múltiples etiquetas a destacados

### Etapa 6: HU8 - Exportación de resumen y destacados (1 semana)
- **Backend**: 
  - Mejorar endpoint de descarga para incluir resumen y destacados
  - Implementar exportación en formato PDF
- **Frontend**: 
  - Implementar opciones avanzadas de exportación (TXT/PDF)
  - Crear interfaz de descarga directa
- **Pruebas**: 
  - Verificar contenido y formato de archivos exportados
  - Validar inclusión de todos los elementos requeridos

### Etapa 7: Integración final y Despliegue (0.5 semanas)
- Pruebas de integración completas
- Actualización de documentación
- Despliegue a producción

**Tiempo total estimado**: 7 semanas

### Consideraciones de Implementación

1. **Nuevos Endpoints a Implementar**:
   - Proyectos: `GET/POST /projects/`, `GET/PUT/DELETE /projects/{id}`, `GET /projects/{id}/transcriptions`
   - Destacados: `GET/POST /transcriptions/{id}/highlights`, `GET/PUT/DELETE /highlights/{id}`
   - Etiquetas: `GET/POST /tags/`, `GET/PUT/DELETE /tags/{id}`, `POST/DELETE /highlights/{id}/tags`

2. **Nuevos Componentes Frontend**:
   - `ProjectList`: Listado de proyectos con opciones CRUD
   - `ProjectDetail`: Vista detallada de un proyecto con sus transcripciones
   - `TranscriptionWithTimestamps`: Visualización de transcripción con marcas de tiempo
   - `HighlightSelector`: Componente para seleccionar y guardar fragmentos destacados
   - `TagSelector`: Componente para crear y seleccionar etiquetas
   - `TagChip`: Visualización de etiquetas como chips de color
   - `SummaryViewer`: Componente para visualizar resúmenes estructurados
   - `ExportOptions`: Opciones avanzadas de exportación

3. **Consideraciones de Escalabilidad**:
   - Implementar índices para optimizar consultas frecuentes
   - Considerar particionamiento para tablas que crecerán mucho (transcriptions)
   - Implementar política de retención para archivos temporales
   - Implementar caché para resultados de transcripción
   - Optimizar carga de datos en el frontend con paginación

---

## Fin del documento