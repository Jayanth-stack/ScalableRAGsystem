import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get your Google API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
else:
    # Configure the genai library with your API key
    genai.configure(api_key=GOOGLE_API_KEY)

    print("Available Google Generative AI Models:")
    try:
        # List all models
        for model in genai.list_models():
            # You can filter models here if needed, e.g., only list models that support text generation
            # if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name} (Supported methods: {model.supported_generation_methods})")

    except Exception as e:
        print(f"An error occurred while listing models: {e}")
        print("Please check your API key and network connection.")