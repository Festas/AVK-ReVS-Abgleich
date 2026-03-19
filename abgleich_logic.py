"""
AVK-vs-ReVS Vergleichslogik
Enthält die reine Vergleichslogik zwischen ReVS- und AVK-Daten.
"""
from typing import Any, Dict, List, Optional

FEHLER_HEADER = [
    "Verpackungs-ID", "Reststoff-ID", "Individuelle ID",
    "Standort ReVS", "Standort AVK",
    "ReVS Nettomasse/kg", "AVK Abfallmasse [kg]",
]

FEHLER_COL_WIDTHS = [22, 18, 18, 22, 22, 20, 20]


def _safe_str(value: Any) -> str:
    """Konvertiert den Wert zu String, oder gibt leeren String zurück falls None."""
    return str(value) if value is not None else ""


def _normalize_mass(value: Any) -> Optional[float]:
    """Normalisiert Massenwerte für den Vergleich (Komma→Punkt, float-Konvertierung)."""
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ".").strip())
    except ValueError:
        return None


def lese_spalten_indizes(sheet: Any, spalten_namen: List[str]) -> Dict[str, int]:
    """Ermittelt die Spaltenindizes für die angegebenen Spaltennamen aus dem Header."""
    header: List[Any] = []
    for row in sheet.iter_rows(min_row=1, max_row=1, values_only=True):
        header = list(row)
        break
    indizes = {}
    for name in spalten_namen:
        if name not in header:
            raise ValueError(
                f"Spalte '{name}' nicht im Header gefunden. Verfügbare Spalten: {header}"
            )
        indizes[name] = header.index(name) + 1
    return indizes


def berechne_avk_standort(standort: str, config: Any) -> str:
    """Berechnet den AVK-Übersetzungsstandort aus dem ReVS-Standort."""
    ort_kkk = config.get('standorte', 'ort_kkk')
    standort_zw6 = config.get('standorte', 'standort_zw6')
    standort_container = config.get('standorte', 'standort_container')
    container_bezeichnung = config.get('standorte', 'container_bezeichnung')

    if not standort:
        return ""
    if standort[0:2] == "EX":
        return ort_kkk
    if standort == standort_zw6:
        return "W 06"
    if standort == standort_container:
        return container_bezeichnung
    if standort[0:2] in ("A-", "AL", "ST") or standort[0:1] == "E":
        z_pos = standort.find("Z")
        if z_pos == -1:
            return standort
        return standort[z_pos + 1: z_pos + 2] + " " + standort[z_pos + 2: z_pos + 7]
    return ""


def vergleiche_gebinde(
    revs: Any,
    avk: Any,
    idx_revs: Dict[str, int],
    idx_avk: Dict[str, int],
    config: Any,
) -> List[List[Any]]:
    """Führt den Abgleich der Gebinde zwischen ReVS und AVK durch."""
    ort_kkk = config.get('standorte', 'ort_kkk')
    standort_an_avk = config.get('standorte', 'standort_an_avk')
    gebindetyp_dreistellig = tuple(config.get('gebindetyp', 'dreistellig') or [])
    gebindetyp_dreistellig_zwei = tuple(config.get('gebindetyp', 'dreistellig_zwei') or [])

    aufgenommen_avk: set = set()
    aufgenommen_revs: set = set()
    ort_kkk_vorhanden = False

    # AVK-Gebinde einlesen
    gebinde_avk = []
    for avk_row in avk.iter_rows(values_only=True):
        zellwert = avk_row[idx_avk["Behälternummer"] - 1]
        if zellwert is None or zellwert == "":
            continue
        zellwert_str = str(zellwert)

        leerzeichen_pos = zellwert_str.find(" ")
        gebinde_typ = zellwert_str[0:leerzeichen_pos] if leerzeichen_pos != -1 else zellwert_str

        stern_pos = zellwert_str.find("*")
        if stern_pos != -1:
            gebinde_nummer = zellwert_str[0:stern_pos]
        elif zellwert_str[0:3] == ort_kkk:
            gebinde_typ = ort_kkk
            gebinde_nummer = zellwert_str
        else:
            gebinde_nummer = zellwert_str

        lagerort = _safe_str(avk_row[idx_avk["Lagerort/Absender"] - 1])
        masse = _safe_str(avk_row[idx_avk["Abfallmasse [kg]"] - 1])
        ind_id = _safe_str(avk_row[idx_avk["Individuelle ID"] - 1])

        if gebinde_typ:
            aufgenommen_avk.add(gebinde_typ)
        if str(lagerort) == ort_kkk:
            ort_kkk_vorhanden = True

        gebinde_avk.append({
            "typ": gebinde_typ,
            "nummer": gebinde_nummer,
            "lagerort": lagerort,
            "masse": masse,
            "ind_id": ind_id,
            "vorhanden": False,
        })

    # ReVS-Gebinde einlesen
    gebinde_revs = []
    for revs_row in revs.iter_rows(values_only=True):
        verpackungs_id = revs_row[idx_revs["Verpackungs-ID"] - 1]
        if verpackungs_id is None or verpackungs_id == "":
            continue
        verpackungs_id_str = str(verpackungs_id)

        minus_pos = verpackungs_id_str.find("-")
        gebinde_typ = verpackungs_id_str[0:minus_pos] if minus_pos != -1 else verpackungs_id_str

        if gebinde_typ not in aufgenommen_avk:
            continue

        # Gebindenummer bestimmen
        if minus_pos != -1:
            if gebinde_typ[0:1] in gebindetyp_dreistellig or gebinde_typ[0:2] in gebindetyp_dreistellig_zwei:
                gebinde_nummer = gebinde_typ + " " + verpackungs_id_str[minus_pos + 2: minus_pos + 5]
            elif gebinde_typ[0:3] == ort_kkk:
                gebinde_nummer = ""
            else:
                gebinde_nummer = gebinde_typ + " " + verpackungs_id_str[minus_pos + 1: minus_pos + 7]
        else:
            gebinde_nummer = gebinde_typ

        standort_val = revs_row[idx_revs["Standort"] - 1]
        standort = _safe_str(standort_val)
        reststoff_id = _safe_str(revs_row[idx_revs["Reststoff-ID"] - 1])
        nettomasse = _safe_str(revs_row[idx_revs["Nettomasse/kg"] - 1])

        if gebinde_typ:
            aufgenommen_revs.add(gebinde_typ)

        avk_standort = berechne_avk_standort(standort, config)

        gebinde_revs.append({
            "typ": gebinde_typ,
            "nummer": gebinde_nummer,
            "standort": standort,
            "reststoff_id": reststoff_id,
            "nettomasse": nettomasse,
            "avk_standort": avk_standort,
            "vorhanden": False,
        })

    # AVK-Gebinde nach Nummer indexieren → O(n + m) statt O(n * m)
    avk_index: Dict[str, List[dict]] = {}
    for eintrag in gebinde_avk:
        avk_index.setdefault(eintrag["nummer"], []).append(eintrag)

    # Abgleich durchführen
    fehler: List[List[Any]] = []
    for revs_eintrag in gebinde_revs:
        kandidaten = avk_index.get(revs_eintrag["nummer"], [])
        for avk_eintrag in kandidaten:
            if avk_eintrag["vorhanden"]:
                continue

            revs_eintrag["vorhanden"] = True
            avk_eintrag["vorhanden"] = True

            abweichungen = 0
            ind_id_out = avk_eintrag["ind_id"]
            standort_avk_out = avk_eintrag["lagerort"]
            masse_avk_out = avk_eintrag["masse"]

            if str(revs_eintrag["reststoff_id"]) == str(avk_eintrag["ind_id"]):
                ind_id_out = "stimmt mit ReVS"
            else:
                abweichungen += 1

            if revs_eintrag["avk_standort"] == str(avk_eintrag["lagerort"]):
                standort_avk_out = "stimmt mit ReVS"
            else:
                abweichungen += 1

            masse_revs_norm = _normalize_mass(revs_eintrag["nettomasse"])
            masse_avk_norm = _normalize_mass(avk_eintrag["masse"])
            if masse_revs_norm == masse_avk_norm:
                masse_avk_out = "stimmt mit ReVS"
            else:
                abweichungen += 1

            if abweichungen > 0:
                fehler.append([
                    revs_eintrag["nummer"],
                    revs_eintrag["reststoff_id"],
                    ind_id_out,
                    revs_eintrag["standort"],
                    standort_avk_out,
                    revs_eintrag["nettomasse"],
                    masse_avk_out,
                ])
            break

        # ReVS-Gebinde nicht im AVK gefunden
        # KKK-Gebinde nur melden, wenn KKK auch im AVK-Auszug enthalten ist
        if (
            not revs_eintrag["vorhanden"]
            and revs_eintrag["typ"] in aufgenommen_avk
            and not (revs_eintrag["avk_standort"] == ort_kkk and not ort_kkk_vorhanden)
            and revs_eintrag["standort"] != standort_an_avk
        ):
            fehler.append([
                revs_eintrag["nummer"],
                revs_eintrag["reststoff_id"],
                "",
                revs_eintrag["standort"],
                "nicht im AVK gelistet",
                revs_eintrag["nettomasse"],
                "",
            ])

    # AVK-Gebinde nicht im ReVS gefunden
    for avk_eintrag in gebinde_avk:
        if not avk_eintrag["vorhanden"] and avk_eintrag["typ"] in aufgenommen_revs:
            fehler.append([
                avk_eintrag["nummer"],
                "nicht im ReVS gelistet",
                avk_eintrag["ind_id"],
                "",
                avk_eintrag["lagerort"],
                "",
                avk_eintrag["masse"],
            ])

    return fehler
