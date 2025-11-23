import re
from pylatexenc.latex2text import LatexNodes2Text
import os
import sys

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

    text = LatexNodes2Text().latex_to_text(tmp)

    text = " ".join(text.split()).lower()
    equations = [eq.replace(' ', '').replace('\n', '') for eq in equations if eq.strip()]

    return equations, text

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

# funkcja do podziału na frazy
def split_phrases(text, phrase_len):
    words = text.split()
    phrases = []

    for i in range(len(words) - phrase_len + 1):
        phrase = " ".join(words[i : i + phrase_len])
        phrases.append(phrase)

    return phrases

# set dla frazy
def phrase_to_set(phrase):
    return set(phrase.split())

# porównywanie podobieństwa słów w frazie
def count_common_words_set(set_a, set_b):
    return len(set_a & set_b)

# znajdowanie podobnych fraz (szybsza wersja minimalna)
def find_similar_phrases(text_a, text_b, level):
    thresholds = similarity_levels(level)
    phrase_lengths = [5, 10, 15, 20]

    similar = []

    for idx, L in enumerate(phrase_lengths):
        t = thresholds[idx]

        phrases_a = split_phrases(text_a, L)
        phrases_b = split_phrases(text_b, L)

        sets_a = [phrase_to_set(p) for p in phrases_a]
        sets_b = [phrase_to_set(p) for p in phrases_b]

        for i, set_pa in enumerate(sets_a):
            for j, set_pb in enumerate(sets_b):
                if count_common_words_set(set_pa, set_pb) >= t:
                    start = i
                    end = i + L
                    similar.append((start, end))
                    break

    return similar

# funkcja pomocnicza, żeby frazy się nie powtarzały
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

# obliczanie %
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


# porównanie z bazą danych
def compare_with_folder(main_eqs, main_text, folder_path, level, mode="all"):
    all_similar_text_segments = set()
    all_base_equations = set()

    run_text_comparison = mode in ["all", "text_only"]
    run_eqs_comparison = mode in ["all", "eqs_only"]

    for filename in os.listdir(folder_path):
        if not filename.endswith(".tex"):
            continue

        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="cp1250") as f: #przy utf-8 wysypuje się na polskich znakach z pliku test.tex
            print("Porównuję z:", filename)
            eqs_b, text_b = preprocessing(f.read())
        
        if run_text_comparison:
            similar = find_similar_phrases(main_text, text_b, level)
            all_similar_text_segments.update(similar)

        if run_eqs_comparison:
            all_base_equations.update(eqs_b)

    percent_text = 0.0
    percent_eqs = 0.0

    if run_text_comparison:
        percent_text, _ = calculate_text_plagiarism(list(all_similar_text_segments), main_text)
    
    if run_eqs_comparison:
        percent_eqs = calculate_equation_plagiarism(main_eqs, all_base_equations)

    return percent_text, percent_eqs


# główna funkcja uruchamiająca analizę
def run_analysis(input_path, base_path, difficulty_level, mode="all"):
    print("Otrzymałem ścieżkę:", input_path)
    print("Poziom trudności:", difficulty_level)
    print("Ścieżka do bazy:", base_path)
    
    try:
        with open(input_path, "r", encoding="cp1250") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku wejściowego: {input_path}")
        return

    equations, text = preprocessing(content)

    percent_text, percent_eqs = compare_with_folder(equations, text, base_path, difficulty_level, mode=mode)

    print("\n--- WYNIKI ANALIZY PLAGIATU ---")

    if mode in ['all', 'text_only']:
        print(f"Plagiat Tekstu: {percent_text:.2f}%")
    
    if mode in ['all', 'eqs_only']:
        print(f"Plagiat Równań: {percent_eqs:.2f}%")
    
    return percent_text, percent_eqs

def main():
    #dane do testów bez argumentów
    STATIC_TEST_FILE = "bazaIO[test]\\test.tex"
    STATIC_BASE_PATH = "bazaIO[test]"
    STATIC_DIFFICULTY = "średni" # opcje: "niski", "średni", "wysoki", "bardzo_wysoki"
    STATIC_MODE = "eqs_only"  # opcje: "all", "text_only", "eqs_only"

    #uruchomienie analizy z argumentami przekazanymi z C#
    if len(sys.argv) > 1:

        latex_file_path = sys.argv[1] # ścieżka do wybranego pliku
        difficulty = sys.argv[2] # poziom
        script_dir = os.path.dirname(os.path.abspath(__file__))
        baza_path = os.path.join(script_dir, "bazaIO") # ścieżka do bazy
        
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