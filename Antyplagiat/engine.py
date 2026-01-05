import os
import sys
import hashlib
from cleaner import preprocessing
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


#podział tekstu na frazy
def split_phrases(text, phrase_len):
    words = text.split()
    phrases = []

    for i in range(len(words) - phrase_len + 1):
        phrase = " ".join(words[i : i + phrase_len])
        phrases.append(phrase)

    return phrases


# konwersja frazy na zbiór słów
def phrase_to_set(phrase):
    return set(phrase.split())


# liczenie wspólnych słów w zbiorach
def count_common_words_set(set_a, set_b):
    return len(set_a & set_b)


# funkcja hashująca frazę
def hash_phrase(phrase):
    return hashlib.sha1(phrase.encode("utf-8")).hexdigest()


# znajdowanie podobnych fraz
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


# scalanie nakładających się segmentów
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


# obliczanie procentu plagiatu w tekście
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


# obliczanie procentu plagiatu w równaniach
def calculate_equation_plagiarism(main_eqs, all_base_eqs):

    if not main_eqs:
        return 0.0

    main_eqs_set = set(main_eqs)
    all_base_eqs_set = set(all_base_eqs)
    
    common_eqs = main_eqs_set.intersection(all_base_eqs_set)
    
    num_common = len(common_eqs)
    num_total_main = len(main_eqs_set)
    
    return (num_common / num_total_main) * 100.0 if num_total_main > 0 else 0.0


# szybkie znajdowanie podobnych fraz
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


# porównanie z bazą
def compare_with_folder(main_eqs, main_text, folder_path, level, mode="all"):
    all_similar_text_segments = []
    all_base_equations = set()

    run_text_comparison = mode in ["all", "text_only", "fast"]
    run_eqs_comparison = mode in ["all", "eqs_only"]

    for filename in os.listdir(folder_path):
        if not filename.endswith(".tex"):
            continue

        file_path = os.path.join(folder_path, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"Porównywanie z plikiem: {filename}")
                eqs_b, text_b, _ = preprocessing(content)
        except Exception as e:
            print(f"BŁĄD: Nie można odczytać pliku {filename}: {e}")
            continue

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