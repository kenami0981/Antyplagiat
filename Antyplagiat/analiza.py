# import re
# from pylatexenc.latex2text import LatexNodes2Text

# def preprocessing(file_content):
#     m = re.search(r'\\begin{document}(.*)\\end{document}', file_content, flags=re.S)
#     if m:
#         file_content = m.group(1)

#     env_pattern = r'\\begin\{(equation|align|gather|multline|eqnarray)\}(.*?)\\end\{\1\}'
#     env_eqs = [m[1] for m in re.findall(env_pattern, file_content, flags=re.S)]

#     inline_eqs = re.findall(r'\$(.*?)\$', file_content, flags=re.S)
#     display_eqs = re.findall(r'\\\[(.*?)\\\]', file_content, flags=re.S)

#     equations = env_eqs + inline_eqs + display_eqs

#     tmp = re.sub(env_pattern, '', file_content, flags=re.S)
#     tmp = re.sub(r'\$(.*?)\$', '', tmp, flags=re.S)
#     tmp = re.sub(r'\\\[(.*?)\\\]', '', tmp, flags=re.S)

#     tmp = re.sub(r'\\[a-zA-Z]+\*?(?=\s|$|{)', '', tmp)

#     text = LatexNodes2Text().latex_to_text(tmp)

#     text = " ".join(text.split())

#     return equations, text


# def similarity_levels(level):
#     if level == "niski":
#         return [3, 6, 8, 11]
#     elif level == "średni":
#         return [4, 8, 11, 14]
#     elif level == "wysoki":
#         return [5, 9, 13, 17]
#     elif level == "bardzo_wysoki":
#         return [5, 10, 15, 19]

# def split_phrases(text, phrase_len):
#     words = text.split()
#     phrases = []

#     for i in range(len(words) - phrase_len + 1):
#         phrase = " ".join(words[i : i + phrase_len])
#         phrases.append(phrase)

#     return phrases

# with open("plik.tex", "r", encoding="utf-8") as f:
#     content = f.read()

# equations, text = preprocessing(content)

# print("\n=== Tekst ===")
# print(text)

import re
from pylatexenc.latex2text import LatexNodes2Text


def preprocessing(file_content):
    """
    Wyodrębnia równania matematyczne do osobnej listy i konwertuje 
    pozostałą treść LaTeX na czysty tekst.
    """
    # 1. Ekstrakcja ciała dokumentu (treści między \begin{document} a \end{document})
    m = re.search(r'\\begin{document}(.*)\\end{document}', file_content, flags=re.S)
    if m:
        file_content = m.group(1)

    # Definicja wzoru dla środowisk równań (z opcjonalną gwiazdką: equation*)
    env_pattern = r'\\begin\{(equation|align|gather|multline|eqnarray)\*?\}(.*?)\\end\{\1\*?\}'
    
    # 2. Ekstrakcja równań matematycznych:
    env_eqs = [m.group(2).strip() for m in re.finditer(env_pattern, file_content, flags=re.S)]
    inline_eqs = re.findall(r'\$(.*?)\$', file_content, flags=re.S)
    display_eqs = re.findall(r'\\\[(.*?)\\\]', file_content, flags=re.S)
    equations = env_eqs + inline_eqs + display_eqs

    # 3. Usuwanie równań z treści. Zastępowanie spacją, aby nie łączyć słów:
    tmp = re.sub(env_pattern, ' ', file_content, flags=re.S)
    tmp = re.sub(r'\$(.*?)\$', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\\[(.*?)\\\]', ' ', tmp, flags=re.S)
    
    # a) Usuń komentarze (ważne, bo % może być mylone z równaniem)
    tmp = re.sub(r'%.*?\n', ' ', tmp, flags=re.S)
    
    # b) Usuń makra bez argumentów lub z argumentami opcjonalnymi
    # CEL: Usunięcie rzeczy typu \maketitle, \tableofcontents, \break, \bfseries
    tmp = re.sub(r'\\[a-zA-Z]+\*?(?=\s|\n|$|\[)', ' ', tmp, flags=re.S) 
    
    # c) Usuń makra z argumentami (np. \cite{}, \label{})
    # CEL: Usunięcie \cite{...}, \ref{...} oraz makr LaTeX-owych typu \em
    tmp = re.sub(r'\\[a-zA-Z]+\*?\{.*?\}', ' ', tmp, flags=re.S)

    # d) Usuń resztki środowisk, które mogły zostać po czyszczeniu równań/makr
    tmp = re.sub(r'\\begin\{.*?\}', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\end\{.*?\}', ' ', tmp, flags=re.S)
    
    # e) Usuń zbędne znaki (np. &,\)
    tmp = re.sub(r'[&\\]', ' ', tmp)

    # 4. Konwersja pozostałej treści LaTeX na czysty tekst za pomocą pylatexenc.
    # Ważne: ta operacja usuwa większość komend formatujących (\section, \textbf itp.)
    try:
        text = LatexNodes2Text().latex_to_text(tmp)
    except IndexError as e:
        # Zgłoś błąd wraz z treścią, aby debugowanie było możliwe
        print(f"!!! BŁĄD PARSOWANIA: {e}")
        print("--- Uszkodzona treść (tmp) ---")
        print(tmp[:1000] + "...") # Wyświetl pierwsze 1000 znaków
        raise e # Ponowne zgłoszenie błędu

    # 5. Normalizacja: usunięcie nadmiarowych spacji i konwersja na małe litery.
    text = " ".join(text.split()).lower()
    
    # 6. Normalizacja równań: usunięcie białych znaków wewnątrz równania (dla porównania)
    equations = [eq.replace(' ', '').replace('\n', '') for eq in equations if eq.strip()]

    return equations, text


def split_phrases(text, phrase_len):
    """
    Dzieli tekst na frazy (N-gramy) o określonej długości słów.
    Zwraca ZBIÓR unikalnych fraz (shingles) dla danego tekstu.
    """
    words = text.split()
    phrases = []

    for i in range(len(words) - phrase_len + 1):
        phrase = " ".join(words[i : i + phrase_len])
        phrases.append(phrase)

    return set(phrases)


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



with open("Antyplagiat\\bazaIO\\critical.tex", "r", encoding="cp1250") as f:
    content = f.read()
   
equations, text = preprocessing(content)

print("=== WYNIK WYODRĘBNIANIA ===")
print("\n## 📝 Czysty Tekst (Normalizowany)")
print(text)
    
print("\n## 🧮 Wyodrębnione Równania (Znormalizowane)")
for i, eq in enumerate(equations):
    print(f"{i+1}. {eq}")
        
# print("\n## 🧩 Test Generowania Fraz (N-gramy K=3)")
# shingles = split_phrases(text, phrase_len=3)
# print(shingles)
    
    


