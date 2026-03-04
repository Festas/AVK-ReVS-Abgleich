#!/bin/bash
# Build-Skript für AVK-ReV-Abgleich (Linux/Mac)

echo "=== AVK-ReV-Abgleich Build-Skript ==="
echo ""

# PyInstaller prüfen
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller nicht gefunden. Installiere..."
    pip install pyinstaller
fi

# Alte Builds bereinigen
echo "Bereinige alte Build-Artefakte..."
rm -rf build/ dist/

# Anwendung bauen
echo "Erstelle Standalone-Anwendung..."
pyinstaller build.spec

# Ergebnis prüfen
if [ -f "dist/AVK-ReV-Abgleich.exe" ] || [ -f "dist/AVK-ReV-Abgleich" ]; then
    echo ""
    echo "✓ Build erfolgreich!"
    echo "Pfad zur Anwendung: dist/"
    echo ""
    if [ -f "dist/AVK-ReV-Abgleich.exe" ]; then
        ls -lh dist/AVK-ReV-Abgleich.exe
    else
        ls -lh dist/AVK-ReV-Abgleich
    fi
else
    echo ""
    echo "✗ Build fehlgeschlagen!"
    echo "Bitte Fehlermeldungen oben prüfen."
    exit 1
fi
