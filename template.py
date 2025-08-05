import os
from pathlib import Path



# Define subdirectories and files
folders = [
    base_dir,
    base_dir / "business_data"
]

files = {
    base_dir / "app.py": """# app.py
# Main Streamlit app logic goes here
# Replace this content with the full chatbot code
print("Hello from Product-Catalogue-Chatbot!")\n""",

    base_dir / "requirements.txt": """streamlit
PyPDF2
langchain
faiss-cpu
google-generativeai
python-dotenv
""",

    base_dir / ".env": """# Optional: Store your Gemini API key here
GOOGLE_API_KEY=your_google_api_key_here
"""
}

# Create folders
for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)

# Create files with content
for file_path, content in files.items():
    with open(file_path, "w") as f:
        f.write(content)

print(f"Template created at: {base_dir.resolve()}")
