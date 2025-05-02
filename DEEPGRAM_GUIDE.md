# Guía para Configurar Deepgram y Deepseek API

Esta guía te ayudará a configurar las APIs necesarias para el funcionamiento completo de Whisper Meeting Transcriber:
- **Deepgram API**: Para la transcripción de audio a texto
- **Deepseek API**: Para la generación de resúmenes, puntos clave y elementos de acción

## 1. Crear una Cuenta en Deepgram

1. Ve al sitio web de Deepgram: [https://console.deepgram.com/signup](https://console.deepgram.com/signup)
2. Regístrate usando tu correo electrónico, Google o GitHub.
3. Completa el proceso de registro con tu información personal.
4. Confirma tu cuenta a través del correo electrónico que recibirás.

## 2. Obtener tu API Key de Deepgram

1. Inicia sesión en la [Consola de Deepgram](https://console.deepgram.com/login).
2. Una vez dentro del panel de control, selecciona tu proyecto en el menú desplegable de la esquina superior izquierda.
3. Haz clic en "Settings" (Configuración) en el menú lateral.
4. Selecciona la pestaña "API Keys".
5. Haz clic en "Create a New API Key" (Crear una nueva clave API).
6. Configura tu clave API:
   - **Friendly Name**: Asigna un nombre descriptivo (ej: "WhisperMeetingProject")
   - **Permissions**: Selecciona "Owner" para tener todos los permisos necesarios.
   - **Expiration**: Puedes configurar una fecha de expiración o seleccionar "Never" si no quieres que expire.
   - **Tags**: Opcional, puedes agregar etiquetas para organizar tus claves.
7. Haz clic en "Create Key".
8. **IMPORTANTE**: Copia inmediatamente la clave API generada y guárdala en un lugar seguro. No podrás volver a verla una vez que cierres esta ventana.

## 3. Añadir Crédito a tu Cuenta de Deepgram

1. Deepgram ofrece $200 en crédito gratuito al registrarte, lo que suele ser suficiente para empezar a probar el servicio.

## 4. Configuración de Utterances y Timestamps en Deepgram

### ¿Qué son los Utterances?

Los utterances son segmentos de habla que Deepgram identifica como unidades semánticas significativas. Estos segmentos permiten dividir una transcripción larga en partes más pequeñas y manejables, cada una con su propio timestamp.

### Parámetros de Configuración

En nuestra implementación, utilizamos los siguientes parámetros para optimizar la detección de utterances:

- **utterances=True**: Activa la detección de utterances en la API de Deepgram.
- **utt_split=2.5**: Define la duración del silencio (en segundos) que Deepgram utiliza para determinar cuándo debe comenzar un nuevo utterance. Un valor más alto genera segmentos más largos y coherentes.

### Beneficios de esta Configuración

- **Mejor experiencia de usuario**: Los timestamps son más significativos y menos fragmentados.
- **Mayor coherencia semántica**: Los segmentos tienden a contener ideas completas.
- **Mejor legibilidad**: La transcripción es más fácil de seguir con menos interrupciones.

### Personalización

Si deseas ajustar el tamaño de los utterances, puedes modificar el valor del parámetro `utt_split` en el archivo `backend/utils/transcriber.py`:

```python
options = PrerecordedOptions(
    ...
    utterances=True,
    utt_split=2.5  # Ajusta este valor según tus necesidades
)
```

- **Valores más bajos** (ej: 0.8, valor predeterminado): Generan más utterances, más cortos y con timestamps más frecuentes.
- **Valores más altos** (ej: 3.0 o 4.0): Generan menos utterances, más largos y con timestamps menos frecuentes.
2. Para añadir fondos adicionales:
   - Ve a la sección "Billing" (Facturación) en el menú lateral.
   - Haz clic en "Add Payment Method" (Añadir método de pago).
   - Ingresa los datos de tu tarjeta de crédito o débito.
   - Selecciona "Add Funds" (Añadir fondos) e ingresa la cantidad deseada.

## 4. Configurar el Proyecto con Deepgram

1. Abre el archivo `.env` en la carpeta `backend` de tu proyecto.
2. Añade tu clave API de Deepgram:
   ```
   DEEPGRAM_API_KEY=tu_clave_api_aqui
   ```
3. También puedes configurar el modelo de transcripción que deseas utilizar:
   ```
   TRANSCRIPTION_MODEL=nova-2
   ```

## 5. Modelos Disponibles de Deepgram

Deepgram ofrece varios modelos con diferentes características y precios:

- **Nova-2**: (Recomendado) La última generación del modelo, ofrece la mejor precisión para español y otros idiomas. Es más rápido y preciso que el modelo estándar.
- **Enhanced**: Un modelo de alta precisión, especialmente bueno para conversaciones y escenarios con ruido de fondo.
- **Base**: El modelo básico, con menor precisión pero más económico.

## 6. Configurar Deepseek API para Generación de Resúmenes

A partir de la versión 1.0, el proyecto utiliza Deepseek para generar automáticamente resúmenes de las transcripciones.

### 6.1 Crear una Cuenta en Deepseek

1. Ve al sitio web de Deepseek: [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. Regístrate usando tu correo electrónico o con Google/GitHub.
3. Completa el proceso de registro y verifica tu cuenta.

### 6.2 Obtener tu API Key de Deepseek

1. Inicia sesión en la plataforma de Deepseek.
2. Navega a la sección "API Keys" en tu perfil o panel de control.
3. Crea una nueva API key con un nombre descriptivo (ej: "WhisperMeetingProject").
4. **IMPORTANTE**: Copia inmediatamente la clave API generada y guárdala en un lugar seguro.

### 6.3 Configurar el Proyecto con Deepseek

1. Abre el archivo `.env` en la carpeta `backend` de tu proyecto.
2. Añade tu clave API de Deepseek junto a la de Deepgram:
   ```
   DEEPGRAM_API_KEY=tu_clave_deepgram_aqui
   DEEPSEEK_API_KEY=tu_clave_deepseek_aqui
   ```

## 7. Consideraciones de Uso y Crédito

- Las transcripciones con Deepgram se facturan por minuto de audio procesado.
- Los resúmenes con Deepseek se facturan por tokens procesados (entrada y salida).
- Ambos servicios ofrecen créditos gratuitos para comenzar:
  - Deepgram: $200 en crédito gratuito al registrarte
  - Deepseek: Varía según promociones, consulta su página

## 8. Solución de Problemas Comunes

- **Error de autenticación**: Verifica que las API keys estén correctamente escritas en el archivo `.env`.
- **Límites de tamaño**: Deepgram limita los archivos a 2 horas o 1GB. Deepseek tiene límites de tokens por solicitud.
- **Problemas de transcripción**: Para mejorar resultados, considera usar archivos de audio con buena calidad y poco ruido de fondo.

---

Si encuentras algún problema o necesitas ayuda adicional, consulta la [documentación oficial de Deepgram](https://developers.deepgram.com/docs/) o comunícate con su soporte técnico.
