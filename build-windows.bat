@echo off
echo Capitalize pyinstaller as PyInstaller if you're having issues, I guess
pyinstaller --onefile --noconsole --add-data="icon.png:." --target-arch=64bit --hidden-import ttkbootstrap --hidden-import obs-websocket-py --hidden-import PIL._tkinter_finder --hidden-import github --icon=icon.ico pychoss.py
