@echo off
REM Ottieni il percorso del file .bat
set "current_dir=%~dp0"

REM Apri il primo terminale e avvia SSH
start cmd /k "cd /d "%current_dir%" && ssh stefano@192.168.1.234"

REM Apri il secondo terminale e avvia UDP.py
start cmd /k "cd /d "%current_dir%"/Code/ && python UDP.py"

REM Apri il terzo terminale e avvia ControllerGUI.py
start cmd /k "cd /d "%current_dir%"/Code/ && python ControllerGUI.py"

REM Apri il terzo terminale e avvia ControllerGUI.py
start cmd /k "cd /d "%current_dir%"/Code/ && python PyClient.py"

REM Apri il terzo terminale e avvia ControllerGUI.py
start cmd /k "cd /d "%current_dir%"/Code/ && python PingClient.py"
