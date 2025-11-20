import re
from pylatexenc.latex2text import LatexNodes2Text

def preprocessing(file_content):
    m = re.search(r'\\begin{document}(.*)\\end{document}', file_content, flags=re.S)
    if m:
        file_content = m.group(1)

    env_pattern = r'\\begin\{(equation|align|gather|multline|eqnarray)\}(.*?)\\end\{\1\}'
    env_eqs = [m[1] for m in re.findall(env_pattern, file_content, flags=re.S)]

    inline_eqs = re.findall(r'\$(.*?)\$', file_content, flags=re.S)
    display_eqs = re.findall(r'\\\[(.*?)\\\]', file_content, flags=re.S)

    equations = env_eqs + inline_eqs + display_eqs

    tmp = re.sub(env_pattern, '', file_content, flags=re.S)
    tmp = re.sub(r'\$(.*?)\$', '', tmp, flags=re.S)
    tmp = re.sub(r'\\\[(.*?)\\\]', '', tmp, flags=re.S)

    tmp = re.sub(r'\\[a-zA-Z]+\*?(?=\s|$|{)', '', tmp)

    text = LatexNodes2Text().latex_to_text(tmp)

    text = " ".join(text.split())

    return equations, text


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

with open("plik.tex", "r", encoding="utf-8") as f:
    content = f.read()

equations, text = preprocessing(content)

print("\n=== Tekst ===")
print(text)
    
    


