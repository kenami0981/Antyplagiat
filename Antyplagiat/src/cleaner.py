import re
from pylatexenc.latex2text import LatexNodes2Text


# czyszczenie danych i podzia³
def preprocessing(file_content):
    m = re.search(r'\\begin{document}(.*)\\end{document}', file_content, flags=re.S)
    if m:
        file_content = m.group(1)

    env_pattern = r'\\begin\{(equation|align|gather|multline|eqnarray)\*?\}(.*?)\\end\{\1\*?\}'
    
    env_eqs = [m.group(2).strip() for m in re.finditer(env_pattern, file_content, flags=re.S)]
    display_dollar_eqs = re.findall(r'\$\$(.*?)\$\$', file_content, flags=re.S)
    inline_eqs = re.findall(r'\$(?!\$)(.*?)\$', file_content, flags=re.S)
    display_eqs = re.findall(r'\\\[(.*?)\\\]', file_content, flags=re.S)
    equations = env_eqs + display_dollar_eqs + inline_eqs + display_eqs


    tmp = re.sub(r'\\begin\{thebibliography\}[\s\S]*?\\end\{thebibliography\}', ' ', file_content)

    tmp = re.sub(env_pattern, ' ', tmp, flags=re.S)
    tmp = re.sub(r'\$\$[\s\S]*?\$\$', ' ', tmp)
    tmp = re.sub(r'\\\[[\s\S]*?\\\]', ' ', tmp)
    tmp = re.sub(r'\$(?!\$)[\s\S]*?\$', ' ', tmp)
    tmp = re.sub(r'\\xymatrix\{[\s\S]*?\}', ' ', tmp)
    tmp = re.sub(r'\\eqref\{.*?\}', ' ', tmp)
    tmp = re.sub(r'%.*$', ' ', tmp, flags=re.M)
    tmp = re.sub(r'\\begin\{tabular\}[\s\S]*?\\end\{tabular\}', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\begin\{.*?\}[\s\S]*?\\end\{.*?\}', ' ', tmp, flags=re.S)
    tmp = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{[\s\S]*?\}', ' ', tmp)
    tmp = re.sub(r'\\[a-zA-Z]+\*?', ' ', tmp)
    tmp = re.sub(r'[&|]', ' ', tmp)
    tmp = re.sub(r'\\\\', ' ', tmp)





    text = LatexNodes2Text().latex_to_text(tmp)
    clean_text = LatexNodes2Text().latex_to_text(tmp)

    clean_text = re.sub(r'([.,;:!?])\s*(\1\s*)+', r'\1 ', clean_text)
    clean_text = re.sub(r'\s+([.,;:!?])', r'\1', clean_text)

    
    text = " ".join(text.split()).lower()
    equations = [eq.replace(' ', '').replace('\n', '') for eq in equations if eq.strip()]
    
    return equations, text, clean_text
