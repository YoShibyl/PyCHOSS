# Python Clone Hero OBS Scene Switcher (PyCHOSS)
This is a rewrite/port of [CHOSS](https://github.com/YoShibyl/CHOSS), an automatic OBS scene switching tool for [Clone Hero](https://clonehero.net/) / [YARG](https://yarg.in/) players.  It works by detecting changes in the `currentsong.txt` file of the game, which lets the program determine when to switch to/from the specified scenes via [OBS websockets](https://github.com/Elektordi/obs-websocket-py).

## Screenshots (v1.2.0)
Taken on Arch Linux with KDE Plasma running on a Steam Deck
<details open>
  <summary>Dark theme</summary>
  <img width="998" height="387" alt="image" src="https://github.com/user-attachments/assets/2688872a-1ead-4068-aed7-7b7590936751" />
</details>
<details>
  <summary>Black theme</summary>
  <img width="998" height="387" alt="image" src="https://github.com/user-attachments/assets/2cb01789-d12c-4f9d-ba3e-37e79f8c285a" />
</details>
<details>
  <summary>Light theme</summary>
  <img width="998" height="387" alt="image" src="https://github.com/user-attachments/assets/eb10de17-e320-44bd-b7f2-25430c3eda98" />
</details>

## Requirements
- Windows or Linux (tested on Arch Linux with KDE Plasma, as well as Windows 11)
- [OBS Studio](https://obsproject.com) v28 or newer, with at least two scenes set up (one for gameplay, and one for menus)
- [Clone Hero](https://clonehero.net) or [YARG](https://yarg.in)

## Setup
Download your platform's build of PyCHOSS from [Releases](https://github.com/YoShibyl/PyCHOSS/releases) to its own folder.

In order to use PyCHOSS, you need to configure your OBS websocket server.

### OBS setup
1) Click **Tools > WebSocket Server Settings**.  Make sure **Enable WebSocket Server** is checked.
2) ***It is strongly recommended to use a password for authentication, preferably one that is generated.***  To do this, check the **Enable Authentication** box, click **Generate Password**, and then click **Apply**.  You only need to do this once.
3) Click the **Show Connect Info** button, and copy the password that was generated.  You'll need this to connect PyCHOSS to the websocket server.
4) *(optional)* If connecting to a WebSocket on a different PC running OBS, you'll need the local IP address of that PC.  Otherwise, leave the IP in PyCHOSS as `localhost`, `127.0.0.1`, or `0.0.0.0`

> [!IMPORTANT]
> It really goes without saying, but do NOT give your PyCHOSS installation's `config.ini` to ANYONE!
> 
> This is because it contains your OBS websocket server password (if any) in plaintext.

### PyCHOSS setup
1) Paste the password for your OBS websocket in the password box by selecting it and pressing Ctrl+V (right-clicking will *not* work)
2) Select which game you're playing via the tabs in the upper-left corner of the window.  If the `currentsong.txt` file isn't found, you might need to browse for it manually.  Also, when playing Clone Hero, *make sure to enable the **Export Current Song** setting in-game!* (see Clone Hero setup below)
3) Change the scene names according to the scene names you have in OBS.  **Note that the scene names are case-sensitive!**
4) Click **Save configuration** to save your settings
5) Click the **Connect** button, and you should be all set!

### Clone Hero setup
In order for PyCHOSS to switch scenes when playing Clone Hero, the Export Current Song setting must be enabled in settings.

<img width="640" height="360" alt="image" src="https://github.com/user-attachments/assets/c1ead2f0-20f9-4e65-87a7-21cd59e7b0be" />

## Building (using [PyInstaller](https://pyinstaller.org/en/stable/))
First and foremost, download the source code for this repo via the green Code button towards the top of the page when viewing this repo.

### Linux binary (from Linux machine)
1) If you don't have Python and `pip` set up, you'll need the latest version of both installed on your system (instructions vary by distro, so look it up, I guess)

I also recommend setting up a [virtual environment](https://docs.python.org/3/library/venv.html) in the directory of the source code to avoid certain issues.
 - If you do this, you'll need to reactivate the venv every time you open the terminal
 - Example of how to set up a venv:
     1) `python -m venv .venv` (only run this once)
     2) `source .venv/bin/activate` (run this every time you open terminal)

You may also need to install some extra libraries in order to use pyinstaller.  See [this page](https://pyinstaller.org/en/stable/requirements.html#gnu-linux) for more info.

2) Install the required libraries from `requirements.txt`
```
pip install -r requirements.txt
```
3) Install `pyinstaller` via pip.
```
pip install -U pyinstaller
```
4) Finally, to build the binary:
```
pyinstaller --onefile --noconsole --hidden-import PIL._tkinter_finder pychoss.py
```
The parameter `--hidden-import PIL._tkinter_finder` is required in order for the build to run, at least according to my testing.

Once complete, the Linux binary will be located in the `dist` directory.

### Windows executable (from Linux machine via Wine)
If you already have 64-bit Python set up in Wine, skip to step 3.

1) Install [Wine](https://www.winehq.org/).  **Note:** If you're unable to install Wine the traditional way, you might end up resorting to installing Wine's Flatpak from Flathub.  If you somehow are in this situation, **replace `wine` in the commands below with `flatpak run org.winehq.Wine` etc.**
2) Download the 64-bit Windows installer of [Python 3.14.2](https://www.python.org/ftp/python/3.14.2/python-3.14.2-amd64.exe), and run it within Wine:
```
wine ./python-3.14.2-amd64.exe
```
  - **IMPORTANT:** Make sure you do these things when installing Python in Wine:
    - Add Python to PATH
    - Customize installation
    - Install for all users as Administrator
    - Set the Python install folder to `C:\Python3\`
  - To check that Python is installed correctly, run `wine C:/Python3/python.exe --version`
3) Update `pip`, and then install the required libraries from `requirements.txt` as well as `pyinstaller`:
```
wine C:/Python3/python.exe -m pip install --upgrade pip
wine C:/Python3/python.exe -m pip install -r requirements.txt
wine C:/Python3/python.exe -m pip install pyinstaller
```
4) Run the `build-windows.bat` Batch file:
```
wine build-windows.bat
```
- Note: You may see a bunch of warning/debug messages.  This is probably normal, and it shouldn't be a huge deal as long as you end up with a working `pychoss.exe` file in the `dist` folder.
5) Test the build to see if it launches properly, either via Wine or a Windows machine.  If it shows the user interface, then you've successfully built it.

### Windows executable from Windows host
*soon™?*

Note: It is currently impossible to build a Linux binary from a Windows machine, as far as I'm aware.  However, building a Windows executable from a Linux machine is possible using Wine (see above).

## Credits and References
- [obs-websocket-py](https://github.com/Elektordi/obs-websocket-py) : WebSocket API used for interfacing with OBS
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) : Library used for enhancing the UI with theme support
- [PyInstaller](https://pyinstaller.org/en/stable/) : Used for compiling single-file binaries for release
- [Clone Hero](https://clonehero.net/) : Clone of Guitar Hero games made in Unity Engine
- [YARG](https://yarg.in/) : Clone of Rock Band games, also made in Unity Engine
- Countless Google searches leading me to various forums and blogs that helped me develop this script
  - including [this blog post](https://www.makeworld.space/2021/10/linux-wine-pyinstaller.html) which helped me build the Windows version without having to boot into Windows.

If you find this program useful for your Twitch streams, then thanks for using it.  I hope you get good FCs, and rock on!
