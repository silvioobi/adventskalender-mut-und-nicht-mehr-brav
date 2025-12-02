import datetime as dt
from pathlib import Path
import html

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# Grundkonfiguration der App
# ---------------------------------------------------------
st.set_page_config(
    page_title="Adventskalender Pegasus Mindset",
    page_icon="🎄",
    layout="wide",
)

# WICHTIG: Light Mode erzwingen für Streamlit
BASE_CSS = """
<style>
/* Streamlit Dark Mode überschreiben */
:root {
    color-scheme: light;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f8f4f0 0%, #ffffff 50%, #fdf8f4 100%) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.main {
    background: linear-gradient(135deg, #f8f4f0 0%, #ffffff 50%, #fdf8f4 100%) !important;
}

body {
    font-family: "Helvetica Neue", Arial, sans-serif;
    color: #2c2c2c !important;
    background: #ffffff !important;
}

h1, h2, h3 {
    font-family: "Playfair Display", "Georgia", serif;
    letter-spacing: 0.03em;
    color: #1a1a1a !important;
}

/* Alle Text-Elemente im Light Mode */
p, span, div {
    color: #2c2c2c;
}

/* Streamlit Container */
.stApp {
    background: linear-gradient(135deg, #f8f4f0 0%, #ffffff 50%, #fdf8f4 100%) !important;
}
</style>
"""
st.markdown(BASE_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# Konfiguration: Pfad zur Excel-Datei
# ---------------------------------------------------------
EXCEL_PATH = Path("advent_content.xlsx")


# ---------------------------------------------------------
# Inhalte laden
# ---------------------------------------------------------
@st.cache_data
def load_advent_content(path: Path) -> pd.DataFrame:
    if not path.exists():
        empty_df = pd.DataFrame(
            columns=["day", "title", "text", "person", "image_url"]
        )
        return empty_df.set_index("day")

    df = pd.read_excel(path)
    df.columns = [str(c).strip().lower() for c in df.columns]

    required_cols = {"day", "text"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"Die Excel-Datei benötigt mindestens die Spalten {required_cols}, "
            f"folgende fehlen: {missing}"
        )

    df["day"] = df["day"].astype(int)
    df = df.set_index("day")

    # Optionale Spalten sicherstellen
    for col in ["title", "person", "image_url"]:
        if col not in df.columns:
            df[col] = None

    return df


# ---------------------------------------------------------
# Logik: bis zu welchem Tag freigeschaltet?
# ---------------------------------------------------------
def get_max_open_day() -> int:
    today = dt.date.today()
    if today.month == 12:
        return min(today.day, 24)
    else:
        # Außerhalb Dezember: alle Türchen frei (für Test / Vorschau)
        return 24


today = dt.date.today()
max_open_day = get_max_open_day()

# ---------------------------------------------------------
# Header & Hinweis - optimiert
# ---------------------------------------------------------
st.markdown(
    """
    <div style="margin-bottom: 2rem; text-align: center;">
        <div style="font-size:0.9rem; letter-spacing:0.2em; text-transform:uppercase; color:#c69063; font-weight:600; margin-bottom: 0.5rem;">
            ✨ "Nicht mehr brav sein" - Advent ✨
        </div>
        <h1 style="margin: 0.4rem 0 0.8rem 0; font-size: 2.5rem; color:#2c2c2c;">
            🎄 Adventskalender Mutiges, Neues und Highlights 🎄
        </h1>
        <p style="max-width: 680px; margin: 0 auto; color:#3a3a3a; font-size: 1.05rem; line-height: 1.6;">
            Hinter jedem Türchen wartet etwas Neues, etwas Mutiges, ein Schritt weg vom brav sein oder ein Highlight.
            <br><strong>Klicke auf ein Bild</strong>, um die Botschaft dieses Tages zu entdecken.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Daten laden
# ---------------------------------------------------------
try:
    df = load_advent_content(EXCEL_PATH)
except Exception as e:
    st.error(
        "Fehler beim Laden der Advents-Inhalte: "
        f"{e}\n\nBitte prüfe die Datei 'advent_content.xlsx'."
    )
    st.stop()

# ---------------------------------------------------------
# Optimiertes CSS für den Kalender
# ---------------------------------------------------------
CARDS_CSS = """
<style>
* {
    box-sizing: border-box;
}

.calendar-grid {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 1.2rem;
    padding: 0.5rem;
}

@media (max-width: 1100px) {
    .calendar-grid {
        grid-template-columns: repeat(4, minmax(0, 1fr));
    }
}

@media (max-width: 800px) {
    .calendar-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}

@media (max-width: 600px) {
    .calendar-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }
}

/* Wrapper je Türchen */
.door-wrapper {
    position: relative;
    cursor: pointer;
    transition: transform 0.2s ease;
}

.door-wrapper:not(.locked):hover {
    transform: translateY(-4px);
}

.door-wrapper.locked {
    cursor: not-allowed;
}

/* Flip-Card Grundstruktur */
.flip-card {
    background: transparent;
    perspective: 1000px;
}

.flip-card-inner {
    position: relative;
    width: 100%;
    height: 240px;
    text-align: center;
    transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(139, 90, 60, 0.15);
}

/* Der eigentliche Flip */
.flip-card-inner.is-flipped {
    transform: rotateY(180deg);
}

/* Vorder- & Rückseite */
.flip-card-front,
.flip-card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    border-radius: 16px;
    overflow: hidden;
}

/* Vorderseite – Bild mit weihnachtlichem Design */
.flip-card-front {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(135deg, #ffffff 0%, #fefdfb 100%);
    border: 2px solid #d4a574;
}

.front-header {
    padding: 0.8rem 1rem 0.4rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #8b5a3c;
    font-weight: 600;
    text-align: center;
    background: linear-gradient(to bottom, rgba(212, 165, 116, 0.1), transparent);
}

.front-header span {
    display: block;
}

.front-header .day-number {
    font-size: 1.3rem;
    font-weight: 700;
    color: #c69063;
    margin-bottom: 0.2rem;
}

.image-box {
    flex: 1;
    margin: 0 1rem 1rem 1rem;
    border-radius: 12px;
    overflow: hidden;
    background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    background-size: cover;
    background-position: center;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Rückseite – Text mit optimiertem Kontrast */
.flip-card-back {
    background: linear-gradient(135deg, #ffffff 0%, #fdfaf7 100%);
    border: 2px solid #d4a574;
    transform: rotateY(180deg);
    padding: 1.2rem 1.3rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.back-heading {
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #8b5a3c;
    font-weight: 600;
    margin-bottom: 0.5rem;
    text-align: center;
}

.back-title {
    font-family: "Playfair Display", "Georgia", serif;
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
    color: #2c2c2c;
    text-align: center;
    line-height: 1.3;
}

.back-text {
    font-size: 0.9rem;
    line-height: 1.6;
    text-align: left;
    color: #1a1a1a;
    white-space: pre-wrap;
    overflow-y: auto;
    max-height: 130px;
}

.back-person {
    margin-top: 0.8rem;
    font-style: italic;
    font-size: 0.85rem;
    color: #8b5a3c;
    text-align: right;
    font-weight: 500;
}

/* Lock-Overlay für gesperrte Türchen - weihnachtlich */
.lock-overlay {
    position: absolute;
    inset: 0;
    border-radius: 16px;
    background: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.97),
        rgba(253, 248, 244, 0.97)
    );
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    color: #8b5a3c;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    border: 2px solid #e8d4c0;
    z-index: 10;
}

.lock-overlay::before {
    content: "🔒";
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

/* Gesperrte Karten: dezent zurückgenommen */
.door-wrapper.locked .flip-card-inner {
    opacity: 0.6;
    box-shadow: 0 2px 6px rgba(139, 90, 60, 0.1);
}

/* Hover-Effekt nur für nicht-gesperrte */
.door-wrapper:not(.locked) .flip-card-inner {
    transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1), 
                box-shadow 0.3s ease;
}

.door-wrapper:not(.locked):hover .flip-card-inner:not(.is-flipped) {
    box-shadow: 0 8px 20px rgba(198, 144, 99, 0.25);
}
</style>
"""

# ---------------------------------------------------------
# HTML für die 24 Flip-Cards erzeugen
# ---------------------------------------------------------
cards_html_parts = ['<div class="calendar-grid">']

for day in range(1, 25):
    if day in df.index:
        row = df.loc[day]
        title = (row.get("title") or "").strip() if pd.notna(row.get("title")) else ""
        text = (row.get("text") or "").strip() if pd.notna(row.get("text")) else ""
        person = (row.get("person") or "").strip() if pd.notna(row.get("person")) else ""
        image_url = (row.get("image_url") or "").strip() if pd.notna(row.get("image_url")) else ""
    else:
        title, text, person, image_url = "", "", "", ""

    if not title:
        title = f"Impuls für Tag {day}"

    # HTML-escaping
    title_esc = html.escape(title)
    text_esc = html.escape(text).replace("\n", "&#10;")
    person_esc = html.escape(person)
    image_style = ""
    if image_url:
        image_style = f"background-image: url('{html.escape(image_url)}');"

    locked_class = "locked" if day > max_open_day else ""

    card_html = f"""
    <div class="door-wrapper {locked_class}" data-day="{day}">
        <div class="flip-card">
            <div class="flip-card-inner">
                <div class="flip-card-front">
                    <div class="front-header">
                        <span class="day-number">{day}</span>
                        <span>Dezember</span>
                    </div>
                    <div class="image-box" style="{image_style}"></div>
                </div>
                <div class="flip-card-back">
                    <div>
                        <div class="back-heading">✨ Tag {day} ✨</div>
                        <div class="back-title">{title_esc}</div>
                        <div class="back-text">{text_esc}</div>
                    </div>
                    <div>
                        {"<div class='back-person'>– " + person_esc + "</div>" if person_esc else ""}
                    </div>
                </div>
            </div>
            {"<div class='lock-overlay'><span>Noch nicht<br>freigeschaltet</span></div>" if day > max_open_day else ""}
        </div>
    </div>
    """
    cards_html_parts.append(card_html)

cards_html_parts.append("</div>")

# ---------------------------------------------------------
# JavaScript: Flip + localStorage - optimiert
# ---------------------------------------------------------
js_script = f"""
<script>
(function() {{
    const maxOpenDay = {max_open_day};

    document.querySelectorAll('.door-wrapper').forEach(function(wrapper) {{
        const day = parseInt(wrapper.getAttribute('data-day'), 10);
        const inner = wrapper.querySelector('.flip-card-inner');
        const isLocked = day > maxOpenDay;
        const storageKey = 'coaching_advent_door_' + day;

        if (!inner) return;

        if (!isLocked) {{
            // Zustand aus localStorage wiederherstellen
            const saved = window.localStorage.getItem(storageKey);
            if (saved === 'open') {{
                inner.classList.add('is-flipped');
            }}

            // Click-Event nur für nicht-gesperrte Türchen
            wrapper.addEventListener('click', function(e) {{
                e.preventDefault();
                e.stopPropagation();

                inner.classList.toggle('is-flipped');
                const isOpen = inner.classList.contains('is-flipped');

                if (isOpen) {{
                    window.localStorage.setItem(storageKey, 'open');
                }} else {{
                    window.localStorage.removeItem(storageKey);
                }}
            }});
        }} else {{
            // Für gesperrte Türchen: Klick blockieren
            wrapper.addEventListener('click', function(e) {{
                e.preventDefault();
                e.stopPropagation();
            }});
        }}
    }});
}})();
</script>
"""

full_html = CARDS_CSS + "\n" + "".join(cards_html_parts) + js_script

# ---------------------------------------------------------
# Im Streamlit-Fenster einbetten - Höhe dynamisch berechnen
# ---------------------------------------------------------
# Berechne die benötigte Höhe basierend auf der Anzahl Zeilen
# Bei 6 Spalten = 4 Zeilen, bei 4 Spalten = 6 Zeilen, etc.
# Kartenhöhe: 240px + gap: 1.2rem (~19px) = ca. 260px pro Zeile
# Plus Padding und etwas Extra-Platz
num_rows = 4  # 24 Türchen / 6 Spalten = 4 Zeilen
card_height = 240
gap = 19
total_height = (num_rows * card_height) + ((num_rows - 1) * gap) + 50  # +50px für Padding

components.html(full_html, height=total_height, scrolling=False)