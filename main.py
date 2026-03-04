"""
AVK-ReV-Abgleich – Hauptanwendung
GUI-basiertes Desktop-Tool zum Abgleich von ReVS- und AVK-Exporten.
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from config import Config
from abgleich_logic import lese_spalten_indizes, vergleiche_gebinde
from file_handler import lade_dateien, schreibe_ergebnis
from gui import center_window, get_theme_colors, ResultsPreview


class AbgleichApp:
    """Hauptanwendungs-Klasse für den AVK-ReV-Abgleich."""

    TITLE = "AVK-ReV-Abgleich"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.config = Config()
        self._theme = self.config.get('ui', 'theme') or "dark"
        self.colors = get_theme_colors(self._theme)

        # Fenstergröße aus Konfiguration lesen
        window_size = self.config.get('ui', 'window_size') or "900x700"
        try:
            width, height = (int(x) for x in window_size.split("x"))
        except ValueError:
            width, height = 900, 700

        self.root.title(self.TITLE)
        self.root.resizable(True, True)
        center_window(self.root, width, height)
        self._build_ui()

    # ------------------------------------------------------------------
    # UI-Aufbau
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        c = self.colors
        self.root.configure(bg=c["bg"])

        # Header
        header = tk.Frame(self.root, bg=c["header_bg"])
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=self.TITLE,
            font=("Segoe UI", 18, "bold"),
            bg=c["header_bg"],
            fg=c["header_fg"],
            pady=14,
        ).pack(side=tk.LEFT, padx=20)

        tk.Button(
            header,
            text="☀ Hell / 🌙 Dunkel",
            command=self._toggle_theme,
            font=("Segoe UI", 9),
            bg=c["button_bg"],
            fg=c["button_fg"],
            relief=tk.FLAT,
            padx=10,
        ).pack(side=tk.RIGHT, padx=15, pady=10)

        # Pfadeingabe
        input_frame = tk.LabelFrame(
            self.root,
            text="  ReVS-Ordner  ",
            font=("Segoe UI", 10, "bold"),
            bg=c["bg"],
            fg=c["fg"],
            padx=12,
            pady=10,
        )
        input_frame.pack(fill=tk.X, padx=20, pady=(15, 5))

        self._pfad_var = tk.StringVar(value=self.config.get('file_paths', 'netzwerkpfad') or "")

        tk.Entry(
            input_frame,
            textvariable=self._pfad_var,
            font=("Segoe UI", 10),
            bg=c["entry_bg"],
            fg=c["entry_fg"],
            insertbackground=c["entry_fg"],
            relief=tk.FLAT,
            bd=2,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        tk.Button(
            input_frame,
            text="Durchsuchen...",
            command=self._browse_folder,
            font=("Segoe UI", 10),
            bg=c["button_bg"],
            fg=c["button_fg"],
            relief=tk.RAISED,
            padx=10,
        ).pack(side=tk.LEFT, padx=(8, 0))

        # Start-Schaltfläche
        tk.Button(
            self.root,
            text="▶  Abgleich starten",
            command=self._starte_abgleich,
            font=("Segoe UI", 13, "bold"),
            bg=c["accent"],
            fg=c["button_fg"],
            relief=tk.RAISED,
            padx=20,
            pady=8,
        ).pack(pady=12)

        # Ergebnisbereich
        result_frame = tk.LabelFrame(
            self.root,
            text="  Ergebnisse  ",
            font=("Segoe UI", 10, "bold"),
            bg=c["bg"],
            fg=c["fg"],
            padx=12,
            pady=8,
        )
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 5))

        self._result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=c["entry_bg"],
            fg=c["entry_fg"],
            insertbackground=c["entry_fg"],
            state=tk.DISABLED,
        )
        self._result_text.pack(fill=tk.BOTH, expand=True)

        # Statusleiste
        self._status_var = tk.StringVar(value="Bereit.")
        tk.Label(
            self.root,
            textvariable=self._status_var,
            font=("Segoe UI", 9),
            bg=c["header_bg"],
            fg=c["fg"],
            anchor=tk.W,
            padx=10,
            pady=4,
        ).pack(fill=tk.X, side=tk.BOTTOM)

    # ------------------------------------------------------------------
    # Aktionen
    # ------------------------------------------------------------------

    def _browse_folder(self) -> None:
        folder = filedialog.askdirectory(title="ReVS-Ordner auswählen")
        if folder:
            self._pfad_var.set(folder)

    def _starte_abgleich(self) -> None:
        pfad = self._pfad_var.get().strip()
        if not pfad:
            messagebox.showerror("Fehler", "Bitte geben Sie den ReVS-Ordnerpfad an.")
            return

        revs_datei = self.config.get('file_paths', 'revs_datei') or "export.xlsx"
        avk_dateinamen = self.config.get('file_paths', 'avk_dateinamen') or ["AVK.xlsx"]
        abgleich_datei = self.config.get('file_paths', 'abgleich_datei') or "Abgleich.xlsx"
        spalten_revs = self.config.get('spalten', 'revs') or []
        spalten_avk = self.config.get('spalten', 'avk') or []

        self._set_status("Lade Dateien…")
        self.root.update_idletasks()

        try:
            revs, avk = lade_dateien(pfad, revs_datei, avk_dateinamen)
        except FileNotFoundError as e:
            messagebox.showerror("Datei nicht gefunden", str(e))
            self._set_status("Fehler beim Laden der Dateien.")
            return

        try:
            idx_revs = lese_spalten_indizes(revs, spalten_revs)
            idx_avk = lese_spalten_indizes(avk, spalten_avk)
        except ValueError as e:
            messagebox.showerror("Spaltenfehler", str(e))
            self._set_status("Fehler beim Einlesen der Spalten.")
            return

        self._set_status("Führe Abgleich durch…")
        self.root.update_idletasks()

        fehler = vergleiche_gebinde(revs, avk, idx_revs, idx_avk, self.config)

        ausgabe_pfad = schreibe_ergebnis(pfad, abgleich_datei, fehler)

        self._zeige_ergebnisse(fehler)
        count = len(fehler)
        self._set_status(f"{count} Abweichung(en) gefunden. Ergebnis gespeichert: {ausgabe_pfad}")

        if count == 0:
            messagebox.showinfo(
                "Abgleich abgeschlossen",
                f"Keine Abweichungen gefunden!\n\nErgebnis gespeichert unter:\n{ausgabe_pfad}",
            )
        else:
            messagebox.showinfo(
                "Abgleich abgeschlossen",
                f"{count} Abweichung(en) gefunden.\n\nErgebnis gespeichert unter:\n{ausgabe_pfad}",
            )

    def _zeige_ergebnisse(self, fehler: list) -> None:
        c = self.colors
        self._result_text.config(state=tk.NORMAL)
        self._result_text.delete("1.0", tk.END)

        if not fehler:
            self._result_text.insert(tk.END, "✔  Keine Abweichungen gefunden!\n")
            self._result_text.tag_configure("ok", foreground=c["success"])
            self._result_text.tag_add("ok", "1.0", tk.END)
        else:
            headers = [
                "Verpackungs-ID", "Reststoff-ID", "Individuelle ID",
                "Standort ReVS", "Standort AVK",
                "ReVS Nettomasse/kg", "AVK Abfallmasse [kg]",
            ]
            col_w = [22, 18, 18, 22, 22, 20, 20]
            header_line = "  ".join(h.ljust(w) for h, w in zip(headers, col_w))
            self._result_text.insert(tk.END, header_line + "\n")
            self._result_text.insert(tk.END, "-" * len(header_line) + "\n")
            for row in fehler:
                line = "  ".join(str(cell).ljust(w) for cell, w in zip(row, col_w))
                self._result_text.insert(tk.END, line + "\n")

        self._result_text.config(state=tk.DISABLED)

    def _set_status(self, text: str) -> None:
        self._status_var.set(text)

    def _toggle_theme(self) -> None:
        self._theme = "light" if self._theme == "dark" else "dark"
        self.colors = get_theme_colors(self._theme)
        self.config.set(self._theme, 'ui', 'theme')
        self.config.save_config()
        # Rebuild UI with new theme
        for widget in self.root.winfo_children():
            widget.destroy()
        self._build_ui()


# ============================================================================
# EINSTIEGSPUNKT
# ============================================================================

def main() -> None:
    root = tk.Tk()
    app = AbgleichApp(root)  # noqa: F841
    root.mainloop()


if __name__ == "__main__":
    main()
