"""
AVK-vs-ReVS GUI-Modul
Theme-System, Hilfsfunktionen und wiederverwendbare Dialog-Klassen.
"""
import os
import sys
import tkinter as tk
from tkinter import scrolledtext
from typing import Any, Dict, List, Optional

from abgleich_logic import FEHLER_HEADER, FEHLER_COL_WIDTHS


# ============================================================================
# RESOURCE PATH FÜR PYINSTALLER
# ============================================================================

def resource_path(relative_path: str) -> str:
    """
    Findet den Pfad zu Ressourcen, auch in der gepackten .exe.

    Args:
        relative_path: Relativer Pfad zur Ressource

    Returns:
        Absoluter Pfad zur Ressource
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ============================================================================
# THEME-DEFINITIONEN
# ============================================================================

DARK_THEME: Dict[str, str] = {
    "bg": "#0d1b2a",
    "fg": "#ffffff",
    "accent": "#4da8da",
    "button_bg": "#4da8da",
    "button_fg": "#ffffff",
    "button_hover": "#5db8ea",
    "entry_bg": "#1b263b",
    "entry_fg": "#ffffff",
    "header_bg": "#1b263b",
    "header_fg": "#ffffff",
    "success": "#4ade80",
    "error": "#f87171",
    "warning": "#ffc857",
    "border": "#2d4a6f",
    "select_bg": "#4da8da",
    "select_fg": "#ffffff",
    "listbox_bg": "#0d1b2a",
    "listbox_fg": "#ffffff",
    "warning_fg": "#ffc857",
    "success_fg": "#4ade80",
    "group_bg": "#1b263b",
    "group_fg": "#ffffff",
}

LIGHT_THEME: Dict[str, str] = {
    "bg": "#f8fafc",
    "fg": "#0d1b2a",
    "accent": "#4da8da",
    "button_bg": "#4da8da",
    "button_fg": "#ffffff",
    "button_hover": "#5db8ea",
    "entry_bg": "#ffffff",
    "entry_fg": "#0d1b2a",
    "header_bg": "#e2e8f0",
    "header_fg": "#0d1b2a",
    "success": "#16a34a",
    "error": "#dc2626",
    "warning": "#d97706",
    "border": "#cbd5e1",
    "select_bg": "#4da8da",
    "select_fg": "#ffffff",
    "listbox_bg": "#ffffff",
    "listbox_fg": "#0d1b2a",
    "warning_fg": "#d97706",
    "success_fg": "#16a34a",
    "group_bg": "#e2e8f0",
    "group_fg": "#0d1b2a",
}

THEMES: Dict[str, Dict[str, str]] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
}


def get_theme_colors(theme_name: str) -> Dict[str, str]:
    """Gibt die Farbpalette für das gewünschte Theme zurück."""
    return THEMES.get(theme_name, LIGHT_THEME)


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def center_window(window: tk.Tk, width: Optional[int] = None, height: Optional[int] = None) -> None:
    """Zentriert ein Fenster auf dem Bildschirm.

    Wenn width und height weggelassen werden, wird die aktuelle Fenstergröße verwendet.
    """
    window.update_idletasks()
    if width is None or height is None:
        width = window.winfo_width()
        height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")


# ============================================================================
# RESULTS PREVIEW DIALOG
# ============================================================================

class ResultsPreview(tk.Toplevel):
    """Zeigt die Abgleich-Ergebnisse in einem scrollbaren Fenster."""

    def __init__(
        self,
        parent: tk.Tk,
        fehler: List[List[Any]],
        colors: Dict[str, str],
    ) -> None:
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Abgleich – Vorschau der Abweichungen")
        self.geometry("1100x550")
        self.configure(bg=colors["bg"])

        # Header
        header_frame = tk.Frame(self, bg=colors["header_bg"])
        header_frame.pack(fill=tk.X)
        tk.Label(
            header_frame,
            text=f"Vorschau – {len(fehler)} Abweichung(en) gefunden",
            font=("Segoe UI", 13, "bold"),
            bg=colors["header_bg"],
            fg=colors["header_fg"],
            pady=12,
        ).pack()

        # Scrolled text table
        text_frame = tk.Frame(self, bg=colors["bg"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self._text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 9),
            bg=colors["entry_bg"],
            fg=colors["entry_fg"],
            insertbackground=colors["entry_fg"],
        )
        self._text.pack(fill=tk.BOTH, expand=True)

        # Populate table
        header_line = "  ".join(h.ljust(w) for h, w in zip(FEHLER_HEADER, FEHLER_COL_WIDTHS))
        self._text.insert(tk.END, header_line + "\n")
        self._text.insert(tk.END, "-" * len(header_line) + "\n")
        for row in fehler:
            line = "  ".join(str(cell).ljust(w) for cell, w in zip(row, FEHLER_COL_WIDTHS))
            self._text.insert(tk.END, line + "\n")
        self._text.config(state=tk.DISABLED)

        # Close button
        btn_frame = tk.Frame(self, bg=colors["bg"])
        btn_frame.pack(fill=tk.X, padx=15, pady=15)
        tk.Button(
            btn_frame,
            text="Schließen",
            command=self.destroy,
            font=("Segoe UI", 10),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            width=15,
            relief=tk.RAISED,
        ).pack(side=tk.RIGHT)

        self.after(10, lambda: self._center(parent))

    def _center(self, parent: tk.Tk) -> None:
        self.update_idletasks()
        w, h = 1100, 550
        px = parent.winfo_x() + (parent.winfo_width() - w) // 2
        py = parent.winfo_y() + (parent.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{px}+{py}")
