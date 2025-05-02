import os
import logging
from pathlib import Path
from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv

# Load environment variables with explicit path
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class Transcriber:
    """Class for transcribing audio files using Deepgram API."""
    
    def __init__(self, model_size="base"):
        """
        Initialize the transcriber with the specified model.
        
        Args:
            model_size: Size of the model to use ('base', 'enhanced', 'nova', 'nova-2', 'nova-3', 'whisper')
        """
        self.model_size = model_size
        
        # Mapeamos los tamaños del modelo a los modelos disponibles en Deepgram
        self.model_mapping = {
            "tiny": "whisper-tiny",
            "base": "base",
            "small": "whisper-small",
            "medium": "whisper-medium",
            "large": "whisper-large",
            "enhanced": "enhanced",
            "nova": "nova",
            "nova-2": "nova-2",
            "nova-3": "nova-3"
        }
        
        # Información adicional sobre modelos especializados
        self.specialized_models = {
            "nova-2-meeting": "Optimizado para reuniones en salas de conferencia",
            "nova-2-phonecall": "Optimizado para llamadas telefónicas de baja calidad",
            "enhanced-meeting": "Optimizado para reuniones (versión Enhanced)",
            "enhanced-phonecall": "Optimizado para llamadas telefónicas (versión Enhanced)"
        }
        
        # Obtener la API key de Deepgram
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        if not self.deepgram_api_key:
            logger.error("DEEPGRAM_API_KEY no está configurada en el archivo .env")
            raise ValueError("DEEPGRAM_API_KEY no configurada. Por favor, añade tu clave API en el archivo .env")
        
        # Inicializar cliente de Deepgram
        try:
            self.deepgram = DeepgramClient(self.deepgram_api_key)
            logger.info(f"Cliente Deepgram inicializado con éxito para el modelo: {model_size}")
        except Exception as e:
            logger.error(f"Error al inicializar el cliente Deepgram: {e}", exc_info=True)
            raise ValueError(f"Error al inicializar Deepgram: {str(e)}")
    
    def transcribe(self, audio_path):
        """
        Transcribe an audio file using Deepgram API.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Tuple containing transcription text and utterances data
        """
        audio_path = Path(audio_path)
        logger.info(f"Iniciando transcripción de {audio_path} con Deepgram API")
        
        try:
            # Determinamos el modelo a usar según el mapping
            api_model = self.model_mapping.get(self.model_size, "nova-2")
            
            # Configuramos las opciones de transcripción
            options = PrerecordedOptions(
                model=api_model,
                smart_format=True,  # Formatea automáticamente números, puntuación, etc.
                language="es-419",  # Idioma español de Latinoamérica (mejor para acentos latinoamericanos)
                punctuate=True,     # Añade puntuación
                diarize=True,       # Identifica diferentes hablantes
                utterances=True,
                utt_split=2.5    # [SF] Habilitamos explícitamente la detección de utterances
            )
            
            # Verificamos que el idioma sea español de Latinoamérica
            assert options.language == "es-419", "El idioma debe estar configurado como español de Latinoamérica"
            
            # Realizamos la transcripción - API actualizada para deepgram-sdk 3.10.1+
            with open(audio_path, "rb") as audio_file:
                # Método correcto para la API v3.10.1 (transcribe_file)
                response = self.deepgram.listen.rest.v("1").transcribe_file(
                    {"buffer": audio_file}, 
                    options
                )
            
            # Extraemos la transcripción y los utterances del formato de respuesta
            transcription = ""
            utterances_data = []
            
            if response and hasattr(response, "results"):
                # Obtenemos la transcripción completa
                transcription = response.results.channels[0].alternatives[0].transcript
                
                # Extraemos los utterances si están disponibles
                if hasattr(response.results, "utterances"):
                    utterances_data = response.results.utterances
                    logger.info(f"Se detectaron {len(utterances_data)} utterances")
                    
                    # Si es un objeto con método to_dict, intentamos usarlo
                    if hasattr(utterances_data, 'to_dict'):
                        try:
                            utterances_data = utterances_data.to_dict()
                        except Exception as e:
                            logger.warning(f"Error al convertir utterances a dict: {e}")
                else:
                    # Intentamos buscar en diferentes estructuras según la versión de la API
                    try:
                        response_dict = response.to_dict()
                        if "utterances" in response_dict["results"]:
                            utterances_data = response_dict["results"]["utterances"]
                            logger.info(f"Se detectaron {len(utterances_data)} utterances (desde dict)")
                    except (KeyError, TypeError) as e:
                        logger.warning(f"No se pudieron extraer utterances: {e}")
            else:
                # Si el formato de respuesta es diferente, intentamos obtener la transcripción
                # de la manera más segura posible
                try:
                    # Para la v3.10.1 del SDK
                    response_dict = response.to_dict()
                    transcription = response_dict["results"]["channels"][0]["alternatives"][0]["transcript"]
                    
                    # Intentamos extraer utterances del diccionario
                    if "utterances" in response_dict["results"]:
                        utterances_data = response_dict["results"]["utterances"]
                        logger.info(f"Se detectaron {len(utterances_data)} utterances (desde dict)")
                except (KeyError, TypeError, IndexError) as e:
                    logger.error(f"Error al extraer la transcripción o utterances: {e}", exc_info=True)
                    raise ValueError("No se pudo extraer la transcripción de la respuesta de Deepgram")
            
            # Verificar que utterances_data sea siempre una lista
            if not isinstance(utterances_data, list):
                utterances_data = [utterances_data] if utterances_data else []
            
            logger.info(f"Transcripción completada con éxito mediante Deepgram. Longitud: {len(transcription)} caracteres")
            return transcription, utterances_data
            
        except Exception as e:
            logger.error(f"Error durante la transcripción con Deepgram API: {e}", exc_info=True)
            raise ValueError(f"Falló la transcripción: {str(e)}")
    
    def get_available_models(self):
        """
        Devuelve la lista de modelos disponibles con sus descripciones.
        
        Returns:
            dict: Diccionario con los modelos disponibles y sus descripciones
        """
        models_info = {
            "base": "Modelo básico - buena relación calidad/precio",
            "enhanced": "Mejor precisión y reconocimiento de palabras que el modelo base",
            "nova": "Entrenado en más de 100 dominios, ideal para aplicaciones diversas",
            "nova-2": "Segunda generación de Nova, mejor precisión y reconocimiento de entidades",
            "nova-3": "La versión más avanzada con mayor precisión y capacidades multilingües",
            "whisper-tiny": "Whisper de OpenAI (39M parámetros) - el más pequeño",
            "whisper-base": "Whisper de OpenAI (74M parámetros)",
            "whisper-small": "Whisper de OpenAI (244M parámetros)",
            "whisper-medium": "Whisper de OpenAI (769M parámetros)",
            "whisper-large": "Whisper de OpenAI (1550M parámetros) - el más grande"
        }
        
        # Añadir los modelos especializados
        models_info.update(self.specialized_models)
        
        return models_info

    def generate_summaries(self, transcription, method="deepseek"):
        """
        Genera resúmenes, puntos clave y elementos de acción a partir de la transcripción.
        
        Args:
            transcription: Texto completo de la transcripción
            method: Método para generar resúmenes ("deepseek" o "local")
            
        Returns:
            Tupla de (short_summary, key_points, action_items)
        """
        logger.info(f"Generando resúmenes con método: {method}")
        logger.info(f"Longitud de la transcripción: {len(transcription)} caracteres")
        
        try:
            if method == "deepseek":
                # Usar Deepseek API
                logger.info("Utilizando Deepseek API para generar resúmenes")
                short_summary, key_points, action_items = self._generate_summaries_with_deepseek(transcription)
                
                # Verificar resultados
                logger.info(f"Resultados de Deepseek - Short summary: {len(short_summary)} caracteres")
                logger.info(f"Resultados de Deepseek - Key points: {len(key_points)} puntos")
                logger.info(f"Resultados de Deepseek - Action items: {len(action_items)} elementos")
                
                return short_summary, key_points, action_items
            else:
                # Usar método simple local
                logger.info("Utilizando método local simple para generar resúmenes")
                return self._generate_simple_summaries(transcription)
        except Exception as e:
            logger.error(f"Error en generate_summaries: {str(e)}", exc_info=True)
            logger.info("Cambiando a método de respaldo debido a error")
            return self._generate_simple_summaries(transcription)

    def _generate_summaries_with_deepseek(self, transcription):
        """
        Genera resúmenes utilizando la API de Deepseek.
        
        Args:
            transcription: Texto completo de la transcripción
            
        Returns:
            Tupla de (short_summary, key_points, action_items)
        """
        try:
            from openai import OpenAI
            import json
            import time
            
            # Obtener la API key de las variables de entorno
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                logger.error("DEEPSEEK_API_KEY no configurada en archivo .env")
                raise ValueError("DEEPSEEK_API_KEY no configurada. Por favor, añade tu clave API en el archivo .env")
            
            # Inicializar cliente de Deepseek (compatible con OpenAI)
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com",  # URL base sin /v1
                timeout=120.0  # Aumentar timeout a 120 segundos
            )
            
            # Configuración de límites de tokens
            # La ventana de contexto total es de 64K tokens
            # Reservamos 8K tokens para la salida (respuesta completa)
            MAX_INPUT_TOKENS = 56000  # 64K - 8K para respuesta
            
            # Conversión aproximada de tokens a caracteres (varía según el idioma)
            # Para español, una estimación conservadora es ~3.5 caracteres por token
            MAX_INPUT_CHARACTERS = int(MAX_INPUT_TOKENS * 3.5)  # ≈ 196,000 caracteres
            
            # Truncar la transcripción si es muy larga
            truncated = False
            if len(transcription) > MAX_INPUT_CHARACTERS:
                logger.warning(f"Transcripción muy larga ({len(transcription)} caracteres), truncando a {MAX_INPUT_CHARACTERS} caracteres...")
                # Truncamos para dejar espacio para el prompt del sistema
                # Restamos 2000 caracteres para el prompt del sistema (~570 tokens)
                transcription = transcription[:MAX_INPUT_CHARACTERS - 2000]
                truncated = True
            
            # Preparar el prompt para el resumen
            system_prompt = """
            Eres un asistente especializado en resumir transcripciones de reuniones en español.
            Debes analizar la transcripción proporcionada y generar:
            
            1. Un resumen corto (TL;DR) de máximo 150 palabras que capture la esencia de la reunión
            2. Una lista de puntos clave (máximo 7 puntos) que resalten las ideas principales discutidas
            3. Una lista de elementos de acción o tareas pendientes identificadas en la reunión (si las hay)
            
            Responde ÚNICAMENTE en formato JSON con las siguientes claves:
            - "short_summary": el resumen corto como texto
            - "key_points": array de strings, cada uno representando un punto clave
            - "action_items": array de strings, cada uno representando un elemento de acción
            
            Si la transcripción está truncada, enfócate en resumir la parte disponible sin mencionar que está incompleta.
            """
            
            # Mensaje de usuario
            user_message = f"Aquí está la transcripción de la reunión para resumir:"
            if truncated:
                user_message += " (Nota: Esta es la primera parte de una transcripción más larga)"
            user_message += f"\n\n{transcription}"
            
            logger.info(f"Enviando solicitud a Deepseek API para generar resumen (longitud transcripción: {len(transcription)} caracteres)")
            
            # Sistema de reintentos
            max_retries = 3
            retry_delay = 5  # segundos
            
            for attempt in range(max_retries):
                try:
                    # Llamada a la API
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        temperature=1.3,  # Temperatura para conversación general
                        max_tokens=4096,  # Ajustar según sea necesario (máximo 8192)
                        response_format={"type": "json_object"}  # Solicitar respuesta en formato JSON
                    )
                    
                    # Si llegamos aquí, la llamada tuvo éxito
                    break
                    
                except Exception as e:
                    logger.warning(f"Intento {attempt+1}/{max_retries} falló: {str(e)}")
                    if attempt < max_retries - 1:
                        logger.info(f"Reintentando en {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Backoff exponencial
                    else:
                        # Agotamos los reintentos, lanzar excepción
                        logger.error(f"No se pudo conectar a la API de Deepseek después de {max_retries} intentos")
                        raise
            
            # Extraer la respuesta
            result_text = response.choices[0].message.content
            logger.debug(f"Respuesta recibida de Deepseek: {result_text[:200]}...")
            
            # Procesar el JSON
            try:
                result = json.loads(result_text)
                
                short_summary = result.get("short_summary", "")
                key_points = result.get("key_points", [])
                action_items = result.get("action_items", [])
                
                # Validar y limpiar los resultados
                if not isinstance(short_summary, str):
                    short_summary = str(short_summary) if short_summary else ""
                
                if not isinstance(key_points, list):
                    key_points = [str(key_points)] if key_points else []
                else:
                    key_points = [str(point) for point in key_points if point]
                
                if not isinstance(action_items, list):
                    action_items = [str(action_items)] if action_items else []
                else:
                    action_items = [str(item) for item in action_items if item]
                
                return short_summary, key_points, action_items
                
            except json.JSONDecodeError as e:
                logger.error(f"Error al procesar la respuesta JSON: {str(e)}")
                logger.debug(f"Respuesta recibida: {result_text}")
                raise ValueError(f"La API de Deepseek no devolvió un JSON válido: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error al generar resúmenes con Deepseek: {str(e)}")
            logger.info("Utilizando método simple de fallback para generar resúmenes")
            return self._generate_simple_summaries(transcription)

    def _generate_simple_summaries(self, transcription):
        """
        Método simple de fallback para generar resúmenes básicos.
        Útil cuando la API externa no está disponible.
        
        Args:
            transcription: Texto completo de la transcripción
            
        Returns:
            Tupla de (short_summary, key_points, action_items)
        """
        logger.info("Utilizando método simple para generar resumen (fallback)")
        
        # Resumen simple: primeras 150 palabras
        words = transcription.split()
        short_summary = " ".join(words[:min(150, len(words))])
        
        # Puntos clave simples: primeras frases de diferentes párrafos
        paragraphs = transcription.split('\n\n')
        key_points = []
        for i, para in enumerate(paragraphs[:7]):
            if para.strip():
                sentences = para.split('.')
                if sentences[0].strip():
                    key_points.append(sentences[0].strip() + '.')
        
        # No podemos extraer action items de forma simple
        action_items = []
        
        return short_summary, key_points, action_items
