import re
from pylatexenc.latex2text import LatexNodes2Text
import os
import sys
import hashlib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import datetime
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

#generowanie raportu
def create_pdf_report(output_path, analyzed_file, base_path, difficulty, mode,
                      percent_text, percent_eqs, compared_files,
                      final_text, segments_with_sources):

    styles = getSampleStyleSheet()

    pdfmetrics.registerFont(TTFont("ArialUni", r"C:\Windows\Fonts\arial.ttf"))
    for style in styles.byName.values():
        style.fontName = "ArialUni"
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


# czyszczenie danych i podział
def preprocessing(file_content):
    m = re.search(r'\\begin{document}(.*)\\end{document}', file_content, flags=re.S)
    if m:
        file_content = m.group(1)

    env_pattern = r'\\begin\{(equation|align|gather|multline|eqnarray)\*?\}(.*?)\\end\{\1\*?\}'
    
    env_eqs = [m.group(2).strip() for m in re.finditer(env_pattern, file_content, flags=re.S)]
    inline_eqs = re.findall(r'\$(.*?)\$', file_content, flags=re.S)
    display_eqs = re.findall(r'\\\[(.*?)\\\]', file_content, flags=re.S)
    equations = env_eqs + inline_eqs + display_eqs

    tmp = re.sub(env_pattern, ' ', file_content, flags=re.S)
    tmp = re.sub(r'\$(.*?)\$', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\\[(.*?)\\\]', ' ', tmp, flags=re.S)
    tmp = re.sub(r'%.*?\n', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\[a-zA-Z]+\*?(?=\s|\n|$|\[)', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\[a-zA-Z]+\*?\{.*?\}', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\begin\{.*?\}', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\end\{.*?\}', ' ', tmp, flags=re.S)
    tmp = re.sub(r'[&\\]', ' ', tmp)
    tmp = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', ' ', tmp, flags=re.S)
    tmp = re.sub(r'[&|]', ' ', tmp)
    tmp = re.sub(r'\\\\', ' ', tmp)


    text = LatexNodes2Text().latex_to_text(tmp)
    clean_text = LatexNodes2Text().latex_to_text(tmp)
    
    text = " ".join(text.split()).lower()
    equations = [eq.replace(' ', '').replace('\n', '') for eq in equations if eq.strip()]
    
    return equations, text, clean_text


# poziomy podobieństwa
def similarity_levels(level):
    if level == "niski":
        return [3, 6, 8, 11]
    elif level == "średni":
        return [4, 8, 11, 14]
    elif level == "wysoki":
        return [5, 9, 13, 17]
    elif level == "bardzo_wysoki":
        return [5, 10, 15, 19]


def split_phrases(text, phrase_len):
    words = text.split()
    phrases = []

    for i in range(len(words) - phrase_len + 1):
        phrase = " ".join(words[i : i + phrase_len])
        phrases.append(phrase)

    return phrases


def phrase_to_set(phrase):
    return set(phrase.split())


def count_common_words_set(set_a, set_b):
    return len(set_a & set_b)


def hash_phrase(phrase):
    return hashlib.sha1(phrase.encode("utf-8")).hexdigest()


def find_similar_phrases(text_a, text_b, level):
    thresholds = similarity_levels(level)
    phrase_lengths = [5, 10, 15, 20]

    similar = []

    for idx, L in enumerate(phrase_lengths):
        t = thresholds[idx]

        phrases_a = split_phrases(text_a, L)
        phrases_b = split_phrases(text_b, L)

        hash_map_b = {}
        for j, phrase_b in enumerate(phrases_b):
            hb = hash_phrase(phrase_b)
            hash_map_b.setdefault(hb, []).append(j)

        sets_b = [phrase_to_set(p) for p in phrases_b]

        for i, phrase_a in enumerate(phrases_a):
            ha = hash_phrase(phrase_a)
            set_pa = phrase_to_set(phrase_a)

            if ha in hash_map_b:
                start = i
                end = i + L
                similar.append((start, end))
                continue  

            for set_pb in sets_b:
                if count_common_words_set(set_pa, set_pb) >= t:
                    start = i
                    end = i + L
                    similar.append((start, end))
                    break

    return similar


def merge_segments(segments):
    if not segments:
        return []

    segments.sort()

    merged = [segments[0]]

    for start, end in segments[1:]:
        last_start, last_end = merged[-1]

        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))

    return merged


def calculate_text_plagiarism(segments, original_text):
    merged = merge_segments(segments)

    words = original_text.split()

    full_text_string = " ".join(words)

    total_chars = len(full_text_string)

    plag_chars = 0

    for start, end in merged:
        fragment = " ".join(words[start:end])
        plag_chars += len(fragment)

    if total_chars == 0:
        return 0, merged

    return 100 * plag_chars / total_chars, merged


def calculate_equation_plagiarism(main_eqs, all_base_eqs):

    if not main_eqs:
        return 0.0

    main_eqs_set = set(main_eqs)
    all_base_eqs_set = set(all_base_eqs)
    
    common_eqs = main_eqs_set.intersection(all_base_eqs_set)
    
    num_common = len(common_eqs)
    num_total_main = len(main_eqs_set)
    
    return (num_common / num_total_main) * 100.0 if num_total_main > 0 else 0.0

def find_similar_phrases_fast(text_a, text_b):
    phrase_lengths = [5, 10, 15, 20]
    similar = []

    for L in phrase_lengths:
        phrases_a = split_phrases(text_a, L)
        phrases_b = split_phrases(text_b, L)

        hashes_b = set(hash_phrase(p) for p in phrases_b)

        for i, phrase in enumerate(phrases_a):
            if hash_phrase(phrase) in hashes_b:
                similar.append((i, i + L))

    return similar


def compare_with_folder(main_eqs, main_text, folder_path, level, mode="all"):
    all_similar_text_segments = []
    all_base_equations = set()

    run_text_comparison = mode in ["all", "text_only", "fast"]
    run_eqs_comparison = mode in ["all", "eqs_only"]

    for filename in os.listdir(folder_path):
        if not filename.endswith(".tex"):
            continue

        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="cp1250") as f:
            print("Porównuję z:", filename)
            eqs_b, text_b, _ = preprocessing(f.read())

        if run_text_comparison:
            if mode == "fast":
                similar = find_similar_phrases_fast(main_text, text_b)
            else:
                similar = find_similar_phrases(main_text, text_b, level)

            for seg in similar:
                all_similar_text_segments.append((seg, filename))

        if run_eqs_comparison:
            all_base_equations.update(eqs_b)

    percent_text = 0.0
    percent_eqs = 0.0

    if run_text_comparison:
        percent_text, _ = calculate_text_plagiarism(
            [s for s, _ in all_similar_text_segments],
            main_text
        )

    if run_eqs_comparison:
        percent_eqs = calculate_equation_plagiarism(main_eqs, all_base_equations)

    return percent_text, percent_eqs, all_similar_text_segments



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



def run_analysis(input_path, base_path, difficulty_level, mode="all"):
    print("Ścieżka do pliku:", input_path)
    print("Poziom trudności:", difficulty_level)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku wejściowego: {input_path}")
        return

    equations, text, clean_text = preprocessing(content)
    final_text = build_final_text(clean_text)


    percent_text, percent_eqs, segments_with_sources = compare_with_folder(
        equations, text, base_path, difficulty_level, mode=mode
    )

    compared_files = [f for f in os.listdir(base_path) if f.endswith(".tex")]

    output_pdf_path = os.path.join(
        os.path.dirname(input_path),
        "raport_plagiatu.pdf"
    )

    create_pdf_report(
        output_pdf_path,
        input_path,
        base_path,
        difficulty_level,
        mode,
        percent_text,
        percent_eqs,
        compared_files,
        final_text,
        segments_with_sources
    )

    print(f"\nPDF zapisany jako: {output_pdf_path}")
    return percent_text, percent_eqs


def main():
    #dane do testów bez argumentów
    STATIC_TEST_FILE = "bazaIO\\orthview.tex"
    STATIC_BASE_PATH = "bazaIO"
    STATIC_DIFFICULTY = "średni" # opcje: "niski", "średni", "wysoki", "bardzo_wysoki"
    STATIC_MODE = "fast"  # opcje: "all", "text_only", "eqs_only"

    #uruchomienie analizy z argumentami przekazanymi z C#
    if len(sys.argv) > 1:

        latex_file_path = sys.argv[1] # ścieżka do wybranego pliku
        difficulty = sys.argv[2] # poziom
        script_dir = os.path.dirname(os.path.abspath(__file__))
        baza_path = os.path.join(script_dir, "bazaIO[test]") # ścieżka do bazy
        
        run_analysis(latex_file_path, baza_path, difficulty)
    ## tryb testowy bez argumentów
    else:
        print("--- TRYB TESTOWY (BRAK ARGUMENTÓW) ---")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, STATIC_TEST_FILE)
        base_dir_path = os.path.join(script_dir, STATIC_BASE_PATH)

        run_analysis(file_path, base_dir_path, STATIC_DIFFICULTY, mode=STATIC_MODE)


if __name__ == "__main__":
    main()

