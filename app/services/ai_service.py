import threading
import openai
from flask import current_app

from app.extensions import db
from app.models.konzept import Konzept
from app.models.question import Section
from app.models.prompt import SystemPrompt
from app.services.knowledge_service import load_knowledge_base


def _build_system_prompt() -> str:
    try:
        docs = (
            KnowledgeDocument.query
            .filter_by(is_active=True)
            .order_by(KnowledgeDocument.priority, KnowledgeDocument.id)
            .all()
        )
    except Exception:
        return SYSTEM_PROMPT
    if not docs:
        return SYSTEM_PROMPT

    parts = [SYSTEM_PROMPT, "\n\n---\n\n## Referenzmaterial und Wissensdatenbank\n"]
    parts.append(
        "Die folgenden Dokumente enthalten verbindliche Leitlinien, Methoden und Rahmenbedingungen "
        "der Stadt Bielefeld. Berücksichtige diese Inhalte bei der Erstellung des Konzepts.\n"
    )
    for doc in docs:
        header = f"### {doc.title}"
        if doc.category:
            header += f" [{doc.category}]"
        parts.append(f"\n{header}\n{doc.content}\n")
    return "\n".join(parts)


def generate_konzept_text(konzept: Konzept) -> str:
    api_key = current_app.config.get("OPENAI_API_KEY")
    base_url = current_app.config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = current_app.config.get("OPENAI_MODEL", "gpt-4o")

    if not api_key:
        return ""

    sections = Section.query.filter_by(is_active=True).order_by(Section.order).all()
    answers_map = {a.question_id: a.value for a in konzept.answers}

    # Sammle alle Antworten als Kontext
    context_parts = [f"Projekttitel: {konzept.title}\n"]
    context_parts.append("=" * 50)
    context_parts.append("\nFolgende Informationen wurden vom Fachamt bereitgestellt:\n")

    for section in sections:
        section_answers = []
        for q in section.questions:
            if not q.is_active:
                continue
            val = answers_map.get(q.id, "")
            if val and val.strip():
                section_answers.append(f"- {q.text}\n  Antwort: {val}")
        if section_answers:
            context_parts.append(f"\n### {section.title}")
            context_parts.extend(section_answers)

    context = "\n".join(context_parts)

    knowledge = load_knowledge_base(current_app.config.get("KNOWLEDGE_BASE_DIR", ""))
    knowledge_block = (
        f"\n\nZusaetzliche Wissensbasis der Stadt Bielefeld "
        f"(interne Dokumente, Leitfaeden, Standards):\n\n{knowledge}\n\n{'=' * 50}"
        if knowledge else ""
    )

    user_prompt = f"""{context}{knowledge_block}

---

Bitte erstelle nun auf Basis dieser Informationen ein vollstaendiges, professionelles Beteiligungskonzept.

Schreibe ein eigenstaendiges Dokument - NICHT einfach die Antworten umformatieren!
Bringe die Informationen in einen sinnvollen Zusammenhang, ergaenze wo noetig, und schreibe fliesende Texte.
Das Konzept soll als Arbeitsgrundlage fuer das Team Dialog & Beteiligung der Stadt Bielefeld dienen.
"""

    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SystemPrompt.get()},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=4000,
    )
    return response.choices[0].message.content


def _generate_in_background(app, konzept_id: int) -> None:
    with app.app_context():
        konzept = db.session.get(Konzept, konzept_id)
        if not konzept:
            return
        try:
            text = generate_konzept_text(konzept)
            if text:
                konzept.generated_text = text
                konzept.edited_text = text
        except Exception:
            pass
        finally:
            konzept.is_generating = False
            db.session.commit()


def start_generation(app, konzept_id: int) -> None:
    t = threading.Thread(target=_generate_in_background, args=(app, konzept_id), daemon=True)
    t.start()
