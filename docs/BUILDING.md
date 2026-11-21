# Building CD Log Checker GUI

This guide explains how to build CD Log Checker GUI yourself. You do **not**
need to be a programmer. Pick the part that fits you:

- **Part A**: let GitHub build it for you (easiest, nothing to install).
- **Part B**: build it on your own Windows PC.
- **[Build a single .exe yourself](#build-a-single-exe-yourself)**: if you want
  one self-contained `.exe` instead of a folder.
- **Part C**: update the app to a newer version of hbcl.
- **Part D**: fixing common problems.

If you only want to *use* the app, you don't need this guide. Just download the
zip from the [Releases page](https://github.com/AgiLityOps/CD-Log-Checker-GUI/releases).

### Folder version vs. single .exe

The app can be built two ways from the same code:

| | Folder version (official) | Single .exe |
|---|---|---|
| What you get | A `CD-Log-Checker-GUI` folder containing `CD-Log-Checker-GUI.exe` and an `_internal` folder | One file, `CD-Log-Checker-GUI.exe` |
| How to share it | Zip the whole folder | Copy the one file |
| Start-up | Fast | Slower (unpacks itself to a temp folder on every start) |
| Antivirus false positives | Rare (the v0.1.2 release scanned 0/71) | More likely |

Official releases are the **folder version**. The single .exe is for people who
build it themselves.

---

## Part A: Get a build automatically with GitHub Actions

### What is GitHub Actions?

GitHub Actions is a free service where GitHub runs a script for you on one of
its own computers. This repository has a script (called a *workflow*) in
[`.github/workflows/build.yml`](../.github/workflows/build.yml), named
**Build Windows exe**. It:

1. starts a fresh Windows computer in the cloud,
2. installs Python, and compiles PyInstaller's starter program (the
   "bootloader") from source, which helps avoid antivirus false positives,
3. installs everything else the app needs and runs the tests,
4. builds the folder version (and, if you ask for it, a single .exe) and checks
   that it starts,
5. zips the result.

The workflow starts in two ways:

| How it starts | What you get |
|---|---|
| You push a **tag** whose name starts with `v` (for example `v0.1.3`) | A **draft Release** on the Releases page with one file attached: `CD-Log-Checker-GUI-v0.1.3-win64-folder.zip`. Only you can see a draft until you publish it |
| You click **Run workflow** in the Actions tab | The folder version as a downloadable **artifact** on the run's page (no Release). Tick **Also build a single-file exe** to also get a single .exe artifact |

Releases start as drafts on purpose, so you can upload the files to a virus
scanner such as [VirusTotal](https://www.virustotal.com) before anyone else can
download them. A single .exe is **never** attached to a Release.

### Step 1: Get your own copy of the repository (a "fork")

You can only run the workflow in a repository you own, so first make a fork.

1. Sign in to [github.com](https://github.com) (create a free account if needed).
2. Open this repository's page.
3. Click **Fork** (top right), then **Create fork**.
4. You now have a copy at `https://github.com/YOUR-NAME/CD-Log-Checker-GUI`.

If you are the owner of the original repository, skip this step and use it directly.

### Step 2: Turn on Actions in your fork

GitHub switches Actions off in new forks for safety.

1. In **your fork**, click the **Actions** tab.
2. Click the green button **I understand my workflows, go ahead and enable them**.

If you don't see that button, Actions is already on.

### Step 3: Start a build

Pick **one** of these three options.

#### Option 1: Make a release from the website

1. In your fork, click **Releases** (right-hand side of the main page;
   or go to `https://github.com/YOUR-NAME/CD-Log-Checker-GUI/releases`).
2. Click **Draft a new release**.
3. Click **Choose a tag**, type a new version such as `v0.1.3`, then click
   **Create new tag: v0.1.3 on publish**.
   The name **must start with a lowercase `v`**, otherwise the workflow won't start.
4. Type a title if you like (for example `v0.1.3`) and click **Publish release**.
5. Publishing creates the tag, and the tag starts the workflow. While it attaches
   the zip, the workflow switches this release back to a **draft**. That is
   expected. Wait for Step 4, then follow Step 5 to publish it again.

#### Option 2: Push a tag from the command line

If you have Git installed and a clone of your fork (see Part B, steps 2 and 3):

```bat
git pull
git tag v0.1.3
git push origin v0.1.3
```

The push starts the workflow. The workflow creates a draft release by itself.

#### Option 3: Run it by hand (no release)

1. Click the **Actions** tab.
2. In the left list, click **Build Windows exe**.
3. Click **Run workflow** (right side). Keep the branch as `main`.
   Tick **Also build a single-file exe** if you want a single .exe too.
4. Click the green **Run workflow** button.
5. When the run finishes, open it and scroll down to **Artifacts**:
   - **CD-Log-Checker-GUI-win64-folder**: the folder version,
   - **CD-Log-Checker-GUI-win64-singlefile**: the single .exe (only if you ticked the box).

   Each one downloads as a zip. Artifacts are deleted automatically after 90 days.

### Step 4: Watch the build

1. Click the **Actions** tab. Your run appears at the top with a yellow dot
   while it is running.
2. Click it, then click the **build** job to see each step live.
3. It takes about 2 to 5 minutes. A green check means success, a red cross
   means something failed (see Part D).

### Step 5: Download, check and publish

1. Click **Releases** (or go to `https://github.com/YOUR-NAME/CD-Log-Checker-GUI/releases`).
2. Find the release marked **Draft**, for example **CD Log Checker GUI v0.1.3**.
3. Under **Assets**, download `CD-Log-Checker-GUI-v0.1.3-win64-folder.zip`.
4. Optional but recommended: upload the zip (and the `CD-Log-Checker-GUI.exe`
   inside it) to [VirusTotal](https://www.virustotal.com) and check the result.
5. To make the release public, click the **pencil (Edit)** icon on the draft,
   then click **Publish release**.

To use the app: extract **all** files from the zip, open the
`CD-Log-Checker-GUI` folder and run `CD-Log-Checker-GUI.exe`. Keep the
`_internal` folder next to the exe.

---

## Part B: Build it locally on Windows

You need Windows 10 or 11 (64-bit) and about 500 MB of free space.

### Step 1: Install Python 3.13

1. Go to [python.org/downloads/windows](https://www.python.org/downloads/windows/).
2. Download the latest **Python 3.13** "Windows installer (64-bit)".
   (Python 3.12 also works. **Don't use 3.14 or newer**; hbcl doesn't support it yet.)
3. Run the installer. **On the first screen, tick "Add python.exe to PATH".**
4. Click **Install Now** and wait until it finishes.
5. Check it works: open the Start menu, type `cmd`, press Enter, and run:

   ```bat
   python --version
   ```

   It should print `Python 3.13.x`.

### Step 2: Install Git

hbcl is downloaded straight from GitHub, so Git is required.

1. Download Git from [git-scm.com/download/win](https://git-scm.com/download/win).
2. Run the installer and keep clicking **Next** (the defaults are fine).
3. **Close and reopen** your Command Prompt, then check:

   ```bat
   git --version
   ```

### Step 3: Download (clone) the source code

In the Command Prompt:

```bat
cd %USERPROFILE%\Documents
git clone https://github.com/AgiLityOps/CD-Log-Checker-GUI.git
cd CD-Log-Checker-GUI
```

(Use your fork's address instead if you made one.)

### Step 4: Create a virtual environment

A virtual environment is a private folder of Python packages just for this
project, so nothing else on your PC is affected.

```bat
python -m venv .venv
.venv\Scripts\activate
```

Your prompt now starts with `(.venv)`. Each time you open a new Command Prompt
to work on the project, `cd` into the folder and run `.venv\Scripts\activate` again.

### Step 5: Install the requirements

```bat
python -m pip install --upgrade pip
pip install -r requirements-build.txt
```

This installs hbcl, tkinterdnd2 (drag and drop) and PyInstaller (the exe builder).

### Step 6 (optional): Try the app without building

```bat
python run_hbcl_gui.py
```

The window should open. Close it when you're done.

### Step 7: Build the folder version (same as the official release)

```bat
set HBCL_GUI_ONEDIR=1
pyinstaller --clean --noconfirm hbcl_gui.spec
```

It takes about a minute. When it prints `Build complete!`, the app is in:

```
dist\CD-Log-Checker-GUI\CD-Log-Checker-GUI.exe
dist\CD-Log-Checker-GUI\_internal\
```

Copy or zip the whole `dist\CD-Log-Checker-GUI` folder to use or share it. The
`build` folder is temporary and can be deleted.

`set HBCL_GUI_ONEDIR=1` only lasts until you close the Command Prompt.

### Step 8 (optional): Run the tests

```bat
pip install pytest
git clone https://github.com/doujincafe/hbcl ..\hbcl
set HBCL_TESTS=..\hbcl\tests\logs
python -m pytest -q
```

> **Note:** a build made on your own PC uses PyInstaller's prebuilt bootloader,
> while the official builds compile it from source. To do the same locally you
> need the free "Build Tools for Visual Studio" (with "Desktop development with
> C++") and then run
> `set PYINSTALLER_COMPILE_BOOTLOADER=1` followed by
> `pip install --force-reinstall --no-binary pyinstaller pyinstaller==6.22.3`
> before building.

---

## Build a single .exe yourself

Official releases are the folder version only. If you want **one
self-contained `.exe`**, build it yourself using one of the two ways below.

> **Heads-up:** single-file PyInstaller exes are more often flagged by antivirus
> programs as a *false positive* (they unpack themselves to a temp folder when
> started, which some scanners find suspicious). This is why official releases
> don't include one. If your antivirus complains about an exe you built
> yourself from this source, you can add an exception for it, or use the
> folder version.

### Way 1: On your own Windows PC

1. Do **Part B, steps 1 to 5** above (install Python and Git, clone, create
   the virtual environment, install the requirements).
2. Open a **new** Command Prompt (so `HBCL_GUI_ONEDIR` is not set), go to the
   project folder and activate the virtual environment:

   ```bat
   cd %USERPROFILE%\Documents\CD-Log-Checker-GUI
   .venv\Scripts\activate
   ```

3. Build. Without `HBCL_GUI_ONEDIR`, the spec builds a single file by default:

   ```bat
   pyinstaller --clean --noconfirm hbcl_gui.spec
   ```

   (If you already set it in this window, run `set HBCL_GUI_ONEDIR=` first to clear it.)
4. Your exe is at `dist\CD-Log-Checker-GUI.exe`. Copy that one file anywhere and run it.

### Way 2: With GitHub Actions (nothing to install)

1. Do **Part A, steps 1 and 2** (fork the repository and enable Actions).
2. Follow **Part A, Step 3, Option 3**, and **tick "Also build a single-file exe"**.
3. When the run finishes, download the **CD-Log-Checker-GUI-win64-singlefile**
   artifact. It is a zip containing `CD-Log-Checker-GUI.exe` (plus the license
   files). Extract the zip and run the exe.

---

## Part C: Update to a newer version of hbcl

The app uses hbcl at one exact, tested version (a *commit*). To move to a newer one:

1. Find the commit you want: open
   [github.com/doujincafe/hbcl/commits/main](https://github.com/doujincafe/hbcl/commits/main),
   click the copy button next to the newest commit to copy its full ID
   (a long code like `93ec71d2d3b1b196d9b51a3d7a6f9e1012923ac9`).
2. Replace the old ID with the new one in **all three** places:
   - `requirements.txt`
   - `pyproject.toml` (the `heybrochecklog @ git+https://...` line)
   - `.github/workflows/build.yml` (the `HBCL_COMMIT:` line)

   You can edit files right on GitHub: open the file, click the pencil icon,
   change it, then click **Commit changes**.
3. Optionally raise the app version in `src/hbcl_gui/__init__.py`
   (`__version__`), `pyproject.toml` (`version`), `version_info.txt` and
   `assets/app.manifest`.
4. Make a new release with a new tag, for example `v0.1.3` (Part A, Step 3).
   The status bar of the new build shows the hbcl version it contains.

---

## Part D: Troubleshooting

**The workflow didn't start after I made a tag.**
- Actions might be disabled in your fork (Part A, Step 2).
- The tag must start with a lowercase `v`, for example `v0.1.3`.
- The workflow file must exist in the commit the tag points to.

**I don't see the "Also build a single-file exe" checkbox.**
It appears after you click **Run workflow** in the Actions tab, on the
**Build Windows exe** workflow. If it's missing, your fork has an old copy of
the workflow: update your fork (**Sync fork** button on its main page).

**I want to rebuild the same version (re-use a tag).**
Delete the old release and tag, then create them again:
on the website, open the release, click the trash icon to delete it, then go to
**Tags**, open the tag and delete it. On the command line:
`git tag -d v0.1.3`, `git push origin :refs/tags/v0.1.3`, then tag and push again.
Note that a rebuilt file has a different SHA-256, so scan it again.

**The workflow failed (red cross).**
Click the failed run, then the red step, to read the error. Common causes:
- *"Resource not accessible by integration"* during **Create draft GitHub Release**:
  go to **Settings > Actions > General > Workflow permissions**, choose
  **Read and write permissions**, save, and run it again.
- A failure in **Run tests** after you changed the hbcl commit: the new hbcl
  version may behave differently. Go back to the previous commit ID or report it.

**The app says "Failed to load Python DLL" or closes immediately (folder version).**
The exe can't find its `_internal` folder. Extract **all** files from the zip
(don't run it from inside the zip) and keep `CD-Log-Checker-GUI.exe` and
`_internal` in the same folder.

**`'python' is not recognized as an internal or external command`.**
Python isn't on your PATH. Re-run the Python installer, choose **Modify**, and
make sure **Add Python to environment variables** is ticked. Then open a new
Command Prompt. Typing `py` instead of `python` also works.

**`'git' is not recognized...` or pip says `Cannot find command 'git'`.**
Install Git (Part B, Step 2) and open a **new** Command Prompt.

**pip tries to compile `faust-cchardet` and fails with "Microsoft Visual C++ 14.0 is required".**
You're probably on Python 3.14 or newer, or 32-bit Python. Install 64-bit
Python 3.13 and create the virtual environment again.

**`.venv\Scripts\activate` gives a security error in PowerShell.**
Use Command Prompt (`cmd`) instead, or run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell once.

**I got a folder when I wanted a single .exe (or the other way round).**
The `HBCL_GUI_ONEDIR` setting decides. `set HBCL_GUI_ONEDIR=1` gives a folder;
a new Command Prompt (or `set HBCL_GUI_ONEDIR=`) gives a single .exe.

**Windows says "Windows protected your PC", or antivirus deletes the exe.**
The app isn't code-signed, so this can happen. Click **More info > Run anyway**.
If antivirus removed an exe you built yourself, restore it from quarantine or
add an exception, or use the folder version, which is flagged much less often.

**Drag and drop doesn't work.**
Windows blocks dragging from a normal window into a program running as
administrator (and the other way round). Run the app normally, not
"as administrator". **Open log...** always works.
