# AVK-ReV-Abgleich

Desktop-Tool zum Abgleich von ReVS-Exporten mit AVK-Daten.  
Erstellt von Gregor Schuboth.

---

## Was macht dieses Tool?

Das Tool vergleicht den ReVS-Export (`export.xlsx`) mit der AVK-Datenliste (`AVK.xlsx`) und erstellt eine Excel-Datei (`Abgleich.xlsx`) mit allen Abweichungen:

- Gebinde, die in ReVS vorhanden sind, aber nicht im AVK
- Gebinde, die im AVK vorhanden sind, aber nicht in ReVS
- Gebinde, bei denen Reststoff-ID, Standort oder Masse abweichen

---

## Voraussetzungen

- Python 3.10 oder neuer
- Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

---

## Starten (aus dem Quellcode)

```bash
python main.py
```

---

## Standalone-EXE erstellen

### Windows

```bat
build.bat
```

Die fertige EXE liegt anschließend unter `dist\AVK-ReV-Abgleich.exe`.

### Linux / Mac

```bash
bash build.sh
```

---

## Konfiguration

Die Datei `config.json` im Programmverzeichnis enthält alle anpassbaren Einstellungen:

| Schlüssel | Beschreibung |
|---|---|
| `file_paths.netzwerkpfad` | Standardordner mit den Excel-Dateien |
| `file_paths.revs_datei` | Dateiname des ReVS-Exports |
| `file_paths.avk_dateinamen` | Mögliche Dateinamen der AVK-Datei |
| `file_paths.abgleich_datei` | Name der Ausgabedatei |
| `ui.theme` | Theme: `"dark"` oder `"light"` |
| `ui.window_size` | Fenstergröße, z. B. `"900x700"` |

Die Einstellungen werden beim nächsten Start automatisch geladen.

---

## Projektstruktur

```
AVK-ReV-Abgleich/
├── main.py              # Einstiegspunkt, GUI (tkinter)
├── gui.py               # Theme-System, Hilfsfunktionen, ResultsPreview
├── config.py            # Config-Klasse mit JSON-Laden und -Speichern
├── config.json          # Benutzerkonfiguration
├── abgleich_logic.py    # Kernlogik des Abgleichs
├── file_handler.py      # Excel-Laden und -Schreiben
├── requirements.txt     # Python-Abhängigkeiten
├── build.bat            # Windows-Build-Skript (PyInstaller)
├── build.sh             # Linux/Mac-Build-Skript
├── build.spec           # PyInstaller-Spezifikation
└── legacy/
    └── Abgleich.py      # Ursprüngliches Einzelskript (Referenz)
```
