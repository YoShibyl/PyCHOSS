#!/bin/bash
pyinstaller --onefile --noconsole --add-data="icon.png:." --hidden-import PIL._tkinter_finder pychoss.py
