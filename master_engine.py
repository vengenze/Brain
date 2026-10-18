import os
import urllib.parse
import subprocess
import time
from io import BytesIO
import requests
from google import genai
from openai import OpenAI
from PIL import Image
from fpdf import FPDF
from datetime import datetime

# Optional Web Search import handling
try:
    from duckduckgo_search import DDGS
    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False

# ==================== SAFE API KEY LOADER ====================
def get_key(var_name, prompt_text):
    key = os.environ.get(var_name)
    if not key or not key.strip():
        print(f"\n⚠️ {var_name} not found in environment.")
        while True:
            key = input(f"Please paste your {prompt_text} (or press Enter to skip): ").strip()
            if key:
                break
            print("⚠️ Skipping this key for now.")
            return ""
        
        os.environ[var_name] = key
        for rc_file in [os.path.expanduser("~/.bashrc"), os.path.expanduser("~/.zshrc")]:
            try:
                with open(rc_file, "a") as f:
                    f.write(f'\nexport {var_name}="{key}"\n')
            except Exception:
                pass
        print(f"✅ {var_name} saved successfully!")
    return key

gemini_key = get_key("GEMINI_API_KEY", "Gemini API Key")
groq_key = get_key("GROQ_API_KEY", "Groq API Key")
openrouter_key = get_key("OPENROUTER_API_KEY", "OpenRouter API Key")
mistral_key = get_key("MISTRAL_API_KEY", "Mistral API Key")

# ==================== CLIENT INITIALIZATION ====================
gemini_client = None
if gemini_key:
    try:
        gemini_client = genai.Client(api_key=gemini_key)
    except Exception:
        pass

groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_key) if groq_key else None
openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_key) if openrouter_key else None

# ==================== 1. SEQUENTIAL SMART-FALLBACK MIND ====================
def unified_think(prompt):
    print("\n🧠 [Smart Mind] Querying available AI backends (Sequential Fallback)...")
    
    # 1. Try OpenRouter Free (High reliability)
    if openrouter_client:
        try:
            res = openrouter_client.chat.completions.create(
                model="openrouter/free",
                messages=[{"role": "user", "content": prompt}],
                timeout=25
            )
            return res.choices[0].message.content
        except Exception:
            pass

    # 2. Try Mistral
    if mistral_key:
        try:
            headers = {"Authorization": f"Bearer {mistral_key}", "Content-Type": "application/json"}
            payload = {"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}]}
            res = requests.post("https://api.mistral.ai/v1/chat/completions", json=payload, headers=headers, timeout=25)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    # 3. Try Gemini Flash
    if gemini_client:
        try:
            res = gemini_client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
            return res.text
        except Exception:
            pass

    # 4. Try Groq
    if groq_client:
        try:
            res = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}],
                timeout=25
            )
            return res.choices[0].message.content
        except Exception:
            pass

    return "❌ All AI backends failed or are currently rate-limited. Please try again in a moment."

# ==================== 2. SHELL EXECUTION AGENT ====================
def execute_terminal_agent(task_description):
    print(f"🤖 [Terminal Agent] Formulating command for: '{task_description}'...")
    command_prompt = f"Write ONLY the exact safe Bash command to accomplish in Termux: '{task_description}'. No markdown blocks, no explanations."
    raw_command = unified_think(command_prompt).strip()
    command = raw_command.replace("```bash", "").replace("```", "").strip()
    
    print(f"\n⚙️ Generated Command: $ {command}")
    confirm = input("Execute this command? [y/N]: ").strip().lower()
    
    if confirm == 'y':
        print("🚀 Executing...")
        start_time = time.time()
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=90)
            elapsed = time.time() - start_time
            print("\n--- SHELL TELEMETRY ---")
            print(f"• Exit Code: {result.returncode}")
            print(f"• Time: {elapsed:.2f}s")
            print("STDOUT:")
            print(result.stdout.strip() if result.stdout.strip() else "[No output]")
            if result.stderr.strip():
                print("STDERR:")
                print(result.stderr.strip())
            print("-----------------------\n")
        except Exception as e:
            print(f"❌ Exception: {e}")
    else:
        print("⚠️ Aborted.")

# ==================== 3. WEB SEARCH TOOL ====================
def web_search(query):
    if not HAS_SEARCH:
        return "❌ Search module not available."
    print(f"🌍 Searching internet for: '{query}'...")
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No results found."
            for i, r in enumerate(results, 1):
                results_text += f"\nResult {i}: {r.get('title')} - {r.get('href')}\nSnippet: {r.get('body')}\n"
    except Exception as e:
        return f"Search Error: {e}"
    return unified_think(f"Search query: '{query}'\nResults:\n{results_text}\nSynthesize into a clear answer with URLs.")

# ==================== 4. DOCUMENT & PDF COMPILER ====================
def generate_document(topic):
    print(f"📄 Drafting document for: '{topic}'...")
    content = unified_think(f"Write a detailed professional report about: '{topic}'. Use markdown.")
    with open("document.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Saved as 'document.md'.")

class ProfessionalPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 7, 'OFFICIAL SYSTEM REPORT', 0, 1, 'L')
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', '', 8)
        self.cell(0, 5, f'Page {self.page_no()}', 0, 0, 'C')

def compile_pdf():
    if not os.path.exists("document.md"):
        print("❌ Error: No 'document.md' found. Run /doc first.")
        return
    print("📑 Compiling PDF...")
    pdf = ProfessionalPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=9)
    with open("document.md", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            pdf.multi_cell(0, 5, line.strip())
    pdf.output("document.pdf")
    print("SUCCESS: Compiled to 'document.pdf'! ✨")

# ==================== 5. IMAGE GENERATOR ====================
def generate_image(prompt):
    print(f"🎨 Rendering image for: '{prompt}'...")
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed=42"
    try:
        res = requests.get(url, timeout=45)
        if res.status_code == 200:
            image = Image.open(BytesIO(res.content))
            image.save("termux_creation.png")
            print("SUCCESS: Saved as 'termux_creation.png'! 🎨")
        else:
            print("❌ Image generation failed.")
    except Exception as e:
        print(f"❌ Error: {e}")

# ==================== MAIN LOOP ====================
def main():
    print("=========================================================")
    print(" 🚀 STABLE MASTER TERMUX AI ENGINE (Sequential Fallback) ")
    print("=========================================================")
    print("Commands: /run, /search, /doc, /pdf, /image, /exit\n")

    while True:
        try:
            user_input = input("\nmaster_engine> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "/exit"]:
                print("Goodbye!")
                break
            
            if user_input.startswith("/run "):
                execute_terminal_agent(user_input[5:].strip())
            elif user_input.startswith("/search "):
                print(web_search(user_input[8:].strip()))
            elif user_input.startswith("/doc "):
                generate_document(user_input[5:].strip())
            elif user_input == "/pdf":
                compile_pdf()
            elif user_input.startswith("/image "):
                generate_image(user_input[7:].strip())
            else:
                print("\n--- MASTER ENGINE ANSWER ---")
                print(unified_think(user_input))
                print("----------------------------")
        except KeyboardInterrupt:
            print("\nEngine interrupted.")
            break

if __name__ == "__main__":
    main()
