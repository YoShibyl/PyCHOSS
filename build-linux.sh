#!/bin/bash
pyinstaller --onefile --noconsole --hidden-import PIL._tkinter_finder pychoss.py
