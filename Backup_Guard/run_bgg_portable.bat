@echo off
title Jalankan Backup Guard GUI (Portable)

REM Ambil path dasar
set ROOT=%~dp0
set PYPATH="%ROOT%python_embed\python.exe"
set SCRIPT="%ROOT%Backup_Guard_Gui.py"

REM Set path TCL supaya tkinter bisa jalan
set TCL_LIBRARY=%ROOT%python_embed\tcl\tcl8.6

echo [*] Menjalankan Backup Guard GUI...
%PYPATH% %SCRIPT%

pause