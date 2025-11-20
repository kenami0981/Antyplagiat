from pylatexenc.latexwalker import LatexWalker, LatexEnvironmentNode, LatexMathNode

def preprocessing(file_content):
    walker = LatexWalker(file_content)
    nodes, _, _ = walker.get_latex_nodes()

    text_parts = []
    equations = []

    def node_end(node):
        if hasattr(node, "pos_end") and node.pos_end is not None:
            return node.pos_end
        return node.pos + node.len

    def visit_node(node):
        if isinstance(node, LatexMathNode):
            equations.append(file_content[node.pos:node_end(node)])
            return
        
        if isinstance(node, LatexEnvironmentNode):
            if node.envname in ["equation", "align", "gather", "multline", "eqnarray"]:
                equations.append(file_content[node.pos:node_end(node)])
                return
            
        if hasattr(node, "chars") and node.chars:
            text_parts.append(node.chars)

        if hasattr(node, "nodelist") and node.nodelist:
            for child in node.nodelist:
                visit_node(child)

    for n in nodes:
        visit_node(n)

    text = " ".join("".join(text_parts).split())

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


    
    


