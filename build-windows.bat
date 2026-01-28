@echo off
echo Capitalize pyinstaller as PyInstaller if you're having issues, I guess
pyinstaller --onefile --noconsole --hidden-import ttkbootstrap --hidden-import obs-websocket-py --hidden-import pygithub pychoss.py
