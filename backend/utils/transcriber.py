import os
import logging
from pathlib import Path
from deepgram import DeepgramClient, PrerecordedOptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
            Transcription text
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
                diarize=True        # Identifica diferentes hablantes
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
            
            # Extraemos la transcripción del formato de respuesta actualizado
            if response and hasattr(response, "results"):
                transcription = response.results.channels[0].alternatives[0].transcript
            else:
                # Si el formato de respuesta es diferente, intentamos obtener la transcripción
                # de la manera más segura posible
                try:
                    # Para la v3.10.1 del SDK
                    response_dict = response.to_dict()
                    transcription = response_dict["results"]["channels"][0]["alternatives"][0]["transcript"]
                except (KeyError, TypeError, IndexError) as e:
                    logger.error(f"Error al extraer la transcripción: {e}", exc_info=True)
                    raise ValueError("No se pudo extraer la transcripción de la respuesta de Deepgram")
            
            logger.info(f"Transcripción completada con éxito mediante Deepgram. Longitud: {len(transcription)} caracteres")
            return transcription
            
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
