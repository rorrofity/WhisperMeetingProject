import os
import tempfile
import logging
from pathlib import Path
from pydub import AudioSegment
import subprocess
import shutil

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Class for processing audio files for transcription with Deepgram."""
    
    def __init__(self, temp_dir=None):
        """
        Initialize the audio processor.
        
        Args:
            temp_dir: Directory for storing temporary files
        """
        self.temp_dir = temp_dir or Path(tempfile.gettempdir())
        # Ya no necesitamos establecer un límite máximo para Deepgram
        # self.max_size_mb = 25  # Maximum size for Whisper processing
        # self.segment_duration_ms = 5 * 60 * 1000  # 5 minutes per segment
    
    def process_audio(self, audio_path):
        """
        Process an audio file for transcription with Deepgram.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Path to the processed audio file ready for transcription
        """
        audio_path = Path(audio_path)
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        
        logger.info(f"Processing audio file: {audio_path} ({file_size_mb:.2f} MB)")
        
        # Convert the audio to WAV format if it's not already
        if audio_path.suffix.lower() != ".wav":
            wav_path = self._convert_to_wav(audio_path)
        else:
            wav_path = audio_path
        
        # Normalize audio (16kHz mono WAV) - Deepgram recomienda este formato
        processed_file = self._normalize_audio(wav_path)
        logger.info(f"Audio processing completed: {processed_file}")
        return processed_file
    
    def _convert_to_wav(self, audio_path):
        """Convert audio file to WAV format."""
        output_path = audio_path.parent / f"{audio_path.stem}.wav"
        
        try:
            audio = AudioSegment.from_file(str(audio_path))
            audio.export(str(output_path), format="wav")
            logger.info(f"Converted {audio_path} to WAV format: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error converting to WAV: {e}")
            # Fallback to ffmpeg directly if pydub fails
            try:
                subprocess.run([
                    "ffmpeg", "-i", str(audio_path), 
                    "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", 
                    str(output_path)
                ], check=True)
                logger.info(f"Converted {audio_path} to WAV format using ffmpeg: {output_path}")
                return output_path
            except Exception as e:
                logger.error(f"Error using ffmpeg: {e}")
                raise ValueError(f"Failed to convert audio file: {e}")
    
    def _normalize_audio(self, wav_path):
        """
        Normalize audio to 16kHz mono WAV for optimal transcription with Deepgram.
        
        Args:
            wav_path: Path to the WAV file
            
        Returns:
            Path to the normalized audio file
        """
        output_path = wav_path.parent / f"{wav_path.stem}_normalized.wav"
        
        try:
            # Load the audio file
            audio = AudioSegment.from_wav(str(wav_path))
            
            # Convert to mono if needed
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Convert to 16kHz if needed
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
            
            # Export the processed audio
            audio.export(str(output_path), format="wav")
            logger.info(f"Normalized audio to 16kHz mono WAV: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error normalizing audio: {e}")
            # Fallback to ffmpeg directly
            try:
                subprocess.run([
                    "ffmpeg", "-i", str(wav_path), 
                    "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", 
                    str(output_path)
                ], check=True)
                logger.info(f"Normalized audio using ffmpeg: {output_path}")
                return output_path
            except Exception as e:
                logger.error(f"Error using ffmpeg: {e}")
                raise ValueError(f"Failed to normalize audio file: {e}")
