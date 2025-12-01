# 🎄 Adventskalender "Nicht mehr brav sein"

Ein interaktiver Adventskalender mit 24 Türchen für mutige und neue Impulse.

## Installation
```bash
pip install -r requirements.txt
```

## Nutzung
```bash
streamlit run app.py
```

## Excel-Datei Format

Die `advent_content.xlsx` benötigt folgende Spalten:
- `day` (1-24)
- `title` (optional)
- `text` (Pflicht)
- `person` (optional)
- `image_url` (optional)