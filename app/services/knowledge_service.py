import os
from docx import Document as DocxDocument


ALLOWED_EXTENSIONS = {".txt", ".md", ".docx"}


def _read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        doc = DocxDocument(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_knowledge_base(base_dir: str) -> str:
    """Walk base_dir, read all supported files, return concatenated context string."""
    if not base_dir or not os.path.isdir(base_dir):
        return ""

    parts = []
    for root, dirs, files in os.walk(base_dir):
        dirs.sort()
        for fname in sorted(files):
            if os.path.splitext(fname)[1].lower() not in ALLOWED_EXTENSIONS:
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, base_dir)
            try:
                content = _read_file(fpath).strip()
            except Exception:
                continue
            if content:
                parts.append(f"=== Wissensbasis-Datei: {rel} ===\n{content}")

    return "\n\n".join(parts)


def list_files(base_dir: str) -> list:
    """Return sorted list of relative file paths in base_dir."""
    if not base_dir or not os.path.isdir(base_dir):
        return []
    result = []
    for root, dirs, files in os.walk(base_dir):
        dirs.sort()
        for fname in sorted(files):
            if os.path.splitext(fname)[1].lower() in ALLOWED_EXTENSIONS:
                result.append(os.path.relpath(os.path.join(root, fname), base_dir))
    return result


def build_composed_prompt(base: str, docs: list) -> str:
    """
    Compose system prompt with active KnowledgeDocument entries by priority:
      prio 1–5   → prepended BEFORE the base prompt
      prio 6–9   → inserted AFTER the base prompt (middle section)
      prio 10+   → appended at the END
    """
    high = [d for d in docs if d.priority <= 5]
    mid  = [d for d in docs if 6 <= d.priority <= 9]
    low  = [d for d in docs if d.priority >= 10]

    def _render(label: str, items: list) -> str:
        lines = [f"## {label}\n"]
        for doc in items:
            header = f"### {doc.title}"
            if doc.category:
                header += f" [{doc.category}]"
            lines.append(f"{header}\n{doc.content}")
        return "\n\n".join(lines)

    parts = []
    if high:
        parts.append(_render("Vorrangige Wissensdatenbank (Prio 1–5)", high))
        parts.append("---")
    parts.append(base)
    if mid:
        parts.append("---")
        parts.append(_render("Ergänzende Wissensdatenbank (Prio 6–9)", mid))
    if low:
        parts.append("---")
        parts.append(_render("Referenzmaterial (Prio 10+)", low))
    return "\n\n".join(parts)


def safe_path(base_dir: str, rel_path: str) -> str | None:
    """Resolve rel_path under base_dir; return None if it escapes base_dir."""
    target = os.path.realpath(os.path.join(base_dir, rel_path))
    if os.path.realpath(base_dir) == os.path.commonpath(
        [os.path.realpath(base_dir), target]
    ):
        return target
    return None
