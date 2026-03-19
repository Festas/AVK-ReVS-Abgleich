#!/bin/bash
# Build-Skript für AVK-vs-ReVS (Linux/Mac)

echo "=== AVK-vs-ReVS Build-Skript ==="
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
if [ -f "dist/AVK-vs-ReVS.exe" ] || [ -f "dist/AVK-vs-ReVS" ]; then
    echo ""
    echo "✓ Build erfolgreich!"
    echo "Pfad zur Anwendung: dist/"
    echo ""
    if [ -f "dist/AVK-vs-ReVS.exe" ]; then
        ls -lh dist/AVK-vs-ReVS.exe
    else
        ls -lh dist/AVK-vs-ReVS
    fi
else
    echo ""
    echo "✗ Build fehlgeschlagen!"
    echo "Bitte Fehlermeldungen oben prüfen."
    exit 1
fi
