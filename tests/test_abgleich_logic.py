"""Unit-Tests für die Kernlogik in abgleich_logic.py."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from abgleich_logic import (
    berechne_avk_standort,
    vergleiche_gebinde,
    lese_spalten_indizes,
    _normalize_mass,
    FEHLER_HEADER,
    FEHLER_COL_WIDTHS,
)


class MockConfig:
    """Minimale Config-Implementierung für Tests."""

    _DATA = {
        'standorte': {
            'ort_kkk': 'KKK',
            'standort_an_avk': 'An AVK übergeben',
            'standort_zw6': 'ZW6-1',
            'standort_container': 'Containerstellplatz-ÜB',
            'container_bezeichnung': 'CONTAINER 20"',
        },
        'gebindetyp': {
            'dreistellig': ['V', 'E'],
            'dreistellig_zwei': ['MH', 'SO', 'AK', 'KE'],
        },
    }

    def get(self, *keys):
        val = self._DATA
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return None
        return val


# ============================================================================
# MockSheet für Sheet-Interface-Tests
# ============================================================================

class MockSheet:
    """Einfaches Sheet-Mock für Tests (bietet iter_rows und cell-Interface)."""

    def __init__(self, rows):
        self._rows = [tuple(r) for r in rows]

    @property
    def max_row(self):
        return len(self._rows)

    @property
    def max_column(self):
        return max((len(r) for r in self._rows), default=0)

    def cell(self, row, col):
        class _Cell:
            def __init__(self, value):
                self.value = value
        try:
            return _Cell(self._rows[row - 1][col - 1])
        except IndexError:
            return _Cell(None)

    def iter_rows(self, min_row=1, max_row=None, values_only=False):
        end = max_row if max_row is not None else len(self._rows)
        for i in range(min_row - 1, end):
            if i >= len(self._rows):
                break
            yield self._rows[i]


def _make_revs_sheet(data_rows):
    """Erstellt ein MockSheet mit Header + Datenzeilen für ReVS."""
    header = ["Verpackungs-ID", "Standort", "Reststoff-ID", "Nettomasse/kg"]
    return MockSheet([header] + data_rows)


def _make_avk_sheet(data_rows):
    """Erstellt ein MockSheet mit Header + Datenzeilen für AVK."""
    header = ["Behälternummer", "Lagerort/Absender", "Abfallmasse [kg]", "Individuelle ID"]
    return MockSheet([header] + data_rows)


def _get_idx_revs(sheet):
    return lese_spalten_indizes(sheet, ["Verpackungs-ID", "Standort", "Reststoff-ID", "Nettomasse/kg"])


def _get_idx_avk(sheet):
    return lese_spalten_indizes(sheet, ["Behälternummer", "Lagerort/Absender", "Abfallmasse [kg]", "Individuelle ID"])


# ============================================================================
# _normalize_mass
# ============================================================================

class TestNormalizeMass:
    def test_integer(self):
        assert _normalize_mass(100) == 100.0

    def test_float(self):
        assert _normalize_mass(100.5) == 100.5

    def test_string_dot(self):
        assert _normalize_mass("100.5") == 100.5

    def test_string_comma(self):
        assert _normalize_mass("100,5") == 100.5

    def test_string_integer(self):
        assert _normalize_mass("100") == 100.0

    def test_none(self):
        assert _normalize_mass(None) is None

    def test_empty_string(self):
        assert _normalize_mass("") is None

    def test_invalid_string(self):
        assert _normalize_mass("abc") is None

    def test_100_equals_100_0(self):
        """100 und 100.0 sollen als gleich gelten."""
        assert _normalize_mass("100") == _normalize_mass("100.0")

    def test_comma_equals_dot(self):
        """100,5 und 100.5 sollen als gleich gelten."""
        assert _normalize_mass("100,5") == _normalize_mass("100.5")

    def test_whitespace_stripped(self):
        assert _normalize_mass("  100.5  ") == 100.5


# ============================================================================
# berechne_avk_standort
# ============================================================================

class TestBerechneAvkStandort:
    def setup_method(self):
        self.config = MockConfig()

    def test_leer(self):
        assert berechne_avk_standort("", self.config) == ""

    def test_ex_prefix(self):
        assert berechne_avk_standort("EX-001", self.config) == "KKK"

    def test_ex_prefix_variante(self):
        assert berechne_avk_standort("EX-KKK-123", self.config) == "KKK"

    def test_standort_zw6(self):
        assert berechne_avk_standort("ZW6-1", self.config) == "W 06"

    def test_standort_container(self):
        assert berechne_avk_standort("Containerstellplatz-ÜB", self.config) == 'CONTAINER 20"'

    def test_al_mit_z(self):
        # AL...Z{A}{12345} → "A 12345"
        result = berechne_avk_standort("ALxxxxxZA12345", self.config)
        assert result == "A 12345"

    def test_unbekannt(self):
        assert berechne_avk_standort("UNBEKANNT", self.config) == ""


# ============================================================================
# lese_spalten_indizes
# ============================================================================

class TestLeseSpaltenIndizes:
    def test_normale_spalten(self):
        sheet = MockSheet([["A", "B", "C"]])
        indizes = lese_spalten_indizes(sheet, ["A", "C"])
        assert indizes["A"] == 1
        assert indizes["C"] == 3

    def test_fehlende_spalte(self):
        sheet = MockSheet([["A", "B"]])
        with pytest.raises(ValueError, match="Spalte 'X' nicht im Header"):
            lese_spalten_indizes(sheet, ["X"])

    def test_alle_spalten(self):
        sheet = MockSheet([["A", "B", "C", "D"]])
        indizes = lese_spalten_indizes(sheet, ["A", "B", "C", "D"])
        assert indizes == {"A": 1, "B": 2, "C": 3, "D": 4}

    def test_none_werte_im_header(self):
        sheet = MockSheet([[None, None, "C"]])
        indizes = lese_spalten_indizes(sheet, ["C"])
        assert indizes["C"] == 3


# ============================================================================
# vergleiche_gebinde
# ============================================================================

class TestVergleicheGebinde:
    def setup_method(self):
        self.config = MockConfig()

    def test_keine_abweichungen(self):
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100"]])
        avk = _make_avk_sheet([["A 001", "KKK", "100", "RS-001"]])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert fehler == []

    def test_revs_nicht_in_avk(self):
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100"]])
        avk = _make_avk_sheet([["A 999", "KKK", "100", "RS-999"]])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert any("nicht im AVK gelistet" in str(row) for row in fehler)

    def test_avk_nicht_in_revs(self):
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100"]])
        avk = _make_avk_sheet([
            ["A 001", "KKK", "100", "RS-001"],
            ["A 002", "KKK", "200", "RS-002"],
        ])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert any("nicht im ReVS gelistet" in str(row) for row in fehler)

    def test_masse_abweichung(self):
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100"]])
        avk = _make_avk_sheet([["A 001", "KKK", "200", "RS-001"]])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert len(fehler) == 1
        assert fehler[0][5] == "100"
        assert fehler[0][6] == "200"

    def test_masse_normalisierung_keine_abweichung(self):
        """100.0 und 100 sollen als gleich gelten (keine falsch-positiven Abweichungen)."""
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100.0"]])
        avk = _make_avk_sheet([["A 001", "KKK", "100", "RS-001"]])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert fehler == []

    def test_masse_komma_normalisierung(self):
        """100,5 und 100.5 sollen als gleich gelten."""
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100,5"]])
        avk = _make_avk_sheet([["A 001", "KKK", "100.5", "RS-001"]])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert fehler == []

    def test_reststoff_id_abweichung(self):
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100"]])
        avk = _make_avk_sheet([["A 001", "KKK", "100", "RS-999"]])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert len(fehler) == 1
        assert fehler[0][2] == "RS-999"

    def test_standort_abweichung(self):
        revs = _make_revs_sheet([["A-001", "EX-001", "RS-001", "100"]])
        avk = _make_avk_sheet([["A 001", "ANDERER-ORT", "100", "RS-001"]])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert len(fehler) == 1
        assert fehler[0][4] == "ANDERER-ORT"

    def test_leere_liste(self):
        revs = _make_revs_sheet([])
        avk = _make_avk_sheet([])
        fehler = vergleiche_gebinde(revs, avk, _get_idx_revs(revs), _get_idx_avk(avk), self.config)
        assert fehler == []


# ============================================================================
# Konstanten
# ============================================================================

class TestKonstanten:
    def test_fehler_header_laenge(self):
        assert len(FEHLER_HEADER) == 7

    def test_fehler_col_widths_laenge(self):
        assert len(FEHLER_COL_WIDTHS) == 7

    def test_fehler_col_widths_positive(self):
        assert all(w > 0 for w in FEHLER_COL_WIDTHS)
