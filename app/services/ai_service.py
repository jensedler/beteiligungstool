import threading
import openai
from flask import current_app

from app.extensions import db
from app.models.konzept import Konzept
from app.models.question import Section


SYSTEM_PROMPT = """Du bist ein erfahrener Experte fuer Buergerbeteiligung und Dialogprozesse der Stadt Bielefeld.

Deine Aufgabe ist es, auf Basis der gesammelten Informationen ein professionelles, eigenstaendiges Beteiligungskonzept zu verfassen.

WICHTIG: Du sollst KEIN Frage-Antwort-Dokument erstellen! Schreibe stattdessen ein fliessendes, professionelles Konzeptdokument, das die Informationen sinnvoll zusammenfuehrt und ergaenzt.

Das Beteiligungskonzept soll folgende Struktur haben:

1. **Zusammenfassung** (Executive Summary)
   - Kurze Uebersicht ueber das Vorhaben und die geplante Beteiligung (3-5 Saetze)

2. **Projektbeschreibung**
   - Was ist das Vorhaben?
   - Welche Ziele werden verfolgt?
   - Welchen raeumlichen/thematischen Bezug gibt es?

3. **Ziele der Beteiligung**
   - Was soll mit der Beteiligung erreicht werden?
   - Welche Beteiligungsstufe wird angestrebt?
   - Welche konkreten Fragestellungen werden bearbeitet?
   - Wie werden Ergebnisse weiterverarbeitet?

4. **Zielgruppen**
   - Wer soll beteiligt werden?
   - Wie werden verschiedene Gruppen erreicht?
   - Besondere Beruecksichtigung schwer erreichbarer Gruppen

5. **Formate und Methoden**
   - Welche Beteiligungsformate werden eingesetzt?
   - Begruendung der Methodenwahl
   - Hinweise zur praktischen Umsetzung

6. **Zeitplan und Prozessablauf**
   - Uebersicht ueber die Phasen
   - Wichtige Meilensteine und Termine

7. **Kommunikation**
   - Wie wird informiert und eingeladen?
   - Wie werden Ergebnisse kommuniziert?

8. **Organisation und Ressourcen**
   - Wer ist verantwortlich?
   - Welche Ressourcen werden benoetigt?

9. **Evaluation**
   - Wie wird der Erfolg gemessen?

10. **Datenschutz**
    - Relevante Hinweise zum Umgang mit Daten

11. **Kontakt**
    - Ansprechpartner*innen

Schreibe in einem professionellen, aber verstaendlichen Stil. Formuliere vollstaendige Saetze und Absaetze.
Wo Informationen fehlen, weise darauf hin oder mache sinnvolle Vorschlaege basierend auf Best Practices der Buergerbeteiligung.
Formatiere das Dokument in Markdown.
"""


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
            {"role": "system", "content": SYSTEM_PROMPT},
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
