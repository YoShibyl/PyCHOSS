# Python Clone Hero OBS Scene Switcher (PyCHOSS)
This is a rewrite/port of [CHOSS](https://github.com/YoShibyl/CHOSS), an automatic OBS scene switching tool for [Clone Hero](https://clonehero.net/) / [YARG](https://yarg.in/) players.  It works by detecting changes in the `currentsong.txt` file of the game, which lets the program determine when to switch to/from the specified scenes via [OBS websockets](https://github.com/Elektordi/obs-websocket-py).

Compiled executables of PyCHOSS will be available in [Releases](https://github.com/YoShibyl/PyCHOSS/releases).

## Requirements
- Windows or Linux (tested on Arch Linux with KDE Plasma)
- [OBS](https://obsproject.com) v28 or newer, with at least two scenes set up (one for gameplay, and one for menus)
- [Clone Hero](https://clonehero.net) or [YARG](https://yarg.in)

## Setup
In order to use CHOSS, you need to configure your OBS websocket server.

### OBS setup
1) Click **Tools > WebSocket Server Settings**.  Make sure **Enable WebSocket Server** is checked.
2) ***It is strongly recommended to use a password for authentication, preferably one that is generated.***  To do this, check the **Enable Authentication** box, click **Generate Password**, and then click **Apply**.  You only need to do this once.
3) Click the **Show Connect Info** button, and copy the password that was generated.  You'll need this to connect PyCHOSS to the websocket server.
4) *(optional)* If connecting to a WebSocket on a different PC running OBS, you'll need the local IP address of that PC.  Otherwise, leave the IP in PyCHOSS as `localhost`, `127.0.0.1`, or `0.0.0.0`

### PyCHOSS setup
1) Paste the password for your OBS websocket in the password box by selecting it and pressing Ctrl+V (right-clicking will *not* work)
2) Select which game you're playing via the tabs in the upper-left corner of the window.  If the `currentsong.txt` file isn't found, you might need to browse for it manually.
3) Change the scene names according to the scene names you have in OBS.  **Note that the scene names are case-sensitive!**
4) Click **Save configuration** to save your settings
5) Click the **Connect** button, and you should be all set!
