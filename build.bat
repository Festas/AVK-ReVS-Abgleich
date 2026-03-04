@echo off
REM Build-Skript für AVK-ReV-Abgleich (Windows)

echo === AVK-ReV-Abgleich Build-Skript ===
echo.

REM PyInstaller prüfen
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller nicht gefunden. Installiere...
    pip install pyinstaller
)

REM Alte Builds bereinigen
echo Bereinige alte Build-Artefakte...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Anwendung bauen
echo Erstelle Standalone-Anwendung...
pyinstaller build.spec

REM Ergebnis prüfen
if exist "dist\AVK-ReV-Abgleich.exe" (
    echo.
    echo Build erfolgreich!
    echo Pfad zur EXE: dist\AVK-ReV-Abgleich.exe
    echo.
    dir dist\AVK-ReV-Abgleich.exe
) else (
    echo.
    echo Build fehlgeschlagen!
    echo Bitte Fehlermeldungen oben prüfen.
    exit /b 1
)

pause
