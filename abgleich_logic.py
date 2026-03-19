"""
AVK-vs-ReVS Vergleichslogik
Enthält die reine Vergleichslogik zwischen ReVS- und AVK-Daten.
"""
from typing import Any, Dict, List

FEHLER_HEADER = [
    "Verpackungs-ID", "Reststoff-ID", "Individuelle ID",
    "Standort ReVS", "Standort AVK",
    "ReVS Nettomasse/kg", "AVK Abfallmasse [kg]",
]


def lese_spalten_indizes(sheet: Any, spalten_namen: List[str]) -> Dict[str, int]:
    """Ermittelt die Spaltenindizes für die angegebenen Spaltennamen aus dem Header."""
    header = [sheet.cell(1, col).value for col in range(1, sheet.max_column + 1)]
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
    for zeile in range(1, avk.max_row + 1):
        zellwert = avk.cell(zeile, idx_avk["Behälternummer"]).value
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

        lagerort = avk.cell(zeile, idx_avk["Lagerort/Absender"]).value
        lagerort = lagerort if lagerort is not None else ""
        masse = avk.cell(zeile, idx_avk["Abfallmasse [kg]"]).value
        masse = masse if masse is not None else ""
        ind_id = avk.cell(zeile, idx_avk["Individuelle ID"]).value
        ind_id = ind_id if ind_id is not None else ""

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
    for zeile in range(1, revs.max_row + 1):
        verpackungs_id = revs.cell(zeile, idx_revs["Verpackungs-ID"]).value
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

        standort = revs.cell(zeile, idx_revs["Standort"]).value
        standort = str(standort) if standort is not None else ""
        reststoff_id = revs.cell(zeile, idx_revs["Reststoff-ID"]).value
        reststoff_id = reststoff_id if reststoff_id is not None else ""
        nettomasse = revs.cell(zeile, idx_revs["Nettomasse/kg"]).value
        nettomasse = nettomasse if nettomasse is not None else ""

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

    # Abgleich durchführen
    fehler: List[List[Any]] = []
    for revs_eintrag in gebinde_revs:
        for avk_eintrag in gebinde_avk:
            if avk_eintrag["vorhanden"]:
                continue
            if revs_eintrag["nummer"] == avk_eintrag["nummer"]:
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

                if str(revs_eintrag["nettomasse"]) == str(avk_eintrag["masse"]):
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
