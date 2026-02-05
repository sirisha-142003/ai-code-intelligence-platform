import os
import re
import lizard
from collections import Counter
from keywords import py_kw, js_kw

with open("data/words_alpha.txt", "r") as f:
    english_words = set(line.strip().lower() for line in f)

def split_identifier(identifier):
    parts = identifier.split("_")
    final_parts = []
    for part in parts:
        split_camel = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', part)
        final_parts.extend([p.lower() for p in split_camel if p])
    return final_parts

def identifier_quality(identifier, max_length=30):
    tokens = split_identifier(identifier)
    if not tokens:
        return 0.0
    valid_frac = sum(1 for t in tokens if t in english_words) / len(tokens)
    length_penalty = 1.0 if len(identifier) <= max_length else max_length / len(identifier)
    return valid_frac * length_penalty

def extract(filepath):
    analysis = lizard.analyze_file(filepath)
    functions = analysis.function_list
    avg_complexity = sum(f.cyclomatic_complexity for f in functions)/len(functions) if functions else 0

    identifiers = [f.name for f in functions]

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        lines = []

    _, ext = os.path.splitext(filepath)
    if ext == '.py':
        lang = 'Python'
        keywords = py_kw
    elif ext == '.js':
        lang = 'JavaScript'
        keywords = js_kw
    else:
        lang = 'Unknown'
        keywords = set()

    code_lines = 0
    comment_lines = 0
    blank_lines = 0
    max_line_length = 0
    total_line_length = 0
    indent_levels = []
    nesting_depth = 0
    max_nesting = 0
    num_imports = 0
    num_loops = 0
    num_conditionals = 0
    num_exceptions = 0
    has_docstring = 0
    total_tokens = 0
    total_token_lines = 0
    keyword_count = 0

    docstring_pattern = re.compile(r'^\s*[ru]?"""|\'\'\'')
    in_docstring = False

    for line in lines:
        stripped = line.strip()
        line_len = len(line.rstrip("\n"))
        max_line_length = max(max_line_length, line_len)
        total_line_length += line_len

        if not stripped:
            blank_lines += 1
            continue
        if lang == 'Python' and stripped.startswith('#'):
            comment_lines += 1
            continue
        if lang == 'JavaScript' and stripped.startswith('//'):
            comment_lines += 1
            continue

        if lang == 'Python':
            if docstring_pattern.match(stripped):
                has_docstring = 1
                in_docstring = not in_docstring
                continue
            if in_docstring:
                comment_lines += 1
                continue

        code_lines += 1

        leading_spaces = len(line) - len(line.lstrip(' '))
        leading_tabs = len(line) - len(line.lstrip('\t'))
        indent_levels.append((leading_spaces, leading_tabs))

        open_braces = line.count('{') if lang == 'JavaScript' else 0
        close_braces = line.count('}') if lang == 'JavaScript' else 0
        nesting_depth += open_braces - close_braces
        max_nesting = max(max_nesting, nesting_depth)

        if lang == 'Python' and (stripped.startswith('import') or stripped.startswith('from')):
            num_imports += 1
        if lang == 'JavaScript' and (stripped.startswith('import') or 'require' in stripped):
            num_imports += 1

        if re.match(r'^\s*(for|while)\b', stripped):
            num_loops += 1

        if re.match(r'^\s*(if|elif|else|else if)\b', stripped):
            num_conditionals += 1

        if re.match(r'^\s*(try|except|catch|finally)\b', stripped):
            num_exceptions += 1

        tokens = re.findall(r'\b\w+\b', stripped)
        total_tokens += len(tokens)
        total_token_lines += 1

        keyword_count += sum(1 for t in tokens if t in keywords)

    space_levels = [s for s, t in indent_levels if s > 0]
    tab_levels = [t for s, t in indent_levels if t > 0]
    indentation_consistency = 0
    if space_levels:
        indentation_consistency = 1 / (1 + (max(space_levels) - min(space_levels)))
    elif tab_levels:
        indentation_consistency = 1 / (1 + (max(tab_levels) - min(tab_levels)))

    avg_identifier_quality = sum(identifier_quality(id_) for id_ in identifiers) / (len(identifiers) or 1)

    metrics = {
        "filename": os.path.basename(filepath),
        "language": lang,
        "lines_of_code": code_lines,
        "num_functions": len(functions),
        "num_comments": comment_lines,
        "comment_ratio": comment_lines / (code_lines + comment_lines + 1),
        "avg_line_length": total_line_length / (len(lines) or 1),
        "max_line_length": max_line_length,
        "indentation_consistency": indentation_consistency,
        "nesting_depth": max_nesting,
        "cyclomatic_complexity": avg_complexity,
        "num_imports": num_imports,
        "num_loops": num_loops,
        "num_conditionals": num_conditionals,
        "num_exceptions": num_exceptions,
        "has_docstring": has_docstring,
        "avg_tokens_per_line": total_tokens / (total_token_lines or 1),
        "keyword_density": keyword_count / (code_lines or 1),
        "blank_lines_ratio": blank_lines / (len(lines) or 1),
        "avg_identifier_quality": avg_identifier_quality
    }

    return metrics

if __name__ == "__main__":
    import sys
    filepath = sys.argv[1]
    result = extract(filepath)
    for k, v in result.items():
        print(f"{k}: {v}")
