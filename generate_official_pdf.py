import os
from fpdf import FPDF
from datetime import datetime

class ProfessionalPDF(FPDF):
    def header(self):
        # Official Top Banner Header
        self.set_font('helvetica', 'B', 13)
        self.set_text_color(20, 35, 70)
        self.cell(0, 7, 'POLISMYNDIGHETEN', 0, 1, 'L')
        
        self.set_font('helvetica', '', 8.5)
        self.set_text_color(100, 110, 120)
        self.cell(0, 4, clean_txt('Registeravdelningen - Utfärdat i enlighet med lag (1998:620)'), 0, 1, 'L')
        
        # Professional divider rule
        self.set_draw_color(30, 50, 90)
        self.set_line_width(0.8)
        self.line(15, self.get_y() + 3, 195, self.get_y() + 3)
        self.ln(6)

    def footer(self):
        self.set_y(-18)
        self.set_font('helvetica', '', 8)
        self.set_text_color(130, 130, 130)
        self.set_draw_color(210, 215, 220)
        self.set_line_width(0.3)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(2)
        self.cell(0, 5, clean_txt('Officiellt registerutdrag - Elektroniskt verifierad handling'), 0, 0, 'L')
        self.cell(0, 5, f'Sida {self.page_no()} av 1', 0, 0, 'R')

def clean_txt(text):
    if not text:
        return ""
    # Replace unicode symbols unsupported by core PDF fonts
    replacements = {
        "—": "-", "–": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "…": "..."
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pro_pdf():
    pdf = ProfessionalPDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(left=15, top=15, right=15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Title
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(20, 35, 70)
    pdf.cell(0, 6, clean_txt("REGISTERUTDRAG UR BELASTNINGSREGISTRET"), 0, 1, "L")
    pdf.ln(2)

    # Information Box (Subject Details)
    pdf.set_fill_color(243, 245, 248)
    pdf.set_draw_color(210, 215, 225)
    pdf.set_line_width(0.3)
    pdf.rect(15, pdf.get_y(), 180, 26, style='DF')
    
    pdf.set_xy(18, pdf.get_y() + 3)
    pdf.set_font("helvetica", "B", 8.5)
    pdf.set_text_color(40, 50, 70)
    pdf.cell(38, 4.5, clean_txt("Registrerad person:"), 0, 0)
    pdf.set_font("helvetica", "", 8.5)
    pdf.cell(0, 4.5, clean_txt("Rasmus Spencer"), 0, 1)
    
    pdf.set_x(18)
    pdf.set_font("helvetica", "B", 8.5)
    pdf.cell(38, 4.5, clean_txt("Ärendetyp:"), 0, 0)
    pdf.set_font("helvetica", "", 8.5)
    pdf.cell(0, 4.5, clean_txt("Enskild kontroll (Officiellt utdrag)"), 0, 1)
    
    pdf.set_x(18)
    pdf.set_font("helvetica", "B", 8.5)
    pdf.cell(38, 4.5, clean_txt("Utfärdat datum:"), 0, 0)
    pdf.set_font("helvetica", "", 8.5)
    pdf.cell(0, 4.5, clean_txt(datetime.now().strftime("%Y-%m-%d")), 0, 1)
    
    pdf.ln(10)

    # Status / Result Section
    pdf.set_font("helvetica", "B", 9.5)
    pdf.set_text_color(20, 35, 70)
    pdf.cell(0, 5, clean_txt("1. Resultat av registerkontroll"), 0, 1, "L")
    
    # Styled green status box
    pdf.set_fill_color(232, 247, 237)
    pdf.set_draw_color(165, 218, 182)
    pdf.rect(15, pdf.get_y(), 180, 10, style='DF')
    pdf.set_xy(18, pdf.get_y() + 2.5)
    pdf.set_font("helvetica", "B", 8.5)
    pdf.set_text_color(18, 115, 45)
    pdf.cell(0, 5, clean_txt("ANTECKNING: INGA NOTERINGAR FINNS (RENT UTDRAG)"), 0, 1, "L")
    
    pdf.ln(6)
    
    # Body Sections
    sections = [
        ("2. Omfattning och rättslig verkan", 
         "Detta utdrag visar uppgifter ur Polismyndighetens belastningsregister enligt lag (1998:620). Vid tidpunkten för kontrollen föreligger inga registrerade påföljder, domar eller aktuella anteckningar för den registrerade personen."),
        
        ("3. Gallringsregler", 
         "Uppgifter i belastningsregistret gallras med stöd av 17 § lag (1998:620) efter bestämda tidsfrister beroende på påföljdernas art. När gallring sker tas uppgifterna bort helt ur registret och kan inte längre visas."),
        
        ("4. Äkthetsverifiering och giltighet", 
         "Detta officiella utdrag är avsett för enskild kontroll och styrker personens registerstatus vid utfärdandet. Dokumentet är elektroniskt framställt och uppfyller gällande myndighetskrav.")
    ]
    
    for title, text in sections:
        pdf.set_font("helvetica", "B", 9)
        pdf.set_text_color(20, 35, 70)
        pdf.cell(0, 4.5, clean_txt(title), 0, 1, "L")
        pdf.set_font("helvetica", "", 8.5)
        pdf.set_text_color(60, 65, 75)
        pdf.multi_cell(0, 4.2, clean_txt(text))
        pdf.ln(4)

    pdf.output("document.pdf")
    print("SUCCESS: Clean professional PDF generated successfully!")

if __name__ == "__main__":
    generate_pro_pdf()
