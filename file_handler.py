"""
AVK-ReV-Abgleich Datei-Handler
Lädt und schreibt Excel-Dateien für den Abgleich.
"""
from pathlib import Path
from typing import Any, List, Tuple

from openpyxl import load_workbook, Workbook

from abgleich_logic import FEHLER_HEADER


def lade_dateien(
    pfad: str,
    revs_datei: str,
    avk_dateinamen: List[str],
) -> Tuple[Any, Any]:
    """Lädt ReVS- und AVK-Workbooks aus dem angegebenen Pfad."""
    revs_pfad = Path(pfad, revs_datei)
    if not revs_pfad.exists():
        raise FileNotFoundError(f"ReVS-Datei nicht gefunden: {revs_pfad}")
    revs = load_workbook(str(revs_pfad)).active

    avk_sheet = None
    for dateiname in avk_dateinamen:
        avk_pfad = Path(pfad, dateiname)
        if avk_pfad.exists():
            avk_sheet = load_workbook(str(avk_pfad)).active
            break
    if avk_sheet is None:
        raise FileNotFoundError(f"AVK-Datei nicht gefunden in: {pfad}")

    return revs, avk_sheet


def schreibe_ergebnis(
    pfad: str,
    abgleich_datei: str,
    fehler: List[List[Any]],
) -> str:
    """Schreibt die Fehlerliste in eine neue Excel-Datei und gibt den Ausgabepfad zurück."""
    ergebnis = Workbook()
    ws = ergebnis.active
    ws.cell(1, 1).value = "Fehlerhafte und fehlende Gebinde"
    ws.append(FEHLER_HEADER)
    for zeile in fehler:
        ws.append(zeile)
    ausgabe_pfad = str(Path(pfad, abgleich_datei))
    ergebnis.save(ausgabe_pfad)
    ergebnis.close()
    return ausgabe_pfad
