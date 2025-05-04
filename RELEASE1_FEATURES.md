# RocketFlow – Documentación para Desarrollo

## 1. Contexto y Visión del Producto

**RocketFlow** es una plataforma que ayuda a los equipos de producto, UX e innovación a capturar y estructurar aprendizajes reales desde entrevistas con usuarios. A partir de grabaciones de audio, la herramienta genera transcripciones automáticas enriquecidas, permite destacar frases clave, etiquetar problemas, y agrupar descubrimientos en proyectos.

El objetivo principal es facilitar decisiones basadas en evidencia real, capturada directamente desde la voz del cliente.

## 2. Plan de Desarrollo

### Versión 1 – MVP Funcional de Transcripción y Organización

Enfocado en entregar una herramienta usable y útil para registrar entrevistas, visualizar resúmenes, exportar resultados y organizar por proyectos.

#### Funcionalidades Implementadas

| Código | Nombre | Estado |
|--------|--------|--------|
| HU1 | Subida de grabaciones y transcripción automática | Completada |
| HU2 | Visualización clara de transcripción y resumen | Completada |
| HU5 | Historial de entrevistas subidas | Completada |
| HU7 | Autenticación y gestión de sesión | Completada |
| HU9 | Visualización de transcripción con marcas de tiempo | Completada |

#### Funcionalidades Pendientes para Versión 1

**HU8 - Exportación TXT con contenido completo**
- El archivo debe tener el mismo nombre del audio original
- Incluir utterances con marcas de tiempo [mm:ss]
- Exportar resumen (short_summary, key_points, action_items)

**HU6 - Organización por proyectos**
- Crear, editar y eliminar proyectos
- Visualizar lista de proyectos del usuario autenticado
- Al subir un archivo, permitir asociarlo a un proyecto existente o crear uno nuevo
- En historial, agrupar transcripciones por proyecto (expandible/collapsable)

#### Funcionalidades Pospuestas (Post-MVP)

Las siguientes historias se moverán al backlog para fases futuras:
- HU3 - Destacar fragmentos clave
- HU4 - Asignar etiquetas a frases destacadas

### Versión 2 – MVP Discovery Contextualizado

Este MVP es funcional y vendible. Aporta estructura, especialización del resumen y base para monetización.

#### Nuevas Funcionalidades Planificadas

**HU10 - Selección de metadatos y resumen contextual**
- Al subir audio: seleccionar tipo de actividad y fase del discovery
- El backend usa prompts especializados según selección
- Devuelve resumen adaptado al contexto
- Exporta .xml si es "levantamiento de procesos"
- Salidas: .txt, .json, .xml (opcional)

**HU11 - Sistema de pago**
- Lógica de planes (Free, Pro, Team)
- Restricciones por volumen o cantidad de transcripciones
- Integración con pasarela (ej: Stripe, MercadoPago)

**HU12 - Login con Google**
- Iniciar sesión con cuenta de Google
- Asociar con cuenta RocketFlow si ya existe con ese correo

**HU13 - Look & Feel profesional**
- Definir identidad visual definitiva
- Ajustar colores, íconos y tipografía
- Crear componentes coherentes y responsivos

## 3. Historias de Usuario Detalladas

A continuación se detallan las historias de usuario con sus especificaciones técnicas y criterios de aceptación. Se indica el estado actual de cada funcionalidad.

---

### HU1. Subida de audio y transcripción automática

**Estado:** Completada

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

**Estado:** Completada

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


---

### HU3. Destacar fragmentos clave de la transcripción

**Estado:** Pospuesta para versiones futuras

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

**Estado:** Pospuesta para versiones futuras

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

**Estado:** Completada

**Como** usuario  
**Quiero** ver una lista de todas las entrevistas que he subido  
**Para** acceder rápidamente a transcripciones pasadas

**Funcionalidad:**
- Visualización de historial de transcripciones del usuario actual
- Acceso directo a cada una
- Paginación (15 elementos por página)
- Ordenamiento por título y fecha (ascendente/descendente)

**Criterios de aceptación:**
- Se muestra título, fecha, duración, estado
- El usuario puede hacer clic para abrir cada transcripción
- Los controles de paginación permiten navegar entre páginas
- Los encabezados de columna 'Título' y 'Fecha' permiten ordenar la tabla

---

### HU6. Organización por proyectos

**Estado:** Pendiente para Versión 1

**Como** usuario  
**Quiero** agrupar mis entrevistas por proyecto  
**Para** mantener organizada la información según el contexto

**Funcionalidad:**
- En la sección de "Historial" el usuario puede ver las transcripciones por proyecto
- El proyecto se debe listar y si tiene transcripciones, se puede abrir y colapsar
- Al subir un archivo se puede asociar a un proyecto existente o crear uno nuevo

**Criterios de aceptación:**
- Cada transcripción debe tener un `project_id` asociado (opcional)
- Se pueden listar los proyectos y ver las transcripciones por proyecto
- Es posible renombrar o eliminar un proyecto vacío
- Si hay alguna transcripción que no pertenece a un proyecto, debe listarlas en orden descendente por fecha

---

### HU7. Autenticación y gestión de sesión

**Estado:** Completada

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

### HU8. Exportación de resumen y transcripción

**Estado:** ✅ Completado

**Como** usuario  
**Quiero** poder exportar el resumen y la transcripción completa  
**Para** compartirlos con mi equipo o incluirlos en documentación

**Funcionalidad implementada:**
- Exportación en `.txt` con nombre del archivo original
- Estructura clara con secciones bien definidas:
  - Encabezado con nombre del archivo original
  - Resumen estructurado (TL;DR, puntos clave, acciones)
  - Transcripción completa con marcas de tiempo [mm:ss]
- Soporte para transcripciones nuevas y existentes en historial
- Manejo robusto de diferentes tipos de datos y formatos

**Detalles técnicos:**
- Implementación en endpoints `/download/{process_id}` y `/api/download/{process_id}`
- Obtención de datos desde la base de datos o memoria según disponibilidad
- Formato de marcas de tiempo: `[mm:ss]` para cada utterance
- Inclusión de información de hablantes cuando está disponible

**Criterios de aceptación cumplidos:**
- ✅ El archivo exportado incluye:
  - `short_summary`, `key_points`, `action_items`
  - Texto transcrito completo con marcas de tiempo
- ✅ La descarga es directa y sin pasos adicionales
- ✅ El formato facilita la lectura y referencia a partes específicas

---

### HU9. Visualización de transcripción con marcas de tiempo

**Estado:** Completada

**Como** usuario  
**Quiero** ver los timestamps junto al texto transcrito  
**Para** poder ubicar fácilmente los momentos clave en la grabación

**Funcionalidad:**
- Mostrar marcas de tiempo de inicio y fin por segmento
- Agrupación inteligente de utterances para mejorar la legibilidad
- Opción para mostrar/ocultar timestamps

**Criterios de aceptación:**
- El texto debe visualizarse agrupado por `utterance`, con timestamp de inicio visible
- Debe poder formatearse como `[mm:ss]`
- Las marcas de tiempo deben venir del backend (estructura `utterances_json`)
- Los utterances deben tener un tamaño adecuado para facilitar la lectura

**Mejoras implementadas:**
- Se configuró el parámetro `utt_split=2.5` en la API de Deepgram para generar utterances más coherentes
- Se implementó un botón para activar/desactivar la visualización de timestamps
- Se optimizó la visualización para mostrar los timestamps en formato `[mm:ss]`

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

## 5. Plan de Implementación Ágil - Versión 1

A continuación se detalla el plan de implementación ágil actualizado para completar las funcionalidades pendientes de la Versión 1. Este plan se enfoca exclusivamente en las historias de usuario que faltan para cerrar el MVP inicial.

### Funcionalidades ya completadas

- ✅ **HU1 - Subida de audio y transcripción automática**
- ✅ **HU2 - Visualización clara de transcripción y resumen**
- ✅ **HU5 - Historial de entrevistas subidas**
- ✅ **HU7 - Autenticación y gestión de sesión**
- ✅ **HU9 - Visualización de transcripción con marcas de tiempo**

### Plan para completar la Versión 1

#### Etapa 1: HU8 - Exportación TXT con contenido completo (1 semana)

**Objetivo**: Mejorar la funcionalidad de exportación para incluir toda la información relevante en un formato claro y utilizable.

- **Backend**: 
  - Modificar el endpoint de descarga para usar el nombre del archivo original
  - Estructurar el contenido del archivo para incluir resumen y transcripción con marcas de tiempo
  - Implementar formato de marcas de tiempo [mm:ss] en el texto exportado

- **Frontend**: 
  - Mejorar la interfaz de descarga para mostrar el progreso
  - Implementar opción para seleccionar qué elementos incluir en la exportación

- **Pruebas**: 
  - Verificar que el archivo descargado tenga el nombre correcto
  - Validar la inclusión de resumen, puntos clave y acciones
  - Comprobar que las marcas de tiempo sean correctas

#### Etapa 2: HU6 - Organización por proyectos (2 semanas)

**Objetivo**: Implementar un sistema de organización por proyectos que permita agrupar transcripciones relacionadas.

- **Backend**: 
  - Crear endpoints CRUD para proyectos: `GET/POST /projects/`, `GET/PUT/DELETE /projects/{id}`
  - Implementar endpoint para listar transcripciones por proyecto: `GET /projects/{id}/transcriptions`
  - Modificar endpoint de subida para permitir asociar a un proyecto

- **Frontend**: 
  - Implementar componente `ProjectList` para listar y gestionar proyectos
  - Crear interfaz para asignar transcripciones a proyectos durante la subida
  - Modificar la vista de historial para agrupar por proyectos (expandible/colapsable)
  - Implementar funcionalidad para reasignar transcripciones entre proyectos

- **Pruebas**: 
  - Validar creación, edición y eliminación de proyectos
  - Verificar que las transcripciones se asignen correctamente
  - Comprobar que la vista de historial agrupe correctamente
  - Validar que las transcripciones sin proyecto se muestren en orden cronológico inverso

#### Etapa 3: Integración final y Despliegue (1 semana)

- **Pruebas de integración**:
  - Validar flujo completo desde subida hasta exportación
  - Verificar organización por proyectos y navegación
  - Comprobar rendimiento con múltiples transcripciones y proyectos

- **Optimización**:
  - Implementar caché para resultados de transcripción
  - Optimizar carga de datos con paginación
  - Implementar política de retención para archivos temporales

- **Documentación y Despliegue**:
  - Actualizar documentación técnica y de usuario
  - Realizar despliegue a producción
  - Configurar monitoreo para detectar problemas

**Tiempo total estimado**: 4 semanas

### Consideraciones de Implementación para Versión 1

1. **Nuevos Endpoints a Implementar**:
   - Proyectos: `GET/POST /projects/`, `GET/PUT/DELETE /projects/{id}`, `GET /projects/{id}/transcriptions`
   - Exportación: Mejorar `GET /transcriptions/{id}/export` para incluir resumen y marcas de tiempo

2. **Nuevos Componentes Frontend**:
   - `ProjectList`: Listado de proyectos con opciones CRUD
   - `ProjectDetail`: Vista detallada de un proyecto con sus transcripciones
   - `ProjectSelector`: Selector de proyecto durante la subida de archivos
   - `ExportOptions`: Opciones básicas de exportación

3. **Consideraciones de Escalabilidad**:
   - Implementar índices para optimizar consultas frecuentes
   - Considerar particionamiento para tablas que crecerán mucho (transcriptions)
   - Implementar política de retención para archivos temporales
   - Implementar caché para resultados de transcripción
   - Optimizar carga de datos en el frontend con paginación

4. **Mejoras de Experiencia de Usuario**:
   - Implementar feedback visual durante procesos largos (carga, transcripción, exportación)
   - Mejorar la navegación entre proyectos y transcripciones
   - Optimizar la visualización en dispositivos móviles

---

## Fin del documento