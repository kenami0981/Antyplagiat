import re
from pylatexenc.latex2text import LatexNodes2Text
import os

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
def calculate_plagiarism(segments, original_text):
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

# porównanie z bazą danych
def compare_with_folder(main_text, folder_path, level):
    all_similar = set()

    for filename in os.listdir(folder_path):
        if not filename.endswith(".tex"):
            continue

        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            _, text_b = preprocessing(f.read())

        similar = find_similar_phrases(main_text, text_b, level)
        all_similar.update(similar)

    percent = calculate_plagiarism(list(all_similar), main_text)
    return percent


with open("bazaIO/critical.tex", "r", encoding="cp1250") as f:
    content = f.read()
   
equations, text = preprocessing(content)

percent = compare_with_folder(text, "bazaIO", "średni")

print("Plagiat:", percent, "%")

