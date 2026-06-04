import threading
import openai
from flask import current_app

from app.extensions import db
from app.models.konzept import Konzept
from app.models.knowledge import KnowledgeDocument
from app.models.question import Section
from app.models.prompt import SystemPrompt, SYSTEM_PROMPT_DEFAULT
from app.services.knowledge_service import build_composed_prompt


def _build_system_prompt() -> str:
    row = SystemPrompt.get()
    base = row.content if row else SYSTEM_PROMPT_DEFAULT
    if not row or not row.use_knowledge_base:
        return base
    try:
        docs = (
            KnowledgeDocument.query
            .filter_by(is_active=True)
            .order_by(KnowledgeDocument.priority, KnowledgeDocument.id)
            .all()
        )
    except Exception:
        return base
    if not docs:
        return base
    return build_composed_prompt(base, docs)


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

    user_prompt = f"""{context}

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
            {"role": "system", "content": _build_system_prompt()},
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
