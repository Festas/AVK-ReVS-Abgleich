"""Unit-Tests für die Config-Klasse in config.py."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import copy
import json

import pytest
from config import Config, DEFAULT_CONFIG


# ============================================================================
# Config.get
# ============================================================================

class TestConfigGet:
    def setup_method(self):
        self.config = Config.__new__(Config)
        self.config.config_path = "nonexistent_test.json"
        self.config.config = copy.deepcopy(DEFAULT_CONFIG)

    def test_get_einfacher_wert(self):
        result = self.config.get('file_paths', 'revs_datei')
        assert result == "export.xlsx"

    def test_get_verschachtelter_wert(self):
        result = self.config.get('ui', 'theme')
        assert result == "dark"

    def test_get_nicht_vorhandener_key(self):
        assert self.config.get('nicht_vorhanden') is None

    def test_get_verschachtelter_nicht_vorhandener_key(self):
        assert self.config.get('file_paths', 'nicht_vorhanden') is None

    def test_get_liste(self):
        result = self.config.get('spalten', 'revs')
        assert isinstance(result, list)
        assert "Verpackungs-ID" in result

    def test_get_sektion(self):
        result = self.config.get('standorte', 'ort_kkk')
        assert result == "KKK"


# ============================================================================
# Config.set
# ============================================================================

class TestConfigSet:
    def setup_method(self):
        self.config = Config.__new__(Config)
        self.config.config_path = "nonexistent_test.json"
        self.config.config = copy.deepcopy(DEFAULT_CONFIG)

    def test_set_einfacher_wert(self):
        self.config.set("light", 'ui', 'theme')
        assert self.config.get('ui', 'theme') == "light"

    def test_set_erstellt_neuen_key(self):
        self.config.set("wert", 'neue_sektion', 'neuer_key')
        assert self.config.get('neue_sektion', 'neuer_key') == "wert"

    def test_set_ueberschreibt_wert(self):
        self.config.set("neuer_pfad.xlsx", 'file_paths', 'revs_datei')
        assert self.config.get('file_paths', 'revs_datei') == "neuer_pfad.xlsx"

    def test_set_liste(self):
        self.config.set(["a", "b"], 'spalten', 'revs')
        assert self.config.get('spalten', 'revs') == ["a", "b"]


# ============================================================================
# Config.load_config / save_config
# ============================================================================

class TestConfigLoadSave:
    def test_load_aus_datei(self, tmp_path):
        config_file = tmp_path / "test_config.json"
        config_data = {"ui": {"theme": "light"}}
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        config = Config(str(config_file))
        assert config.get('ui', 'theme') == "light"
        # Default-Werte sollen noch vorhanden sein
        assert config.get('file_paths', 'revs_datei') == "export.xlsx"

    def test_save_und_reload(self, tmp_path):
        config_file = tmp_path / "test_config.json"
        config = Config(str(config_file))
        config.set("light", 'ui', 'theme')
        config.save_config()

        # Neu laden und prüfen
        config2 = Config(str(config_file))
        assert config2.get('ui', 'theme') == "light"

    def test_ungueltige_config_datei(self, tmp_path):
        config_file = tmp_path / "bad_config.json"
        config_file.write_text("kein gültiges json {{{", encoding="utf-8")

        # Soll auf Defaults zurückfallen
        config = Config(str(config_file))
        assert config.get('ui', 'theme') == "dark"

    def test_nicht_vorhandene_datei(self, tmp_path):
        config_file = tmp_path / "nicht_vorhanden.json"
        config = Config(str(config_file))
        # Defaults laden
        assert config.get('ui', 'theme') == "dark"
        assert config.get('file_paths', 'revs_datei') == "export.xlsx"

    def test_save_gibt_true_zurueck(self, tmp_path):
        config_file = tmp_path / "test_config.json"
        config = Config(str(config_file))
        result = config.save_config()
        assert result is True

    def test_merge_config_ueberschreibt_nur_geaenderte_werte(self, tmp_path):
        config_file = tmp_path / "partial_config.json"
        # Nur ui.theme ändern, Rest soll Default bleiben
        config_data = {"ui": {"theme": "light"}}
        config_file.write_text(json.dumps(config_data), encoding="utf-8")

        config = Config(str(config_file))
        assert config.get('ui', 'theme') == "light"
        assert config.get('ui', 'window_size') == "900x700"
