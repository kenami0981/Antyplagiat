import re
from pylatexenc.latex2text import LatexNodes2Text


# czyszczenie danych i podzia³
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
