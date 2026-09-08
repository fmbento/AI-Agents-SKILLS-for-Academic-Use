"""
V2: Apply the PLATINUM capitalization rule to all overlay titles and subtitles.
Uses line-by-line parsing of overlays tuple structure.
"""
import re, os, sys, subprocess

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE, '_build_all.py')

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ── Key terms vocabulary ──
ACRONYMS = {
    'CRAAP', 'IMRD', 'DOAJ', 'APA', 'IEEE', 'APC', 'DOI', 'CSV', 'Excel',
    'ISCTE', 'PDF', 'UA', 'ERIC', 'AND', 'OR', 'NOT', 'MeSH', 'IA', 'RCAAP',
    'b-on', 'WoS', 'SEMPRE', 'TODAS', 'AI', 'DOIs',
}
KEY_TERMS = {
    'Google Scholar', 'Web of Science', 'Scopus', 'PubMed', 'NotebookLM',
    'Elicit', 'Scispace', 'Consensus', 'Research Rabbit',
    'ChatGPT', 'Claude', 'Gemini', 'DeepSeek', 'Mistral', 'Grok',
    'Peer Review', 'Peer review', 'Literature Review',
    'Ciência Aberta', 'Acesso Aberto', 'Literatura Cinzenta',
    'Literatura cinzenta', 'Grey Literature',
    'Revisão por Pares', 'Revisão por pares', 'Método Científico',
    'Método CRAAP', 'Método IMRD', 'Método CRAAP + Revistas Predatórias',
    'Currency', 'Relevance', 'Authority', 'Accuracy', 'Purpose',
    'Accepted Manuscript', 'Article in Press',
    'Predatory Journals', 'Think. Check. Submit.',
    'Emerald Insight', 'Acta Biomaterialia',
    'Microsoft Copilot', 'Copilot',
    'Pré-print', 'Pós-print', 'Versão Final',
    'Character AI', 'Reddit',
    'Operadores Booleanos', 'Booleanos',
    'Ciclo de Webinars', 'Bibliotecas UA',
    'Estrutura IMRD',
    'Estratégia de Pesquisa', 'Estratégia de pesquisa',
    'Série Completa',
    'Semantic Scholar', 'OpenAlex',
    'Medical Subject Headings',
    'Subject Headings',
    'Education Resources Information Center',
    'Information Center',
    'Mendeley', 'Zotero',
    'Base de Dados', 'Base de dados',
    # IMRD sections (standalone + compounds)
    'Introduction', 'Methods', 'Results', 'Discussion',
    'Introduction, Methods, Results, Discussion',
    # Portuguese equivalents of CRAAP criteria
    'Atualidade', 'Relevância', 'Autoridade', 'Precisão', 'Propósito',
}

key_lower = {k.lower(): k for k in KEY_TERMS}


def platinum_rule(text):
    """Apply platinum rule: first word of phrase capital, key terms capital, rest lowercase."""
    if not text or not text.strip():
        return text

    # Handle period-split sentences (capitalize each sentence's first word)
    if '. ' in text:
        # Split, but only on sentence-ending periods, not abbreviations
        parts = []
        current = ""
        for segment in text.split('. '):
            if current:
                current += '. ' + segment
            else:
                current = segment
            # If this looks like a complete sentence (not abbreviation), finalize
            if len(segment.split()) >= 3 and segment[-1] not in '()[]{}':
                parts.append(current)
                current = ""
        if current:
            parts.append(current)
        if len(parts) > 1:
            # Process each sentence independently (first word of each gets capital)
            fixed = []
            for part in parts:
                fixed.append(platinum_segment(part, is_first=True))
            return '. '.join(fixed)

    # Handle colon-split phrases
    if ': ' in text:
        parts = text.split(': ')
        fixed = []
        for i, part in enumerate(parts):
            fixed.append(platinum_segment(part, is_first=(i == 0)))
        return ': '.join(fixed)

    # Handle em-dash split
    if ' — ' in text:
        parts = text.split(' — ')
        fixed = []
        for i, part in enumerate(parts):
            fixed.append(platinum_segment(part, is_first=(i == 0)))
        return ' — '.join(fixed)

    # Handle " vs " (e.g., "Pré-print vs Pós-print")
    if ' vs ' in text:
        parts = text.split(' vs ')
        fixed = []
        for i, part in enumerate(parts):
            fixed.append(platinum_segment(part, is_first=(i == 0)))
        return ' vs '.join(fixed)

    return platinum_segment(text, is_first=True)


def split_punct(word):
    """Split a word into (prefix_punctuation, core_word, suffix_punctuation)."""
    prefix = ''
    suffix = ''
    core = word
    for i, ch in enumerate(word):
        if ch.isalnum():  # Python 3 isalnum() covers all Unicode letters incl. accented
            prefix = word[:i]
            core = word[i:]
            break
    else:
        return (word, '', '')  # entirely punctuation/symbols
    for i in range(len(core) - 1, -1, -1):
        if core[i].isalnum():
            suffix = core[i+1:]
            core = core[:i+1]
            break
    return (prefix, core, suffix)


def wrap_punct(prefix, replacement, suffix):
    """Re-wrap a replacement word with original punctuation."""
    return prefix + replacement + suffix


def platinum_segment(seg, is_first):
    """Apply rule to one segment (no colons). Preserves punctuation on matched terms."""
    if not seg.strip():
        return seg

    words = seg.split()
    if not words:
        return seg

    result = []
    i = 0
    while i < len(words):
        word = words[i]
        matched = False

        # Try to match multi-word key terms (look ahead up to 4 words)
        for n in range(min(4, len(words) - i), 0, -1):
            # Build clean phrase for matching (strip punctuation)
            clean_cores = []
            for w in words[i:i+n]:
                _, core, _ = split_punct(w)
                clean_cores.append(core)
            clean_phrase = ' '.join(clean_cores)

            if clean_phrase.lower() in key_lower:
                replacement = key_lower[clean_phrase.lower()]
                repl_words = replacement.split()
                for j, rw in enumerate(repl_words):
                    if i + j < len(words):
                        prefix, _, suffix = split_punct(words[i + j])
                        result.append(wrap_punct(prefix, rw, suffix))
                    else:
                        result.append(rw)
                i += n
                matched = True
                break

        if matched:
            continue

        # Single word handling
        prefix, core, suffix = split_punct(word)

        if core.upper() in ACRONYMS or core in ACRONYMS:
            result.append(word)  # keep as-is with original punctuation
        elif core.lower() in key_lower:
            repl = key_lower[core.lower()]
            result.append(wrap_punct(prefix, repl, suffix))
        elif i == 0 and is_first:
            # First word of first segment: capitalize first letter of core
            if len(core) > 1:
                capped = core[0].upper() + core[1:]
            else:
                capped = core.upper()
            result.append(wrap_punct(prefix, capped, suffix))
        elif prefix and not core:
            # Pure punctuation/symbol — keep as-is
            result.append(word)
        else:
            # Lowercase the core, preserving punctuation
            result.append(wrap_punct(prefix, core.lower(), suffix))
        i += 1

    return ' '.join(result)


# ── Find and fix overlay tuples ──
# Modern OVERLAYS format (anchor-based _build_all.py):
#   ("f1", "concept", "CONCEITO", "TITLE", "BODY", ["terms"], True|False),
# all on ONE line. Title is the 4th element, body the 5th.
OVERLAY_RE = re.compile(
    r'^(\s*)\("(f\d+)",\s*"(?:concept|structure|tool|tip|important|example)",\s*'
    r'"[A-Z]+",\s*"([^"]*)",\s*"([^"]*)",\s*\[[^\]]*\],\s*(True|False)\)'
)

fixed_count = 0
for idx, line in enumerate(lines):
    m = OVERLAY_RE.match(line)
    if not m:
        continue
    indent, oid, old_title, old_body, fullscreen = m.groups()

    new_title = platinum_rule(old_title)
    new_body = platinum_rule(old_body)

    if old_title != new_title or old_body != new_body:
        # Rebuild the tuple line preserving indentation and fullscreen flag
        kind = re.search(r'"(concept|structure|tool|tip|important|example)"', line).group(1)
        tag = re.search(r'"[A-Z]+"', line).group(0)
        terms_m = re.search(r'\[[^\]]*\]', line)
        terms = terms_m.group(0) if terms_m else '[]'
        new_line = (f'{indent}("{oid}", "{kind}", {tag}, '
                    f'"{new_title}", "{new_body}", {terms}, {fullscreen}),\n')
        lines[idx] = new_line
        fixed_count += 1
        print(f'  {old_title[:55]}...')
        print(f'  -> {new_title[:55]}...')
        if new_body != old_body:
            print(f'     body: {old_body[:60]} -> {new_body[:60]}')
        print()

# Write back
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'\nFixed {fixed_count} overlay titles/subtitles.')
print('Regenerating index.html...')

result = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=BASE)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr[:500])
