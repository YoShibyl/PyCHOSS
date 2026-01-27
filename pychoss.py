#!/usr/bin/env python
import os
import sys
import re
import configparser
import struct
import time
import threading
import tkinter
from tkinter import *
import tkinter.font as font
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.widgets.tableview import Tableview
from ttkbootstrap.constants import *
from PIL import ImageTk, Image
from obswebsocket import obsws, requests

appVersion = "v1.0.0"  # Change before release

print("Python Clone Hero OBS Scene Switcher (PyCHOSS) " + appVersion)
print("Created by Yoshibyl (Yoshi) :: https://github.com/Yoshibyl/")

## config.ini setup
appcfg = configparser.ConfigParser(allow_no_value=True, strict=False, interpolation=None)

defaultGeneral = {
    "app_theme":"Dark",
    "ip_address":"localhost",
    "port":"4455",
    "password":""
}
defaultCloneHero = {
    "currentsong_path": os.path.expanduser("~/.clonehero/currentsong.txt"),
    "game_scene":"CH Gameplay",
    "menu_scene":"CH Menu"
}
defaultYarg = {
    "currentsong_path": os.path.expanduser("~/.config/unity3d/YARC/YARG/release/currentSong.txt"),
    "game_scene":"YARG Gameplay",
    "menu_scene":"YARG Menu"
}
defaultYargNightly = {
    "currentsong_path": os.path.expanduser("~/.config/unity3d/YARC/YARG/nightly/currentSong.txt"),
    "game_scene":"YARG Gameplay",
    "menu_scene":"YARG Menu"
}

if sys.platform == "win32":
    defaultCloneHero["currentsong_path"] = os.path.expanduser("~\\OneDrive\\Documents\\Clone Hero\\currentsong.txt")
    defaultYarg["currentsong_path"] = os.path.expanduser("~\\AppData\\LocalLow\\YARC\\YARG\\release\\currentSong.txt")
    defaultYargNightly["currentsong_path"] = os.path.expanduser("~\\AppData\\LocalLow\\YARC\\YARG\\nightly\\currentSong.txt")

def update_config(reload=False):
    global appcfg
    if not os.path.exists("config.ini"):
        appcfg["general"] = defaultGeneral
        appcfg["clonehero"] = defaultCloneHero
        appcfg["yarg"] = defaultYarg
        appcfg["yarg_nightly"] = defaultYargNightly
    if reload:
        appcfg.read("config.ini")
        # General
        if "general" not in appcfg.sections():
            appcfg["general"] = defaultGeneral
        for k in defaultGeneral.keys():
            if k not in appcfg["general"].keys(): appcfg["general"][k] = defaultGeneral[k]
        # Clone Hero
        if "clonehero" not in appcfg.sections():
            appcfg["clonehero"] = defaultCloneHero
        for k in defaultCloneHero.keys():
            if k not in appcfg["clonehero"].keys(): appcfg["clonehero"][k] = defaultCloneHero[k]
        # YARG Stable and Nightly
        if "yarg" not in appcfg.sections():
            appcfg["yarg"] = defaultYarg
        for k in defaultYarg.keys():
            if k not in appcfg["yarg"].keys(): appcfg["yarg"][k] = defaultYarg[k]
        if "yarg_nightly" not in appcfg.sections():
            appcfg["yarg_nightly"] = defaultYargNightly
        for k in defaultYargNightly.keys():
            if k not in appcfg["yarg_nightly"].keys(): appcfg["yarg_nightly"][k] = defaultYargNightly[k]
    with open("config.ini", "w") as cfgfile:
        appcfg.write(cfgfile)
        cfgfile.close()
## read the config.ini; create/populate if necessary
update_config(True)

## Functions and stuff
def fixstring(inputstr=""):  # not sure if we'll need this tbh
    CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    fixedStr = ''.join(c if c <= '\uffff' else ''.join(chr(x) for x in struct.unpack('>2H', c.encode('utf-8'))) for c in inputstr)
    fixedStr = re.sub(CLEANR, "", fixedStr)
    return fixedStr
# connect/disconnect button click
def connectBtnClick(event=None):
    global wsThread
    if connStatusBool == False:
        connBtnTxtVar.set("Connecting...")
        connectBtn.config(state="disabled")
        for child in nbFrameCH.winfo_children():
            child.config(state="disabled")
        for child in nbFrameYARG.winfo_children():
            child.config(state="disabled")
        for child in nbFrameYARGnightly.winfo_children():
            child.config(state="disabled")
        wsThread = threading.Thread(target=wsConnectionWorker)
        wsThread.start()
    else:
        client.disconnect()
        connStatusTxt.set("Not connected")
        connStatusLbl.config(bootstyle="danger")
        connBtnTxtVar.set("Connect")
        connectBtn.config(state="enabled")
        for child in nbFrameCH.winfo_children():
            child.config(state="enabled")
        for child in nbFrameYARG.winfo_children():
            child.config(state="enabled")

def onConnect(sock):
    global connStatusBool
    connStatusBool = True
    connStatusTxt.set("Connected (%s)" % whichTabMode)
    connStatusLbl.config(bootstyle="success")
    connBtnTxtVar.set("Disconnect")
    connectBtn.config(state="enabled")
def onDisconnect(sock):
    global connStatusBool
    if exiting == False:
        connStatusBool = False
        connStatusTxt.set("Not connected")
        connStatusLbl.config(bootstyle="danger")
        connBtnTxtVar.set("Connect")
        connectBtn.config(state="enabled")
        for child in nbFrameCH.winfo_children():
            child.config(state="enabled")
        for child in nbFrameYARG.winfo_children():
            child.config(state="enabled")
        for child in nbFrameYARGnightly.winfo_children():
            child.config(state="enabled")
# websocket thread thing
def wsConnectionWorker():
    global client
    global whichTabMode
    global connStatusBool
    ip = ipVar.get()
    port = portVar.get()
    pw = passVar.get()
    csPath = ""
    gameScene = ""
    menuScene = ""
    whichTabMode = nb.tab(nb.select(), "text")
    if whichTabMode == "Clone Hero":
        csPath = currSongTxtVar_CH.get()
        gameScene = gameSceneTxtVar_CH.get()
        menuScene = menuSceneTxtVar_CH.get()
    elif whichTabMode == "YARG stable":
        csPath = currSongTxtVar_YARG.get()
        gameScene = gameSceneTxtVar_YARG.get()
        menuScene = menuSceneTxtVar_YARG.get()
    elif whichTabMode == "YARG nightly":
        csPath = currSongTxtVar_YARGnightly.get()
        gameScene = gameSceneTxtVar_YARGnightly.get()
        menuScene = menuSceneTxtVar_YARGnightly.get()
    if os.path.isfile(csPath):
        client = obsws(ip, port, pw, on_connect=onConnect, on_disconnect=onDisconnect, timeout=5)
        try:
            client.connect()
            connStatusBool = True
        except:
            connStatusBool = False
            connStatusLbl.config(bootstyle="danger")
            connStatusTxt.set("Connection failed.  Check OBS websocket settings and/or password")
            connBtnTxtVar.set("Connect")
            connectBtn.config(state="enabled")
            connBtnTxtVar.set("Connect")
            for child in nbFrameCH.winfo_children():
                child.config(state="enabled")
            for child in nbFrameYARG.winfo_children():
                child.config(state="enabled")
            for child in nbFrameYARGnightly.winfo_children():
                child.config(state="enabled")
        if connStatusBool == True:
            old_size = os.path.getsize(csPath)
            while connStatusBool == True:
                new_size = os.path.getsize(csPath)
                if old_size != new_size:
                    if new_size == 0:  # menu scene
                        # time.sleep(0.25)
                        if os.path.getsize(csPath) == 0:
                            client.call(requests.SetCurrentProgramScene(sceneName=menuScene))
                    else:  # gameplay scene
                        # time.sleep(0.25)
                        client.call(requests.SetCurrentProgramScene(sceneName=gameScene))
                    old_size = new_size
                time.sleep(0.1)
    else:
        connStatusLbl.config(bootstyle="warning")
        connStatusTxt.set("currentsong.txt not found!")
        connBtnTxtVar.set("Connect")
        connectBtn.config(state="enabled")
        for child in nbFrameCH.winfo_children():
            child.config(state="enabled")
        for child in nbFrameYARG.winfo_children():
            child.config(state="enabled")
        for child in nbFrameYARGnightly.winfo_children():
            child.config(state="enabled")
# application close handler
def onCloseWindow(event=None):
    global client
    global connStatusBool
    if connStatusBool:
        if messagebox.askokcancel("Warning", "There is an active connection to the OBS websocket.  Are you sure you want to exit?", icon="warning"):
            try:
                client.disconnect()
            except:
                print("Error trying to disconnect websocket")
            update_config()
            root.destroy()
            exit()
    else:
        update_config()
        root.destroy()
        exit()
# save config button click
def saveBtnClick(event=None):
    appcfg["general"]["ip_address"] = ipVar.get()
    appcfg["general"]["port"] = portVar.get()
    appcfg["general"]["password"] = passVar.get()
    appcfg["clonehero"]["currentsong_path"] = currSongTxtVar_CH.get()
    appcfg["yarg"]["currentsong_path"] = currSongTxtVar_YARG.get()
    appcfg["yarg_nightly"]["currentsong_path"] = currSongTxtVar_YARGnightly.get()
    appcfg["clonehero"]["game_scene"] = gameSceneTxtVar_CH.get()
    appcfg["clonehero"]["menu_scene"] = menuSceneTxtVar_CH.get()
    appcfg["yarg"]["game_scene"] = gameSceneTxtVar_YARG.get()
    appcfg["yarg"]["menu_scene"] = menuSceneTxtVar_YARG.get()
    appcfg["yarg_nightly"]["game_scene"] = gameSceneTxtVar_YARGnightly.get()
    appcfg["yarg_nightly"]["menu_scene"] = menuSceneTxtVar_YARGnightly.get()
    update_config()
# theme select handler
def updateTheme(event=None):
    themeOption.config(width=5)
    themeVal = themeTxtVar.get()
    if themeVal == "Dark":
        root.style.theme_use("darkly")
    elif themeVal == "Black":
        root.style.theme_use("cyborg")
    elif themeVal == "Light":
        root.style.theme_use("litera")
    appcfg["general"]["app_theme"] = themeVal
# "Browse currentsong.txt" button handlers
def browseForTxt_CH(event=None):
    global appcfg
    startDir = appcfg["clonehero"]["currentsong_path"].replace("currentsong.txt", "")
    filepath = filedialog.askopenfilename(filetypes=[("Text file","*.txt")], initialdir=startDir)
    if len(filepath) > 0:
        currSongTxtVar_CH.set(filepath)
def browseForTxt_YARG(event=None):
    global appcfg
    startDir = appcfg["yarg"]["currentsong_path"].replace("currentSong.txt", "")
    filepath = filedialog.askopenfilename(filetypes=[("Text file","*.txt")], initialdir=startDir)
    if len(filepath) > 0:
        currSongTxtVar_YARG.set(filepath)
def browseForTxt_YARGnightly(event=None):
    global appcfg
    startDir = appcfg["yarg_nightly"]["currentsong_path"].replace("currentSong.txt", "")
    filepath = filedialog.askopenfilename(filetypes=[("Text file","*.txt")], initialdir=startDir)
    if len(filepath) > 0:
        currSongTxtVar_YARGnightly.set(filepath)

## initialize main window and stuff
root = tb.Window(title="PyCHOSS " + appVersion, themename="darkly")
root.protocol("WM_DELETE_WINDOW", onCloseWindow)

## variables
themeTxtVar = tkinter.StringVar(root, appcfg["general"]["app_theme"])
connStatusBool = False
connStatusTxt = tkinter.StringVar(root, "Not connected")
ipVar = tkinter.StringVar(root, appcfg["general"]["ip_address"])
portVar = tkinter.StringVar(root, appcfg["general"]["port"])
passVar = tkinter.StringVar(root, appcfg["general"]["password"])
connBtnTxtVar = tkinter.StringVar(root, "Connect")
currSongTxtVar_CH = tkinter.StringVar(root, appcfg["clonehero"]["currentsong_path"])
currSongTxtVar_YARG = tkinter.StringVar(root, appcfg["yarg"]["currentsong_path"])
currSongTxtVar_YARGnightly = tkinter.StringVar(root, appcfg["yarg_nightly"]["currentsong_path"])
gameSceneTxtVar_CH = tkinter.StringVar(root, appcfg["clonehero"]["game_scene"])
menuSceneTxtVar_CH = tkinter.StringVar(root, appcfg["clonehero"]["menu_scene"])
gameSceneTxtVar_YARG = tkinter.StringVar(root, appcfg["yarg"]["game_scene"])
menuSceneTxtVar_YARG = tkinter.StringVar(root, appcfg["yarg"]["menu_scene"])
gameSceneTxtVar_YARGnightly = tkinter.StringVar(root, appcfg["yarg_nightly"]["game_scene"])
menuSceneTxtVar_YARGnightly = tkinter.StringVar(root, appcfg["yarg_nightly"]["menu_scene"])
exiting = False

whichTabMode = "Clone Hero"

## right-click menus
# later?

## Layout stuff
# Scene Switcher settings
nb = ttk.Notebook(root, padding=0, height=140)
# Clone Hero
nbFrameCH = ttk.Frame(nb, padding=10)
currSongBrowseCH = ttk.Button(nbFrameCH, text="Browse currentsong.txt", command=browseForTxt_CH).grid(row=0,column=0,pady=2)
currSongEntryCH = ttk.Entry(nbFrameCH, textvariable=currSongTxtVar_CH,width=30).grid(row=0,column=1,pady=2)
lblGameSceneCH = ttk.Label(nbFrameCH, text="Gameplay Scene: ").grid(row=1,column=0,padx=10,pady=2,sticky=W)
gameSceneEntryCH = ttk.Entry(nbFrameCH, textvariable=gameSceneTxtVar_CH, width=30).grid(row=1,column=1,padx=10,pady=2,sticky=E)
lblMenuSceneCH = ttk.Label(nbFrameCH, text="Menu Scene: ").grid(row=2,column=0,padx=10,pady=2,sticky=W)
menuSceneEntryCH = ttk.Entry(nbFrameCH, textvariable=menuSceneTxtVar_CH, width=30).grid(row=2,column=1,padx=10,pady=2,sticky=E)
# YARG stable
nbFrameYARG = ttk.Frame(nb, padding=10)
currSongBrowseYARG = ttk.Button(nbFrameYARG, text="Browse currentSong.txt", command=browseForTxt_YARG).grid(row=0,column=0,pady=2)
currSongEntryYARG = ttk.Entry(nbFrameYARG, textvariable=currSongTxtVar_YARG,width=30).grid(row=0,column=1,pady=2)
lblGameSceneYARG = ttk.Label(nbFrameYARG, text="Gameplay Scene: ").grid(row=1,column=0,padx=10,pady=2,sticky=W)
gameSceneEntryYARG = ttk.Entry(nbFrameYARG, textvariable=gameSceneTxtVar_YARG, width=30).grid(row=1,column=1,padx=10,pady=2,sticky=E)
lblMenuSceneYARG = ttk.Label(nbFrameYARG, text="Menu Scene: ").grid(row=2,column=0,padx=10,pady=2,sticky=W)
menuSceneEntryYARG = ttk.Entry(nbFrameYARG, textvariable=menuSceneTxtVar_YARG, width=30).grid(row=2,column=1,padx=10,pady=2,sticky=E)
# YARG nightly
nbFrameYARGnightly = ttk.Frame(nb, padding=10)
currSongBrowseYARG = ttk.Button(nbFrameYARGnightly, text="Browse currentSong.txt", command=browseForTxt_YARGnightly).grid(row=0,column=0,pady=2)
currSongEntryYARGnightly = ttk.Entry(nbFrameYARGnightly, textvariable=currSongTxtVar_YARGnightly,width=30).grid(row=0,column=1,pady=2)
lblGameSceneYARGnightly = ttk.Label(nbFrameYARGnightly, text="Gameplay Scene: ").grid(row=1,column=0,padx=10,pady=2,sticky=W)
gameSceneEntryYARGnightly = ttk.Entry(nbFrameYARGnightly, textvariable=gameSceneTxtVar_YARGnightly, width=30).grid(row=1,column=1,padx=10,pady=2,sticky=E)
lblMenuSceneYARGnightly = ttk.Label(nbFrameYARGnightly, text="Menu Scene: ").grid(row=2,column=0,padx=10,pady=2,sticky=W)
menuSceneEntryYARGnightly = ttk.Entry(nbFrameYARGnightly, textvariable=menuSceneTxtVar_YARGnightly, width=30).grid(row=2,column=1,padx=10,pady=2,sticky=E)
nb.add(nbFrameCH, text="Clone Hero")
nb.add(nbFrameYARG, text="YARG stable")
nb.add(nbFrameYARGnightly, text="YARG nightly")

nb.grid(row=0,column=0,rowspan=4, padx=10, pady=10, sticky=NW)

# Websocket Settings frame
wsFrame = ttk.Labelframe(root, text="Websocket Connection", width=370, height=180, padding=10)
ipLabel = ttk.Label(wsFrame, text=" IP Address:")
ipEntry = ttk.Entry(wsFrame, textvariable=ipVar, width=16)
portLabel = ttk.Label(wsFrame, text="  Port:")
portEntry = ttk.Entry(wsFrame, textvariable=portVar, width=6)
passLabel = ttk.Label(wsFrame, text="Password:")
passEntry = ttk.Entry(wsFrame, textvariable=passVar, show="•", width=34)
ipLabel.grid(row=0, column=0, padx=10, pady=2, sticky=E)
ipEntry.grid(row=0, column=1, padx=10, pady=2, sticky=E)
portLabel.grid(row=0,column=2, padx=10, pady=2, sticky=E)
portEntry.grid(row=0, column=3, padx=10, pady=2, sticky=E)
passLabel.grid(row=1, column=0, padx=10, pady=2, sticky=E)
passEntry.grid(row=1, column=1, columnspan=3, padx=10, pady=2, sticky=W)
wsFrame.grid(row=0, column=1, padx=10, pady=10, sticky=NE)

# Case-sensitivity notice for scene names
caseSensitiveInfoLbl = tb.Label(root, text="Note: OBS scene names are case-sensitive!")
caseSensitiveInfoLbl.grid(row=2, column=0)

# Theme select
themeFrame = tkinter.Frame(root, padx=10, pady=10)
themeLbl = tb.Label(themeFrame, text="Application theme:  ")
themeOption = tb.OptionMenu(themeFrame, themeTxtVar, "","Dark","Black","Light", command=updateTheme)
updateTheme()
themeLbl.grid(row=0,column=0,sticky=W)
themeOption.grid(row=0,column=1,sticky=W)
themeFrame.grid(row=3, column=0,sticky=W)

# Save config button
saveBtn = ttk.Button(root, text="Save configuration", width=50, command=saveBtnClick)
saveBtn.grid(row=1, column=1, ipady=5, pady=10)
# Connection status indicator
connStatusLbl = tb.Label(root, textvariable=connStatusTxt, bootstyle="danger")
connStatusLbl.grid(row=2, column=1)
# Connect button
connectBtn = tb.Button(root, textvariable=connBtnTxtVar, width=50, command=connectBtnClick, bootstyle="info")
connectBtn.grid(row=3, column=1, ipady=18, pady=10)

# set things up
root.geometry()
root.resizable(False,False)
client = obsws()

# main loop
root.mainloop()
