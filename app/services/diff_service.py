import re
import difflib
from markupsafe import escape, Markup


def compute_diff_html(old_text: str, new_text: str) -> tuple:
    """Word-level diff. Returns (old_html, new_html) as Markup with inline highlights."""
    tokens_old = re.split(r'(\s+)', old_text)
    tokens_new = re.split(r'(\s+)', new_text)

    matcher = difflib.SequenceMatcher(None, tokens_old, tokens_new, autojunk=False)

    old_parts, new_parts = [], []

    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        old_chunk = escape(''.join(tokens_old[i1:i2]))
        new_chunk = escape(''.join(tokens_new[j1:j2]))

        if op == 'equal':
            old_parts.append(old_chunk)
            new_parts.append(new_chunk)
        elif op == 'replace':
            old_parts.append(Markup(f'<mark class="diff-del">{old_chunk}</mark>'))
            new_parts.append(Markup(f'<mark class="diff-ins">{new_chunk}</mark>'))
        elif op == 'delete':
            old_parts.append(Markup(f'<mark class="diff-del">{old_chunk}</mark>'))
        elif op == 'insert':
            new_parts.append(Markup(f'<mark class="diff-ins">{new_chunk}</mark>'))

    return Markup('').join(old_parts), Markup('').join(new_parts)
