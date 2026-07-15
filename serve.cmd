@echo off
rem Launch the RAW viewer dev server (with the COOP/COEP headers LibRaw needs)
rem and open it in the default browser.
cd /d "%~dp0"
set PORT=8791
start "" http://localhost:%PORT%/
python serve.py %PORT%
