from enum import Enum
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import snapshot_download
import google.generativeai as genai
import requests
import json
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    TRANSFORMERS_LOCAL = "transformers_local"
    TRANSFORMERS_HUB = "transformers_hub"
    TRANSFORMERS_DOWNLOAD = "transformers_download"

class CodeAssistConfig:
    def __init__(self):
        self.provider = None
        self.model_name = None
        self.local_model = None
        self.local_tokenizer = None
        self.api_keys = {
            "openai": {"api_key": None, "model": "gpt-4"},
            "anthropic": {"api_key": None, "model": "claude-3-sonnet"},
            "gemini": {"api_key": None, "model": "gemini-pro"},
            "huggingface": {"api_key": None, "model": None}
        }

config = CodeAssistConfig()

def call_openai(prompt: str) -> str:
    if not config.api_keys["openai"]["api_key"]:
        return "OpenAI API key not set. Use %set_api_key openai <your_key>"

    try:
        headers = {
            "Authorization": f"Bearer {config.api_keys['openai']['api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": config.api_keys["openai"]["model"],
            "messages": [
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return f"Error: {str(e)}"

def call_anthropic(prompt: str) -> str:
    if not config.api_keys["anthropic"]["api_key"]:
        return "Anthropic API key not set. Use %set_api_key anthropic <your_key>"

    try:
        headers = {
            "x-api-key": config.api_keys["anthropic"]["api_key"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": config.api_keys["anthropic"]["model"],
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.7
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"].strip()
    except Exception as e:
        logger.error(f"Anthropic API error: {e}")
        return f"Error: {str(e)}"

def call_gemini(prompt: str) -> str:
    if not config.api_keys["gemini"]["api_key"]:
        return "Gemini API key not set. Use %set_api_key gemini <your_key>"

    try:
        genai.configure(api_key=config.api_keys["gemini"]["api_key"])
        model = genai.GenerativeModel(config.api_keys["gemini"]["model"])
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Error: {str(e)}"

def download_model(model_name: str, cache_dir: Optional[str] = None) -> str:
    try:
        logger.info(f"Downloading model {model_name}")
        return snapshot_download(
            repo_id=model_name,
            cache_dir=cache_dir,
            local_files_only=False
        )
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        raise

def load_model(model_path: str, device: str = "auto", load_in_8bit: bool = False):
    try:
        model_kwargs = {
            "device_map": device,
            "torch_dtype": torch.float16,
        }
        if load_in_8bit:
            model_kwargs["load_in_8bit"] = True
        
        config.local_tokenizer = AutoTokenizer.from_pretrained(model_path)
        config.local_model = AutoModelForCausalLM.from_pretrained(
            model_path,
            **model_kwargs
        )
        return True
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return False

def generate_with_model(prompt: str) -> str:
    if not config.local_model or not config.local_tokenizer:
        return "Local model not loaded. Use %set_llm_provider transformers_local <model_path>"

    try:
        inputs = config.local_tokenizer(
            prompt,
            return_tensors="pt"
        ).to(config.local_model.device)
        
        outputs = config.local_model.generate(
            inputs["input_ids"],
            max_new_tokens=800,
            temperature=0.7,
            do_sample=True,
            pad_token_id=config.local_tokenizer.eos_token_id
        )
        response = config.local_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):].strip()
    except Exception as e:
        return f"Error generating with local model: {str(e)}"
