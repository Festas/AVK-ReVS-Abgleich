"""
AVK-vs-ReVS Konfigurationsmodul
Verwaltet alle Konfigurationseinstellungen und Konstanten.

VERWENDUNG:
-----------
from config import Config

config = Config()
pfad = config.get('file_paths', 'netzwerkpfad')
theme = config.get('ui', 'theme')
"""
import os
import json
import copy
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


# ============================================================================
# DEFAULT CONFIGURATION
# ============================================================================

DEFAULT_CONFIG: Dict[str, Any] = {
    "file_paths": {
        "netzwerkpfad": "Z:\\KKK\\Fachbereiche\\TKW\\Allgemein\\ReVS Arbeitsordner\\12_ReVS-AVK-Abgleich",
        "revs_datei": "export.xlsx",
        "avk_dateinamen": ["AVK.xlsx", "Avk.xlsx", "avk.xlsx"],
        "abgleich_datei": "Abgleich.xlsx"
    },
    "spalten": {
        "revs": ["Verpackungs-ID", "Standort", "Reststoff-ID", "Nettomasse/kg"],
        "avk": ["Behälternummer", "Lagerort/Absender", "Abfallmasse [kg]", "Individuelle ID"]
    },
    "standorte": {
        "ort_kkk": "KKK",
        "standort_an_avk": "An AVK übergeben",
        "standort_zw6": "ZW6-1",
        "standort_container": "Containerstellplatz-ÜB",
        "container_bezeichnung": 'CONTAINER 20"'
    },
    "gebindetyp": {
        "dreistellig": ["V", "E"],
        "dreistellig_zwei": ["MH", "SO", "AK", "KE"]
    },
    "ui": {
        "theme": "dark",
        "window_size": "900x700"
    }
}


# ============================================================================
# CONFIG CLASS
# ============================================================================

class Config:
    """Konfigurationsmanager für AVK-vs-ReVS."""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = copy.deepcopy(DEFAULT_CONFIG)
        self.load_config()

    def load_config(self) -> None:
        """Lädt die Konfiguration aus der JSON-Datei, falls vorhanden."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self._merge_config(user_config)
                logger.info(f"Konfiguration geladen aus {self.config_path}")
            except Exception as e:
                logger.warning(f"Konfigurationsdatei konnte nicht geladen werden: {e}")

    def _merge_config(self, user_config: Dict) -> None:
        """Führt die Benutzerkonfiguration rekursiv mit den Defaults zusammen."""
        def merge_dict(base: Dict, override: Dict) -> None:
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        merge_dict(self.config, user_config)

    def save_config(self) -> bool:
        """Speichert die aktuelle Konfiguration in die JSON-Datei."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Konfiguration gespeichert in {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {e}")
            return False

    def get(self, *keys: str) -> Any:
        """Gibt einen Konfigurationswert anhand verschachtelter Schlüssel zurück."""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return None
            else:
                return None
        return value

    def set(self, value: Any, *keys: str) -> None:
        """Setzt einen Konfigurationswert anhand verschachtelter Schlüssel."""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
