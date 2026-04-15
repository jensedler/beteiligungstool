"""Initiale Leitfragen und Admin-User anlegen."""
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.question import Section, Question

app = create_app()

SECTIONS = [
    {
        "title": "Projektbeschreibung und Ziel des Gesamtvorhabens",
        "order": 1,
        "questions": [
            ("Wie lautet der Titel des Vorhabens?", "text", True, ""),
            ("Welches Amt/welche Organisationseinheit ist fuer das Vorhaben verantwortlich?", "text", True, ""),
            ("Beschreiben Sie das Vorhaben in wenigen Saetzen.", "textarea", True, "Was ist der Kern des Projekts?"),
            ("Was ist das uebergeordnete Ziel des Vorhabens?", "textarea", True, ""),
            ("Welchen raeumlichen Bezug hat das Vorhaben?", "text", False, "z.B. Stadtteil, gesamtes Stadtgebiet"),
            ("Gibt es einen politischen Beschluss oder Auftrag?", "yesno", False, ""),
            ("Wenn ja, welchen?", "textarea", False, "Beschlussnummer, Datum, Inhalt"),
            ("Welche weiteren Akteure sind beteiligt?", "textarea", False, "z.B. andere Aemter, externe Partner"),
        ],
    },
    {
        "title": "Ziel der Beteiligung/Dialogveranstaltung",
        "order": 2,
        "questions": [
            ("Was genau soll mit der Beteiligung erreicht werden?", "textarea", True, ""),
            ("Auf welcher Stufe der Beteiligung bewegt sich das Vorhaben?", "multichoice", True, "",
             "Information\nKonsultation\nMitgestaltung\nMitentscheidung"),
            ("Welche konkreten Fragestellungen sollen bearbeitet werden?", "textarea", True, ""),
            ("Welche Ergebnisse werden erwartet?", "textarea", True, ""),
            ("Wie werden die Ergebnisse weiterverarbeitet?", "textarea", True, "z.B. Einfluss auf Planung, Beschlussvorlage"),
            ("Gibt es Themen, die nicht zur Disposition stehen?", "textarea", False, "Was steht bereits fest und ist nicht verhandelbar?"),
        ],
    },
    {
        "title": "Rahmenbedingungen des Beteiligungsprozesses",
        "order": 3,
        "questions": [
            ("Welche Rahmenbedingungen muessen beachtet werden?", "textarea", True, "z.B. rechtliche Vorgaben, Fristen"),
            ("Gibt es bereits laufende oder abgeschlossene Beteiligungsverfahren zum Thema?", "yesno", False, ""),
            ("Wenn ja, welche und mit welchem Ergebnis?", "textarea", False, ""),
            ("Welche Ressourcen (Budget, Personal) stehen zur Verfuegung?", "textarea", False, ""),
            ("Gibt es Konflikte oder Risiken, die beruecksichtigt werden muessen?", "textarea", False, ""),
        ],
    },
    {
        "title": "Zielgruppen/Adressaten der Beteiligung",
        "order": 4,
        "questions": [
            ("Welche Zielgruppen sollen angesprochen werden?", "textarea", True, ""),
            ("Gibt es schwer erreichbare Gruppen, die besonders einbezogen werden sollen?", "textarea", False,
             "z.B. Jugendliche, Menschen mit Migrationshintergrund, mobilitaetseingeschraenkte Personen"),
            ("Wie gross ist die erwartete Teilnehmerzahl?", "text", False, ""),
            ("Gibt es bereits bestehende Netzwerke oder Kontakte zu den Zielgruppen?", "textarea", False, ""),
        ],
    },
    {
        "title": "Formate und Methoden",
        "order": 5,
        "questions": [
            ("Welche Beteiligungsformate kommen in Frage?", "checklist", True, "",
             "Informationsveranstaltung\nWorkshop\nOnline-Beteiligung\nBuergerwerkstatt\nRunder Tisch\nBegehung/Stadtteilspaziergang\nBefragung\nSonstiges"),
            ("Soll die Beteiligung digital, analog oder hybrid stattfinden?", "multichoice", True, "",
             "Digital\nAnalog\nHybrid"),
            ("Welche Methoden sollen eingesetzt werden?", "textarea", False, "z.B. World Cafe, Fishbowl, Planungszellen"),
            ("Gibt es Anforderungen an Barrierefreiheit?", "textarea", False, ""),
            ("Wird eine externe Moderation benoetigt?", "yesno", False, ""),
        ],
    },
    {
        "title": "Zeitliche Uebersicht/Prozessplanung",
        "order": 6,
        "questions": [
            ("In welchem Zeitraum soll die Beteiligung stattfinden?", "textarea", True, "Start- und Enddatum, Meilensteine"),
            ("Gibt es feste Termine oder Deadlines, die eingehalten werden muessen?", "textarea", False, ""),
        ],
    },
    {
        "title": "Optionale Ergaenzungen",
        "order": 7,
        "is_optional": True,
        "questions": [
            ("Gibt es weitere Aspekte, die Sie ergaenzen moechten?", "textarea", False, ""),
        ],
    },
    {
        "title": "Offene Fragen/Ergaenzende Hinweise",
        "order": 8,
        "questions": [
            ("Welche offenen Fragen gibt es noch?", "textarea", False, ""),
            ("Gibt es weitere Hinweise fuer das Team Dialog & Beteiligung?", "textarea", False, ""),
        ],
    },
    {
        "title": "Kommunikation",
        "order": 9,
        "questions": [
            ("Wie soll ueber die Beteiligung informiert werden?", "checklist", True, "",
             "Pressemitteilung\nSocial Media\nWebsite\nFlyer/Plakate\nDirektansprache\nNewsletter\nSonstiges"),
            ("Wer ist fuer die Oeffentlichkeitsarbeit zustaendig?", "text", False, ""),
            ("Soll eine eigene Projektwebsite erstellt werden?", "yesno", False, ""),
            ("Wie sollen die Ergebnisse kommuniziert werden?", "textarea", False, ""),
            ("Gibt es bereits eine Kommunikationsstrategie?", "yesno", False, ""),
            ("Wenn ja, bitte beschreiben.", "textarea", False, ""),
        ],
    },
    {
        "title": "Organisation/Ressourcen",
        "order": 10,
        "questions": [
            ("Wer ist fuer die Organisation der Beteiligung zustaendig?", "text", True, ""),
            ("Welche raeumlichen Ressourcen werden benoetigt?", "textarea", False, "z.B. Veranstaltungsraeume, technische Ausstattung"),
            ("Wird externes Fachpersonal benoetigt?", "textarea", False, "z.B. Moderation, Uebersetzung, Kinderbetreuung"),
        ],
    },
    {
        "title": "Monitoring/Evaluation",
        "order": 11,
        "questions": [
            ("Wie soll der Beteiligungsprozess evaluiert werden?", "textarea", False, ""),
            ("Welche Erfolgskriterien werden definiert?", "textarea", False, ""),
        ],
    },
    {
        "title": "Datenschutz",
        "order": 12,
        "questions": [
            ("Werden personenbezogene Daten erhoben?", "yesno", True, ""),
            ("Wenn ja, welche und zu welchem Zweck?", "textarea", False, ""),
            ("Ist eine Datenschutzfolgeabschaetzung erforderlich?", "yesno", False, ""),
        ],
    },
    {
        "title": "Kontaktdaten/Ansprechpartner*innen",
        "order": 13,
        "questions": [
            ("Wer ist Ansprechpartner*in im Fachamt?", "text", True, "Name, Funktion"),
            ("E-Mail-Adresse", "text", True, ""),
            ("Telefonnummer", "text", False, ""),
            ("Gibt es weitere Ansprechpartner*innen?", "textarea", False, ""),
        ],
    },
]


def seed():
    with app.app_context():
        db.create_all()

        # Admin-User
        if not User.query.filter_by(email="admin@bielefeld.de").first():
            admin = User(
                email="admin@bielefeld.de",
                name="Admin",
                role="admin",
                department="IT",
            )
            admin.set_password("changeme123")
            db.session.add(admin)
            print("Admin-User erstellt: admin@bielefeld.de / changeme123")

        # Sections + Questions
        if Section.query.count() == 0:
            for s_data in SECTIONS:
                section = Section(
                    title=s_data["title"],
                    order=s_data["order"],
                    description=s_data.get("description", ""),
                    is_optional=s_data.get("is_optional", False),
                )
                db.session.add(section)
                db.session.flush()

                for i, q_data in enumerate(s_data["questions"], start=1):
                    text, qtype, required, help_text = q_data[0], q_data[1], q_data[2], q_data[3]
                    options = q_data[4] if len(q_data) > 4 else ""
                    question = Question(
                        section_id=section.id,
                        text=text,
                        question_type=qtype,
                        is_required=required,
                        help_text=help_text,
                        options_json=options,
                        order=i,
                    )
                    db.session.add(question)

            print(f"{len(SECTIONS)} Sektionen mit Fragen erstellt.")
        else:
            print("Sektionen existieren bereits, uebersprungen.")

        db.session.commit()
        print("Seed abgeschlossen.")


if __name__ == "__main__":
    seed()
