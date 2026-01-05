import os
import datetime
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def register_font():
    win_dir = os.environ.get('WINDIR', 'C:\\Windows')
    fonts_dir = os.path.join(win_dir, 'Fonts')

    font_priority_list = [
        "arial.ttf",      
        "tahoma.ttf",     
        "verdana.ttf",    
        "segoeui.ttf"     
    ]

    registered_name = "Helvetica" 

    for filename in font_priority_list:
        full_path = os.path.join(fonts_dir, filename)
        
        if os.path.exists(full_path):
            try:
                pdfmetrics.registerFont(TTFont("WinSystemFont", full_path))
                registered_name = "WinSystemFont"
                #print(f"Załadowano czcionkę: {filename}")
                break 
            except Exception as e:
                print(f"Nie udało się załadować {filename}: {e}")
                continue

    return registered_name


#generowanie raportu
def create_pdf_report(output_path, analyzed_file, base_path, difficulty, mode,
                      percent_text, percent_eqs, compared_files,
                      final_text, segments_with_sources):

    styles = getSampleStyleSheet()

    current_font = register_font()

    for style in styles.byName.values():
        style.fontName = current_font  
        style.alignment = 4

    story = []

    story.append(Paragraph("Raport analizy plagiatu", styles["Title"]))
    story.append(Spacer(1, 12))

	#dane	
    story.append(Paragraph(f"<b>Analizowany plik:</b> {os.path.basename(analyzed_file)}", styles["Normal"]))
    #story.append(Paragraph(f"<b>Baza porównawcza:</b> {os.path.basename(base_path)}", styles["Normal"]))
    story.append(Paragraph(f"<b>Poziom trudności:</b> {difficulty}", styles["Normal"]))
    story.append(Paragraph(f"<b>Tryb analizy:</b> {mode}", styles["Normal"]))

    formatted_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph(f"<b>Data analizy:</b> {formatted_date}", styles["Normal"]))
    story.append(Spacer(1, 12))
	
	#wyniki
    story.append(Paragraph("<b>Wyniki:</b>", styles["Heading2"]))

    if mode in ("all", "text_only","fast"):
        story.append(Paragraph(f"Plagiat tekstu: {percent_text:.2f}%", styles["Normal"]))

    if mode in ("all", "eqs_only","fast"):
        story.append(Paragraph(f"Plagiat równań: {percent_eqs:.2f}%", styles["Normal"]))

    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Wykryte fragmenty podobne:</b>", styles["Heading2"]))

    highlighted_text, bibliography = highlight_final_text(final_text, segments_with_sources)

    story.append(Paragraph(highlighted_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Źródła podobieństw:</b>", styles["Heading2"]))
    for idx, src in bibliography:
        story.append(Paragraph(f"[{idx}] {src}", styles["Normal"]))

	# lista plików
    story.append(Paragraph("<b>Porównane pliki:</b>", styles["Heading3"]))
    for f in compared_files:
        story.append(Paragraph(os.path.basename(f), styles["Normal"]))


    pdf = SimpleDocTemplate(output_path, pagesize=A4)
    pdf.build(story)


def find_fragments_and_sources(segments):
    if not segments:
        return []

    segments_sorted = sorted(segments, key=lambda x: x[0])  

    merged = [segments_sorted[0]]

    for (start, end), src in segments_sorted[1:]:
        (last_start, last_end), last_src = merged[-1]

        if start <= last_end:
            merged[-1] = ((last_start, max(last_end, end)), last_src)
        else:
            merged.append(((start, end), src))

    return merged

def build_final_text(clean_text: str) -> str:
    text = re.sub(r'\s+', ' ', clean_text).strip()

    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    return "\n\n".join(paragraphs)


def highlight_final_text(final_text, segments_with_sources):
    words = final_text.split()
    merged = find_fragments_and_sources(segments_with_sources)

    output = []
    bibliography = []
    pointer = 0
    idx = 1

    for (start, end), src in merged:
        output.append(" ".join(words[pointer:start]))

        fragment = " ".join(words[start:end])
        output.append(f"<font backColor='#FFF2A8'>{fragment}</font>[{idx}]")

        bibliography.append((idx, src))
        pointer = end
        idx += 1

    output.append(" ".join(words[pointer:]))

    return " ".join(output), bibliography