import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # 'openai' or 'groq'

# Flask configuration
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "your-secret-key-for-development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"

# Medical specialties configuration
MEDICAL_SPECIALTIES = [
    "cardiology",
    "neurology",
    "pediatrics",
    "oncology",
    "dermatology",
    "psychiatry",
    "internal_medicine",
    "emergency_medicine",
    "traumatology"
]

# Agent configuration
DEFAULT_TEMPERATURE = 0.2
MAX_TOKENS = 4096

# LangGraph configuration
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "True") == "True" 