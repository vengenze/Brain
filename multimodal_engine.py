import os
from google import genai
from PIL import Image

# Ensure API key is loaded
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("⚠️ GEMINI_API_KEY environment variable not found in this session.")
    api_key = input("Please paste your Gemini API key here: ").strip()
    os.environ["GEMINI_API_KEY"] = api_key

# Initialize Gemini Client explicitly with the key
client = genai.Client(api_key=api_key)

def analyze_media(file_path: str, prompt: str):
    if not os.path.exists(file_path):
        return f"❌ Error: File '{file_path}' not found on disk."

    print(f"👁️ [Multimodal Core] Reading file '{file_path}' with prompt: '{prompt}'...")
    
    try:
        ext = file_path.lower()
        
        # 1. Handle Image Files (PNG, JPG, WEBP)
        if ext.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
            img = Image.open(file_path)
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=[prompt, img]
            )
            return response.text

        # 2. Handle Text / Code Files (TXT, MD, PY, JSON)
        elif ext.endswith(('.txt', '.md', '.py', '.json', '.log', '.csv')):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                file_text = f.read()
            full_prompt = f"Document Content from '{file_path}':\n\n{file_text}\n\nUser Request: {prompt}"
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=full_prompt
            )
            return response.text

        # 3. Handle PDFs and other binary documents using Gemini Files API
        elif ext.endswith('.pdf'):
            print("📤 Uploading document to Gemini session...")
            uploaded_file = client.files.upload(file=file_path)
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=[uploaded_file, prompt]
            )
            return response.text
        else:
            return "❌ Unsupported file format. Please use images (.png/.jpg), text files (.txt/.md/.py), or PDFs (.pdf)."

    except Exception as e:
        return f"❌ Multimodal Processing Error: {e}"

def main():
    print("=================================================")
    print(" 👁️ TERMUX MULTIMODAL VISION & DOCUMENT ENGINE   ")
    print("=================================================")

    while True:
        try:
            file_path = input("\nEnter file path (or type 'exit' to quit): ").strip()
            if not file_path or file_path.lower() in ["exit", "quit"]:
                print("Shutting down multimodal engine. Goodbye!")
                break
            
            if not os.path.exists(file_path):
                print(f"⚠️ File '{file_path}' does not exist. Check your path.")
                continue

            user_prompt = input("Enter your instruction / prompt for this file: ").strip()
            if not user_prompt:
                user_prompt = "Analyze this file and summarize its contents."

            result = analyze_media(file_path, user_prompt)
            print("\n--- AI ANALYSIS & ADJUSTMENT ---")
            print(result)
            print("--------------------------------\n")
            
        except KeyboardInterrupt:
            print("\nEngine interrupted. Exiting.")
            break

if __name__ == "__main__":
    main()
