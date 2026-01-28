#!/usr/bin/env python
import os
import sys
import configparser
import time
import threading
import webbrowser
import tkinter
from tkinter import *
import tkinter.font as font
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.validation import *
from obswebsocket import obsws, requests
from github import Github

appVersion = "v1.1.0"
latestRelease = appVersion
repoURL = "https://github.com/Yoshibyl/PyCHOSS"

print("Python Clone Hero OBS Scene Switcher (PyCHOSS) " + appVersion)
print("Created by Yoshibyl (Yoshi) :: https://github.com/Yoshibyl/")

## Update checker stuff
updateAvailable = False
isChecking = False
txtTimer = 0.0
def updateBtnTimerStart():  # This should only be called ONCE during execution!
    btnBgThread = threading.Thread(target=timerTickLoop)
    btnBgThread.start()
def checkGithubForUpdate(event=None):
    global updateAvailable
    global isChecking
    if not updateAvailable:
        if txtTimer == 0.0:
            isChecking = True
            checkerThread = threading.Thread(target=updateCheckWorker)
            checkerThread.start()
            updateBtn.config(state="disabled", bootstyle="primary")
            updateBtnTxtVar.set("Checking...")
    else:
        updatePrompt = messagebox.askyesno(title="PyCHOSS Update", message="Download PyCHOSS " + latestRelease + "?\n\nClicking \"Yes\" will open GitHub in your default web browser.")
        if updatePrompt:
            webbrowser.open_new_tab(repoURL + "/releases/tag/" + latestRelease)
def updateCheckWorker():
    global updateAvailable
    global latestRelease
    global txtTimer
    global isChecking
    global updateChannel
    global appVersion
    txtTimer = 67  # haha six seven (please laugh)
    print("\nChecking GitHub for update...")
    try:
        gHub = Github()
        gTags = gHub.get_repo("Yoshibyl/PyCHOSS").get_tags()
        tags = []
        channel = "stable"
        try:
            channel = updateChannel.get()
        except: pass
        updateAvailable = False
        for gTag in gTags:
            tag = gTag.name.lower()
            tags.append(tag)
            if tag != appVersion:
                if "pre" not in channel.lower() and "pre" in tag:
                    tags.remove(tag)
        latestRelease = tags[0]
        if appVersion in tags and tags[0] != appVersion:  # only count latest version if current version is on github
            isChecking = False
            print("Version %s found: " % latestRelease)
            print(repoURL + "/releases/tag/" + latestRelease)
            updateAvailable = True
        else:
            print("No update available at this time (%s)" % appVersion)
            updateAvailable = False
        try:
            if updateAvailable:
                updateBtnTxtVar.set("Update available: " + latestRelease)
                updateBtn.config(state="enabled",bootstyle="success")
                txtTimer = -1 # disable timer for resetting button text because update was found
            else:
                updateBtnTxtVar.set("On the latest version: %s" % appVersion)
                updateBtn.config(state="enabled",bootstyle="info")
                txtTimer = 6
        except: pass
    except:
        print("An error occurred while trying to check GitHub")
        updateAvailable = False
        try:
            txtTimer = 6
            updateBtnTxtVar.set("Can't connect to GitHub")
            updateBtn.config(state="enabled",bootstyle="danger")
        except: pass
    isChecking = False
def timerTickLoop():
    global exiting
    global txtTimer
    if appcfg["general"]["auto_check_update"].lower() == "true":
        checkGithubForUpdate()
    while exiting == False and txtTimer > -1:
        time.sleep(0.1)
        if txtTimer > 0:
            txtTimer -= 0.1
            if txtTimer < 0: txtTimer = 0
        if txtTimer == 0.0:
            try:
                updateBtnTxtVar.set("Check for update")
            except: pass

## config.ini setup
appcfg = configparser.ConfigParser(allow_no_value=True, strict=False, interpolation=None)
defaultChannel = "Stable"
if "pre" in appVersion: defaultChannel = "PreRelease"
defaultGeneral = {
    "app_theme": "Dark",
    "ip_address": "localhost",
    "port": "4455",
    "password": "",
    "auto_check_update": "true",
    "update_channel": defaultChannel,  # Changes to "Stable" on release, or "PreRelease" in pre-release builds
    "cooldown_seconds": "1.0"
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

# connect/disconnect button click
def connectBtnClick(event=None):
    global cooldownTxtVar
    global cooldownSpin
    global cooldown
    global wsThread
    fixCooldownTxt()
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
    global cooldown
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
            connStatusTxt.set("Connection failed.  Check OBS websocket settings/password")
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
                    cooldown = cooldownChangeHandler()
                    if new_size == 0:  # menu scene
                        client.call(requests.SetCurrentProgramScene(sceneName=menuScene))
                        if cooldown > 0: time.sleep(cooldown)
                    else:  # gameplay scene
                        client.call(requests.SetCurrentProgramScene(sceneName=gameScene))
                        if cooldown > 0: time.sleep(cooldown)
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
    global exiting
    global cooldownTxtVar
    global cooldownSpin
    global cooldown
    fixCooldownTxt()
    if connStatusBool == True:
        if messagebox.askyesno("Warning", "There is an active connection to the OBS websocket.  Are you sure you want to exit?", icon="warning"):
            try:
                client.disconnect()
            except:
                print("Error trying to disconnect websocket")
            exiting = True
            saveBtnClick()
            root.destroy()
            sys.exit()
    else:
        exiting = True
        saveBtnClick()
        root.destroy()
        sys.exit()
# save config button click
def saveBtnClick(event=None):
    global cooldownTxtVar
    global cooldownSpin
    global cooldown
    global appcfg
    fixCooldownTxt()
    appcfg["general"]["ip_address"] = ipVar.get()
    appcfg["general"]["port"] = portVar.get()
    appcfg["general"]["password"] = passVar.get()
    appcfg["general"]["auto_check_update"] = "true" if autoCheckUpdateVar.get() == True else "false"
    appcfg["general"]["update_channel"] = updateChannel.get()
    appcfg["general"]["cooldown_seconds"] = cooldownTxtVar.get()
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
# update channel select handler
def changeUpdateChannel(event=None):
    appcfg["general"]["update_channel"] = updateChannel.get()
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
# cooldown spinbox validation
def isStringFloat(string_ = ""):
    try:
        float_ = float(string_)
    except:
        return False
    return True
# cooldown changed
def cooldownChangeHandler(event=None):
    global cooldown
    global cooldownTxtVar
    fixCooldownTxt()
    if isStringFloat(cooldownTxtVar.get()):
        cooldown = float(cooldownTxtVar.get())
        if cooldown > 30.0: cooldown = 30.0
        elif cooldown < 0.0: cooldown = 0.0
        return cooldown
# cooldown validation
def fixCooldownTxt(a=None,b=None,c=None):
    global cooldownTxtVar
    global cooldown
    cooldownStr = cooldownTxtVar.get().replace("-","")
    if isStringFloat(cooldownStr) == False:
        cooldownStr = "1.0"
        cooldown = 1.0
        cooldownTxtVar.set(cooldownStr)
    else:
        cooldown = float(cooldownStr)
        if cooldown > 30.0: cooldown = 30.0
        elif cooldown < 0.0: cooldown = 0.0
        cooldownStr = f"{cooldown:0.1f}"
        cooldownTxtVar.set(cooldownStr)

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
updateBtnTxtVar = tkinter.StringVar(root, "Check for update")
exiting = False
autoCheckUpdateVar = tkinter.BooleanVar(root, appcfg["general"]["auto_check_update"] == "true")
updateChannel = tkinter.StringVar(root, appcfg["general"]["update_channel"])
cooldownTxtVar = tkinter.StringVar(root, appcfg["general"]["cooldown_seconds"])
cooldown = 0.0
if isStringFloat(cooldownTxtVar.get()):
    cooldown = float(cooldownTxtVar.get())
fixCooldownTxt()

whichTabMode = "Clone Hero"

## Layout stuff
# Scene Switcher settings
nb = ttk.Notebook(root, padding=0, height=140)
# Clone Hero
nbFrameCH = ttk.Frame(nb, padding=10)
currSongBrowseCH = ttk.Button(nbFrameCH, text="Browse currentsong.txt", command=browseForTxt_CH).grid(row=0,column=0,pady=2)
currSongEntryCH = ttk.Entry(nbFrameCH, textvariable=currSongTxtVar_CH,width=35).grid(row=0,column=1,pady=2)
lblGameSceneCH = ttk.Label(nbFrameCH, text="Gameplay Scene: ").grid(row=1,column=0,padx=10,pady=2,sticky=W)
gameSceneEntryCH = ttk.Entry(nbFrameCH, textvariable=gameSceneTxtVar_CH, width=35).grid(row=1,column=1,padx=10,pady=2,sticky=E)
lblMenuSceneCH = ttk.Label(nbFrameCH, text="Menu Scene: ").grid(row=2,column=0,padx=10,pady=2,sticky=W)
menuSceneEntryCH = ttk.Entry(nbFrameCH, textvariable=menuSceneTxtVar_CH, width=35).grid(row=2,column=1,padx=10,pady=2,sticky=E)
# YARG stable
nbFrameYARG = ttk.Frame(nb, padding=10)
currSongBrowseYARG = ttk.Button(nbFrameYARG, text="Browse currentSong.txt", command=browseForTxt_YARG).grid(row=0,column=0,pady=2)
currSongEntryYARG = ttk.Entry(nbFrameYARG, textvariable=currSongTxtVar_YARG,width=35).grid(row=0,column=1,pady=2)
lblGameSceneYARG = ttk.Label(nbFrameYARG, text="Gameplay Scene: ").grid(row=1,column=0,padx=10,pady=2,sticky=W)
gameSceneEntryYARG = ttk.Entry(nbFrameYARG, textvariable=gameSceneTxtVar_YARG, width=35).grid(row=1,column=1,padx=10,pady=2,sticky=E)
lblMenuSceneYARG = ttk.Label(nbFrameYARG, text="Menu Scene: ").grid(row=2,column=0,padx=10,pady=2,sticky=W)
menuSceneEntryYARG = ttk.Entry(nbFrameYARG, textvariable=menuSceneTxtVar_YARG, width=35).grid(row=2,column=1,padx=10,pady=2,sticky=E)
# YARG nightly
nbFrameYARGnightly = ttk.Frame(nb, padding=10)
currSongBrowseYARG = ttk.Button(nbFrameYARGnightly, text="Browse currentSong.txt", command=browseForTxt_YARGnightly).grid(row=0,column=0,pady=2)
currSongEntryYARGnightly = ttk.Entry(nbFrameYARGnightly, textvariable=currSongTxtVar_YARGnightly,width=35).grid(row=0,column=1,pady=2)
lblGameSceneYARGnightly = ttk.Label(nbFrameYARGnightly, text="Gameplay Scene: ").grid(row=1,column=0,padx=10,pady=2,sticky=W)
gameSceneEntryYARGnightly = ttk.Entry(nbFrameYARGnightly, textvariable=gameSceneTxtVar_YARGnightly, width=35).grid(row=1,column=1,padx=10,pady=2,sticky=E)
lblMenuSceneYARGnightly = ttk.Label(nbFrameYARGnightly, text="Menu Scene: ").grid(row=2,column=0,padx=10,pady=2,sticky=W)
menuSceneEntryYARGnightly = ttk.Entry(nbFrameYARGnightly, textvariable=menuSceneTxtVar_YARGnightly, width=35).grid(row=2,column=1,padx=10,pady=2,sticky=E)
nb.add(nbFrameCH, text="Clone Hero")
nb.add(nbFrameYARG, text="YARG stable")
nb.add(nbFrameYARGnightly, text="YARG nightly")

nb.grid(row=0,column=0,rowspan=2, padx=10, pady=10, sticky=NW)

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

# Theme select and other settings
genSettingsFrame = tkinter.Frame(root, padx=10, pady=10)
themeLbl = tb.Label(genSettingsFrame, text=" App theme: ")
themeOption = tb.OptionMenu(genSettingsFrame, themeTxtVar, "","Dark","Black","Light", command=updateTheme)
updateTheme()
themeLbl.grid(row=0,column=0,sticky=W)
themeOption.grid(row=0,column=1,sticky=W, padx=10,pady=10)
cooldownLbl = tb.Label(genSettingsFrame, text="  Scene cooldown (sec): ").grid(row=0,column=2,columnspan=2,sticky=W)
cooldownSpin = ttk.Spinbox(genSettingsFrame, increment=0.1, from_=0, to=30, command=cooldownChangeHandler, validatecommand=isStringFloat, textvariable=cooldownTxtVar, width=4)
# cooldownTxtVar.trace("w", fixCooldownTxt)
cooldownSpin.grid(row=0,column=4,sticky=W)
updateBtn = tb.Button(genSettingsFrame, textvariable=updateBtnTxtVar, command=checkGithubForUpdate, width=29)
updateBtn.grid(row=1,column=0,columnspan=3,sticky=SW)
autoUpdateToggle = tb.Checkbutton(genSettingsFrame, variable=autoCheckUpdateVar, text="Auto-check: ", bootstyle="round-toggle")
autoUpdateToggle.grid(row=1,column=3,padx=5)
updChanOption = tb.OptionMenu(genSettingsFrame, updateChannel, "","Stable","PreRelease", command=changeUpdateChannel)
updChanOption.grid(row=1,column=4)
genSettingsFrame.grid(row=3, column=0, rowspan=2, sticky=SW)

# Save config button
saveBtn = ttk.Button(root, text="Save configuration", width=50, command=saveBtnClick)
saveBtn.grid(row=1, column=1, ipady=5, pady=10)
# Connection status indicator
connStatusLbl = tb.Label(root, textvariable=connStatusTxt, bootstyle="danger")
connStatusLbl.grid(row=3, column=1, sticky=S)
# Connect button
connectBtn = tb.Button(root, textvariable=connBtnTxtVar, width=50, command=connectBtnClick, bootstyle="info")
connectBtn.grid(row=4, column=1, ipady=18, pady=10)

# set things up
root.geometry()
root.resizable(False,False)
client = obsws()
root.after(0, updateBtnTimerStart)

# main loop
root.mainloop()
