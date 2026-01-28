@echo off
echo Capitalize pyinstaller as PyInstaller if you're having issues, I guess
pyinstaller --onefile --noconsole --target-arch=64bit --hidden-import ttkbootstrap --hidden-import obs-websocket-py --hidden-import PIL._tkinter_finder --hidden-import pygithub --icon=icon.ico pychoss.py
