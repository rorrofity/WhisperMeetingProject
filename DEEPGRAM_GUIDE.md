# Guía para Configurar Deepgram API

Esta guía te ayudará a crear una cuenta en Deepgram, obtener una API key y agregar crédito a tu cuenta para poder utilizar el servicio de transcripción de audio.

## 1. Crear una Cuenta en Deepgram

1. Ve al sitio web de Deepgram: [https://console.deepgram.com/signup](https://console.deepgram.com/signup)
2. Regístrate usando tu correo electrónico, Google o GitHub.
3. Completa el proceso de registro con tu información personal.
4. Confirma tu cuenta a través del correo electrónico que recibirás.

## 2. Obtener tu API Key

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

## 3. Añadir Crédito a tu Cuenta

1. Deepgram ofrece $200 en crédito gratuito al registrarte, lo que suele ser suficiente para empezar a probar el servicio.
2. Para añadir fondos adicionales:
   - Ve a la sección "Billing" (Facturación) en el menú lateral.
   - Haz clic en "Add Payment Method" (Añadir método de pago).
   - Ingresa los datos de tu tarjeta de crédito o débito.
   - Selecciona "Add Funds" (Añadir fondos) e ingresa la cantidad deseada.

## 4. Configurar el Proyecto

1. Abre el archivo `.env` en la carpeta `backend` de tu proyecto.
2. Añade tu clave API de Deepgram:
   ```
   DEEPGRAM_API_KEY=tu_clave_api_aqui
   ```
3. También puedes configurar el modelo de transcripción que deseas utilizar:
   ```
   TRANSCRIPTION_MODEL=nova-2
   ```

## 5. Modelos Disponibles

Deepgram ofrece varios modelos con diferentes características y precios:

- **Nova-3**: El modelo más avanzado con la mejor precisión y capacidades multilingües.
- **Nova-2**: Excelente para casos de uso generales, con opciones específicas para reuniones, llamadas telefónicas, etc.
- **Enhanced**: Mejor precisión que los modelos base, con buen reconocimiento de palabras poco comunes.
- **Base**: Modelos básicos con buena relación calidad/precio.
- **Whisper**: Variantes del modelo Whisper de OpenAI, con diferentes tamaños disponibles.

Para casos de uso específicos, puedes utilizar variantes como:
- `nova-2-meeting`: Optimizado para reuniones en salas de conferencia.
- `nova-2-phonecall`: Optimizado para llamadas telefónicas.
- `enhanced-meeting`: Versión Enhanced optimizada para reuniones.

## 6. Precios y Costos

- Los precios de Deepgram se basan en la duración del audio procesado.
- El modelo Nova-2 cuesta aproximadamente $0.0125 por minuto ($0.75 por hora).
- Los modelos Nova-3 y Enhanced tienen precios ligeramente más altos.
- Los modelos Base son más económicos.
- Puedes consultar los precios actualizados en [la página de precios de Deepgram](https://deepgram.com/pricing/).

## 7. Limitaciones y Consideraciones

- Deepgram puede manejar archivos de audio grandes sin problemas.
- Los formatos admitidos incluyen MP3, MP4, WAV, M4A, entre otros.
- El servicio funciona mejor con audio claro y de buena calidad.
- Para transcribir idiomas distintos al español, modifica el parámetro `language` en la función `transcribe()` del archivo `transcriber.py`.

---

Si encuentras algún problema o necesitas ayuda adicional, consulta la [documentación oficial de Deepgram](https://developers.deepgram.com/docs/) o comunícate con su soporte técnico.
