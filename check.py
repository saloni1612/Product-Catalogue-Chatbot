from google.generativeai import list_models
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)
for model in list_models():
    print(model.name, model.supported_generation_methods)
