import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'Termux AI Engine - Exported Document', 0, 1, 'R')
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def convert_markdown_to_pdf(md_filename="document.md", pdf_filename="document.pdf"):
    if not os.path.exists(md_filename):
        print(f"❌ Error: {md_filename} not found!")
        return

    # Initialize PDF with explicit safe margins (20mm)
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=20, top=20, right=20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)

    with open(md_filename, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for line in lines:
        line = line.rstrip()
        
        # Skip code block markdown fences
        if line.startswith("```"):
            continue

        # Clean markdown symbols
        clean_line = line.replace("**", "").replace("`", "")
        
        # Prevent layout crashes from extremely long unbroken words or URLs
        if len(clean_line) > 90 and " " not in clean_line:
            clean_line = ' '.join([clean_line[i:i+80] for i in range(0, len(clean_line), 80)])

        try:
            # Safe encoding fallback for standard core fonts
            safe_text = clean_line.encode('latin-1', 'replace').decode('latin-1')

            if line.startswith("# "):
                pdf.set_font("helvetica", "B", 14)
                pdf.set_text_color(15, 23, 42)
                pdf.ln(4)
                pdf.multi_cell(0, 6, safe_text[2:].strip())
                pdf.set_font("helvetica", size=10)
                pdf.set_text_color(51, 65, 85)
            elif line.startswith("## "):
                pdf.set_font("helvetica", "B", 11)
                pdf.set_text_color(15, 23, 42)
                pdf.ln(3)
                pdf.multi_cell(0, 5, safe_text[3:].strip())
                pdf.set_font("helvetica", size=10)
                pdf.set_text_color(51, 65, 85)
            elif line.startswith("- ") or line.startswith("* "):
                pdf.multi_cell(0, 5, "  • " + safe_text[2:].strip())
            elif line.strip() == "":
                pdf.ln(2)
            else:
                pdf.multi_cell(0, 5, safe_text)
        except Exception as ex:
            # Skip any malformed line gracefully without crashing
            continue

    pdf.output(pdf_filename)
    print(f"SUCCESS: Successfully converted '{md_filename}' into '{pdf_filename}'! 📑✨")

if __name__ == "__main__":
    convert_markdown_to_pdf()
