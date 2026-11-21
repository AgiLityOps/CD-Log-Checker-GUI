# CD Log Checker GUI

**A portable Windows desktop app for checking CD rip logs, built on
[hbcl (hey-bro-check-log)](https://github.com/doujincafe/hbcl).**

CD Log Checker GUI puts a simple window on top of hbcl, the EAC / XLD rip log
checker. Drop a log file onto the window and you get the score, the list of
deductions, and the full log with color coding, so bad settings and rip errors
stand out right away. It is a single `.exe` with nothing to install.

![CD Log Checker GUI showing a scored EAC log](screenshots/screenshot.png)

## Features

- **Scores EAC and XLD logs** using hbcl's rules, including old EAC 0.95 logs,
  foreign-language EAC logs and combined logs.
- **Lists deductions** with the points each one costs.
- **Color-coded stylized log**: green for good settings and accurate rips,
  orange for warnings, red for problems, blue for neutral information.
- **Drag and drop** one or more `.log` files onto the window, or use
  **Open log...**. You can also drop a log onto the `.exe` icon.
- **Translate** foreign EAC logs to English.
- **Experimental integrity check** (EAC / XLD checksum verification, from hbcl).
- **Copy** the report to the clipboard, or **Save as...** plain text or colored HTML.
- **Portable**: one file, no installer, no Python needed.
- Bad input (unrecognized logs, broken encodings, non-log files) is reported in
  the window; it does not crash the app.

## Download and use

1. Go to the [**Releases**](https://github.com/AgiLityOps/CD-Log-Checker-GUI/releases) page and download
   `CD-Log-Checker-GUI.exe` from the latest release
2. Double-click the `.exe`. To open the program
3. Drag a `.log` file from Explorer onto the window (or click **Open log...**).
4. Tick **Translate** or **Experimental integrity check** if you need them; the
   loaded logs are re-checked immediately.

Keyboard shortcuts: `Ctrl+O` open, `Ctrl+S` save, `Ctrl+A` select all, `Ctrl+C` copy selection.

## Building it yourself

See **[docs/BUILDING.md](docs/BUILDING.md)** for a step-by-step guide, written
for beginners. It covers:

- getting a ready-made `.exe` from GitHub Actions (no tools needed on your PC),
- building on your own Windows PC,
- moving to a newer version of hbcl,
- fixing common errors.

Quick version for developers (Windows, Python 3.12 or 3.13, Git installed):

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-build.txt
pyinstaller --clean --noconfirm hbcl_gui.spec
```

The result is `dist\CD-Log-Checker-GUI.exe`. To run from source instead:
`python run_hbcl_gui.py`.

## Credits and thanks

This app is only a window. **All of the log checking, scoring, translation and
integrity checking is done by hbcl**, and the credit for that belongs to the
people below. Thank you all for building and maintaining such a useful tool and
for releasing it as open source.

- **[ligh7s](https://github.com/ligh7s)**, author of the original
  [hey-bro-check-log](https://github.com/ligh7s/hey-bro-check-log), which hbcl
  grew from.
- **The doujin café Discord community**, who maintain
  [hbcl](https://github.com/doujincafe/hbcl) today. Thanks to the contributors
  to the doujincafe/hbcl repository:
  [@fumiichan](https://github.com/fumiichan),
  [@0x1f610](https://github.com/0x1f610),
  [@CetaceanNation](https://github.com/CetaceanNation),
  [@grigorescu](https://github.com/grigorescu),
  [@woshiluo](https://github.com/woshiluo) and
  [@justjakka](https://github.com/justjakka).
- **[puddly](https://github.com/puddly)**, whose
  [eac_logsigner](https://github.com/puddly/eac_logsigner) provides the EAC
  checksum check used by hbcl.
- **[OPSnet](https://github.com/OPSnet)**, whose
  [xld_logchecker.py](https://github.com/OPSnet/xld_logchecker.py) provides the
  XLD checksum check used by hbcl.

Drag and drop uses [tkinterdnd2](https://github.com/Eliav2/tkinterdnd2) and the
tkdnd extension. The exe is built with [PyInstaller](https://pyinstaller.org).

**This is an unofficial GUI.** It is not affiliated with, or endorsed by,
ligh7s, the doujin café community, the hbcl contributors, puddly or OPSnet.
Please report problems with this app here, not to the hbcl project.

## AI disclaimer

This project was built with the help of Grok, an AI assistant. The code was
AI-generated and then reviewed and tested by the maintainer. It is provided
"as is", without warranty of any kind. Use it at your own risk.

## Known issues

- **Antivirus / SmartScreen warnings.** Unsigned single-file PyInstaller apps
  are sometimes flagged as false positives. Release builds use a PyInstaller
  bootloader compiled from source (no UPX) to reduce this, and a folder
  version is provided as an alternative. You can build the exe yourself (see
  [docs/BUILDING.md](docs/BUILDING.md)) if you prefer.
- **Slow first start.** The single-file exe unpacks itself to a temporary
  folder each time it starts, so it can take a second or two to open.
- hbcl's markup for some EAC 0.95 track headers is slightly malformed; the app
  repairs it before displaying it.

## License

Licensed under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) for
attribution of hbcl (also Apache-2.0) and of the third-party components that
are bundled in the Windows exe.
