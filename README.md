# CrosshairX Pro

A customizable Windows desktop crosshair overlay built with Python and PySide6.

## Features
- Transparent, always-on-top crosshair overlay
- Classic, compact, T-style, plus, circle and X styles
- Adjustable size, thickness, center gap and opacity
- Color picker and quick color presets
- Optional center dot and black outline
- System tray controls
- Automated Windows executable builds with GitHub Actions

## Build locally
Run these commands in PowerShell, not inside the Python `>>>` prompt:

```powershell
py -m pip install -r requirements.txt
py -m pip install pyinstaller
py -m PyInstaller --noconfirm --clean --windowed --onefile --name CrosshairXPro main.py
```

The executable is created at `dist\CrosshairXPro.exe`.

## Download the Windows build
After a successful workflow run, open the repository's **Actions** tab, select the latest **Build CrosshairX Pro** run, and download the `CrosshairXPro-Windows` artifact. Artifacts are retained for 14 days.

This is a visual overlay only. It does not read game memory, automate gameplay, or bypass anti-cheat systems.
