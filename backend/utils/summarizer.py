import os
import logging
from pathlib import Path
import torch
from transformers import pipeline, BartForConditionalGeneration, BartTokenizer
from transformers import T5ForConditionalGeneration, T5Tokenizer
import openai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Summarizer:
    """Class for generating summaries from transcriptions."""
    
    def __init__(self):
        """Initialize the summarizer."""
        self.local_model = None
        self.local_tokenizer = None
        self.model_type = None  # 'bart' or 't5'
        self.gpt_model = "gpt-3.5-turbo"  # Default GPT model
        
        # Try to get API key from environment variable
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
    
    def _load_local_model(self, model_type="bart"):
        """
        Load a local summarization model.
        
        Args:
            model_type: Type of model to load ('bart' or 't5')
        """
        if self.local_model is not None and self.model_type == model_type:
            return
        
        self.model_type = model_type
        
        try:
            if model_type == "bart":
                logger.info("Loading BART model for summarization")
                model_name = "facebook/bart-large-cnn"
                self.local_tokenizer = BartTokenizer.from_pretrained(model_name)
                self.local_model = BartForConditionalGeneration.from_pretrained(model_name)
            elif model_type == "t5":
                logger.info("Loading T5 model for summarization")
                model_name = "t5-small"
                self.local_tokenizer = T5Tokenizer.from_pretrained(model_name)
                self.local_model = T5ForConditionalGeneration.from_pretrained(model_name)
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
                
        except Exception as e:
            logger.error(f"Error loading local model: {e}")
            raise ValueError(f"Failed to load local model: {e}")
    
    def _summarize_with_local_model(self, text, max_length=150, min_length=30):
        """
        Generate a summary using a local model.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Generated summary
        """
        # Default to BART if no model is loaded
        if self.local_model is None:
            self._load_local_model("bart")
        
        try:
            # Truncate text if it's too long for the model
            max_input_length = 1024  # Adjust based on model limitations
            tokens = self.local_tokenizer.encode(text, truncation=True, max_length=max_input_length)
            truncated_text = self.local_tokenizer.decode(tokens, skip_special_tokens=True)
            
            if self.model_type == "bart":
                inputs = self.local_tokenizer(truncated_text, return_tensors="pt", max_length=max_input_length, truncation=True)
                summary_ids = self.local_model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )
                summary = self.local_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                
            elif self.model_type == "t5":
                inputs = self.local_tokenizer("summarize: " + truncated_text, return_tensors="pt", max_length=max_input_length, truncation=True)
                summary_ids = self.local_model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )
                summary = self.local_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with local model: {e}")
            return "Error generating summary with local model."
    
    def _summarize_with_gpt(self, text, type="short"):
        """
        Generate a summary using GPT.
        
        Args:
            text: Text to summarize
            type: Type of summary ('short' or 'detailed')
            
        Returns:
            Generated summary
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. Using local model instead.")
            if type == "short":
                return self._summarize_with_local_model(text, max_length=100, min_length=30)
            else:
                return self._summarize_with_local_model(text, max_length=200, min_length=100)
        
        # Configure OpenAI
        openai.api_key = self.openai_api_key
        
        try:
            # Prepare prompt based on summary type
            if type == "short":
                prompt = f"Please provide a very concise summary (3-4 key points) of the following meeting transcript:\n\n{text}"
            else:
                prompt = f"Please provide a detailed summary (one paragraph covering the main points) of the following meeting transcript:\n\n{text}"
            
            # Make API call
            response = openai.chat.completions.create(
                model=self.gpt_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes meeting transcripts accurately and concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500 if type == "detailed" else 200,
                temperature=0.5
            )
            
            # Extract and return summary
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with GPT: {e}")
            logger.info("Falling back to local model")
            
            # Fallback to local model
            if type == "short":
                return self._summarize_with_local_model(text, max_length=100, min_length=30)
            else:
                return self._summarize_with_local_model(text, max_length=200, min_length=100)
    
    def generate_short_summary(self, text, method="local"):
        """
        Generate a short summary.
        
        Args:
            text: Text to summarize
            method: Summarization method ('local' or 'gpt')
            
        Returns:
            Short summary
        """
        logger.info(f"Generating short summary using {method} method")
        
        if method == "gpt":
            return self._summarize_with_gpt(text, type="short")
        else:
            return self._summarize_with_local_model(text, max_length=100, min_length=30)
    
    def generate_detailed_summary(self, text, method="local"):
        """
        Generate a detailed summary.
        
        Args:
            text: Text to summarize
            method: Summarization method ('local' or 'gpt')
            
        Returns:
            Detailed summary
        """
        logger.info(f"Generating detailed summary using {method} method")
        
        if method == "gpt":
            return self._summarize_with_gpt(text, type="detailed")
        else:
            return self._summarize_with_local_model(text, max_length=200, min_length=100)
