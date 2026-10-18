import os
import concurrent.futures
import urllib.parse
from io import BytesIO
import requests
from google import genai
from openai import OpenAI
from PIL import Image
from duckduckgo_search import DDGS
from fpdf import FPDF
from datetime import datetime

# ==================== CLIENT INITIALIZATION ====================
gemini_client = genai.Client()
groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY")
)
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)

# ==================== 1. TRI-CORE MIND ====================
def fetch_groq(prompt):
    try:
        res = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"[Groq Error: {e}]"

def fetch_gemini(prompt):
    try:
        res = gemini_client.models.generate_content(model='gemini-3.8-flash', contents=prompt)
        return res.text
    except Exception as e:
        return f"[Gemini Error: {e}]"

def fetch_openrouter(prompt):
    try:
        res = openrouter_client.chat.completions.create(
            model="openrouter/free",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"[OpenRouter Error: {e}]"

def unified_think(prompt):
    print("\n🧠 [Tri-Core Mind] Consulting Gemini, Groq, and OpenRouter in parallel...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        f_groq = executor.submit(fetch_groq, prompt)
        f_gemini = executor.submit(fetch_gemini, prompt)
        f_or = executor.submit(fetch_openrouter, prompt)
        groq_ans, gemini_ans, or_ans = f_groq.result(), f_gemini.result(), f_or.result()

    print("⚡ Hemispheres synchronized. Synthesizing consensus...\n")
    synthesis_prompt = f"""
You are the core consciousness of a tri-engine AI system running locally on mobile.
User Prompt: "{prompt}"
Sub-Mind 1 (Groq): {groq_ans}
Sub-Mind 2 (Gemini): {gemini_ans}
Sub-Mind 3 (OpenRouter): {or_ans}
Task: Cross-examine these viewpoints and synthesize them into a single, highly accurate, and comprehensive final response. Speak with a unified voice.
"""
    try:
        res = gemini_client.models.generate_content(model='gemini-3.8-flash', contents=synthesis_prompt)
        return res.text
    except Exception as e:
        return f"Synthesis Error: {e}"

# ==================== 2. WEB SEARCH TOOL ====================
def web_search(query):
    print(f"🌍 [Web Search] Crawling the internet for: '{query}'...")
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            if not results:
                return "No live search results found."
            for i, r in enumerate(results, 1):
                results_text += f"\nResult {i}:\nTitle: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')}\n"
    except Exception as e:
        return f"Search Error: {e}"

    synthesis_query = f"User search query: '{query}'\n\nLive Search Results:\n{results_text}\n\nTask: Synthesize these live findings into an accurate, clear answer with source URLs."
    return unified_think(synthesis_query)

# ==================== 3. DOCUMENT & PDF COMPILER ====================
def generate_document(topic):
    print(f"📄 [Document Engine] Drafting structured document for: '{topic}'...")
    doc_prompt = f"Write a professional, detailed, and fully structured official document or report about: '{topic}'. Use clean markdown headings and sections."
    content = unified_think(doc_prompt)
    with open("document.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: Markdown draft saved as 'document.md'.")

class ProfessionalPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(20, 35, 70)
        self.cell(0, 7, 'OFFICIAL RECORD // SYSTEM REPORT', 0, 1, 'L')
        self.set_font('helvetica', '', 8.5)
        self.set_text_color(100, 110, 120)
        self.cell(0, 4, 'Generated securely via Termux Tri-Core AI Engine', 0, 1, 'L')
        self.set_draw_color(30, 50, 90)
        self.set_line_width(0.6)
        self.line(15, self.get_y() + 2, 195, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-18)
        self.set_font('helvetica', '', 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 5, f'Date: {datetime.now().strftime("%Y-%m-%d")} | Page {self.page_no()}', 0, 0, 'C')

def clean_txt(text):
    if not text:
        return ""
    return text.replace("—", "-").replace("–", "-").replace("“", '"').replace("”", '"').encode('latin-1', 'replace').decode('latin-1')

def compile_pdf():
    if not os.path.exists("document.md"):
        print("❌ Error: No 'document.md' found. Run /doc <topic> first.")
        return
    print("📑 [PDF Compiler] Converting 'document.md' into 'document.pdf'...")
    pdf = ProfessionalPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=15, top=15, right=15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_font("helvetica", size=9)
    pdf.set_text_color(50, 55, 65)

    with open("document.md", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("# "):
                pdf.set_font("helvetica", "B", 13)
                pdf.set_text_color(20, 35, 70)
                pdf.ln(4)
                pdf.multi_cell(0, 6, clean_txt(line[2:]))
                pdf.set_font("helvetica", size=9)
                pdf.set_text_color(50, 55, 65)
            elif line.startswith("## "):
                pdf.set_font("helvetica", "B", 11)
                pdf.set_text_color(20, 35, 70)
                pdf.ln(3)
                pdf.multi_cell(0, 5, clean_txt(line[3:]))
                pdf.set_font("helvetica", size=9)
                pdf.set_text_color(50, 55, 65)
            elif line.strip() == "":
                pdf.ln(2)
            else:
                pdf.multi_cell(0, 4.5, clean_txt(line.replace("**", "").replace("`", "")))

    pdf.output("document.pdf")
    print("SUCCESS: Compiled cleanly to 'document.pdf'! 📱✨")

# ==================== 4. IMAGE GENERATOR ====================
def generate_image(prompt):
    print(f"🎨 [Image Engine] Rendering art for: '{prompt}'...")
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed=42"
    try:
        res = requests.get(url, timeout=45)
        if res.status_code == 200 and "image" in res.headers.get("content-type", ""):
            image = Image.open(BytesIO(res.content))
            image.save("termux_creation.png")
            print("SUCCESS: Image saved as 'termux_creation.png'! 🎨")
        else:
            print("❌ Image generation failed.")
    except Exception as e:
        print(f"❌ Error: {e}")

# ==================== 5. MULTIMODAL ANALYZER ====================
def analyze_file(file_path, prompt):
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return
    print(f"👁️ [Multimodal Engine] Analyzing '{file_path}'...")
    try:
        ext = file_path.lower()
        if ext.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            img = Image.open(file_path)
            res = gemini_client.models.generate_content(model='gemini-3.8-flash', contents=[prompt, img])
            print("\n--- ANALYSIS RESULT ---")
            print(res.text)
            print("-----------------------")
        elif ext.endswith(('.txt', '.md', '.py', '.json')):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = f.read()
            res = gemini_client.models.generate_content(model='gemini-3.8-flash', contents=f"File Content:\n{data}\n\nTask: {prompt}")
            print("\n--- ANALYSIS RESULT ---")
            print(res.text)
            print("-----------------------")
        elif ext.endswith('.pdf'):
            uploaded = gemini_client.files.upload(file=file_path)
            res = gemini_client.models.generate_content(model='gemini-3.8-flash', contents=[uploaded, prompt])
            print("\n--- ANALYSIS RESULT ---")
            print(res.text)
            print("-----------------------")
        else:
            print("❌ Unsupported file type.")
    except Exception as e:
        print(f"❌ Error: {e}")

# ==================== MAIN COMMAND LOOP ====================
def main():
    print("=========================================================")
    print(" 🚀 ULTIMATE MASTER TERMUX AI ENGINE (Tri-Core + Tools)  ")
    print("=========================================================")
    print("Commands:")
    print("  <any text>              - Ask the Tri-Core Mind")
    print("  /search <query>         - Search the live internet")
    print("  /doc <topic>            - Draft document (.md)")
    print("  /pdf                    - Convert document.md to document.pdf")
    print("  /image <prompt>         - Generate free image (.png)")
    print("  /analyze <path> <prompt>- Analyze image, code, or PDF")
    print("  /exit                   - Quit engine\n")

    while True:
        try:
            user_input = input("\nmaster_engine> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "/exit"]:
                print("Powering down Master Engine. Goodbye!")
                break
            
            if user_input.startswith("/search "):
                print(web_search(user_input[8:].strip()))
            elif user_input.startswith("/doc "):
                generate_document(user_input[5:].strip())
            elif user_input == "/pdf":
                compile_pdf()
            elif user_input.startswith("/image "):
                generate_image(user_input[7:].strip())
            elif user_input.startswith("/analyze "):
                parts = user_input[9:].split(" ", 1)
                fpath = parts[0].strip()
                fprompt = parts[1].strip() if len(parts) > 1 else "Analyze this file."
                analyze_file(fpath, fprompt)
            else:
                print("\n--- MASTER ENGINE ANSWER ---")
                print(unified_think(user_input))
                print("----------------------------")
        except KeyboardInterrupt:
            print("\nEngine interrupted. Exiting.")
            break

if __name__ == "__main__":
    main()
