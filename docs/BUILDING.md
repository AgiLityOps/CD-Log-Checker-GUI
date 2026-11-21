# Building CD Log Checker GUI

This guide explains how to get your own copy of `CD-Log-Checker-GUI.exe`.
You do **not** need to be a programmer. Pick the part that fits you:

- **Part A**: let GitHub build the exe for you (easiest, nothing to install).
- **Part B**: build the exe on your own Windows PC.
- **Part C**: update the app to a newer version of hbcl.
- **Part D**: fixing common problems.

If you only want to *use* the app, you don't need this guide. Just download the
exe from the [Releases page](https://github.com/AgiLityOps/CD-Log-Checker-GUI/releases).

---

## Part A: Get a build automatically with GitHub Actions

### What is GitHub Actions?

GitHub Actions is a free service where GitHub runs a script for you on one of
its own computers. This repository has a script (called a *workflow*) in
[`.github/workflows/build.yml`](../.github/workflows/build.yml). It:

1. starts a fresh Windows computer in the cloud,
2. installs Python and everything the app needs,
3. runs the tests,
4. builds `CD-Log-Checker-GUI.exe` (single file) and a folder version, and
   checks that both start,
5. puts them in a **draft** release for you to check and publish.

The workflow starts in two ways:

| How it starts | What you get |
|---|---|
| You push a **tag** whose name starts with `v` (for example `v0.1.2`) | A **draft Release** on the Releases page with the exe, a zip, and a folder-version zip attached. Only you can see a draft until you publish it |
| You click **Run workflow** in the Actions tab | The exe and the folder version as downloadable **artifacts** on the run's page (no Release) |

Releases start as drafts on purpose, so you can upload the files to a virus
scanner such as [VirusTotal](https://www.virustotal.com) before anyone else can download them.

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

### Step 3 (option 1): Make a Release from the website

1. In your fork, click **Releases** (right-hand side of the main page;
   or go to `https://github.com/YOUR-NAME/CD-Log-Checker-GUI/releases`).
2. Click **Draft a new release**.
3. Click **Choose a tag**, type a new version such as `v0.1.2`, then click
   **Create new tag: v0.1.2 on publish**.
   The name **must start with a lowercase `v`**, otherwise the workflow won't start.
4. Type a title if you like (for example `v0.1.2`) and click **Publish release**.
5. Publishing creates the tag, and the tag starts the workflow. While it attaches
   the files, the workflow switches this release back to a **draft**. That is
   expected. Wait for Step 4, then follow Step 5 to publish it again.

### Step 3 (option 2): Push a tag from the command line

If you have Git installed and a clone of your fork (see Part B, steps 2 and 3):

```bat
git pull
git tag v0.1.2
git push origin v0.1.2
```

The push starts the workflow. The workflow creates a draft Release by itself.

### Step 3 (option 3): Run it by hand, no Release

1. Click the **Actions** tab.
2. In the left list, click **Build Windows exe**.
3. Click **Run workflow** (right side), keep the branch as `main`, and click the
   green **Run workflow** button.
4. When the run finishes, open it and scroll to **Artifacts**. Download
   **CD-Log-Checker-GUI-win64** (a zip containing the exe).

### Step 4: Watch the build

1. Click the **Actions** tab. Your run appears at the top with a yellow dot
   while it is running.
2. Click it, then click the **build** job to see each step live.
3. It takes about 3 to 6 minutes. A green check means success, a red cross
   means something failed (see Part D).

### Step 5: Download the exe

1. Click **Releases** (or go to `https://github.com/YOUR-NAME/CD-Log-Checker-GUI/releases`).
2. Find the release marked **Draft**, for example **CD Log Checker GUI v0.1.2**.
3. Under **Assets** you'll find:
   - `CD-Log-Checker-GUI.exe`: the single-file app,
   - `CD-Log-Checker-GUI-v0.1.2-win64.zip`: the same exe plus the license files,
   - `CD-Log-Checker-GUI-v0.1.2-win64-folder.zip`: the folder version. Unzip it
     and run `CD-Log-Checker-GUI.exe` inside. It starts faster, and antivirus
     programs flag it less often.
4. Optional: download the files and scan them on VirusTotal.
5. To make the release public, click the **pencil (Edit)** icon on the draft,
   then click **Publish release**.

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

### Step 7: Build the exe

```bat
pyinstaller --clean --noconfirm hbcl_gui.spec
```

It takes about a minute. (For the folder version, run `set HBCL_GUI_ONEDIR=1`
first; the result goes to `dist\CD-Log-Checker-GUI\`.) When it prints
`Build complete!`, your exe is at:

```
dist\CD-Log-Checker-GUI.exe
```

You can copy that single file anywhere and run it. The `build` folder is
temporary and can be deleted.

### Step 8 (optional): Run the tests

```bat
pip install pytest
git clone https://github.com/doujincafe/hbcl ..\hbcl
set HBCL_TESTS=..\hbcl\tests\logs
python -m pytest -q
```

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
   (`__version__`), `pyproject.toml` (`version`) and `version_info.txt`.
4. Make a new release with a new tag, for example `v0.1.3` (Part A, Step 3).
   The status bar of the new exe shows the hbcl version it contains.

---

## Part D: Troubleshooting

**The workflow didn't start after I made a tag.**
- Actions might be disabled in your fork (Part A, Step 2).
- The tag must start with a lowercase `v`, for example `v0.1.2`.
- The workflow file must exist in the commit the tag points to.

**I want to rebuild the same version (re-use a tag).**
Delete the old release and tag, then create them again:
on the website, open the release, click the trash icon to delete it, then go to
**Tags**, open the tag and delete it. On the command line:
`git tag -d v0.1.2`, `git push origin :refs/tags/v0.1.2`, then tag and push again.

**The workflow failed (red cross).**
Click the failed run, then the red step, to read the error. Common causes:
- *"Resource not accessible by integration"* during **Create draft GitHub Release**:
  go to **Settings > Actions > General > Workflow permissions**, choose
  **Read and write permissions**, save, and run it again.
- A failure in **Run tests** after you changed the hbcl commit: the new hbcl
  version may behave differently. Go back to the previous commit ID or report it.

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

**Windows says "Windows protected your PC", or antivirus deletes the exe.**
The exe isn't code-signed, so this can happen. The workflow compiles
PyInstaller's starter program (the "bootloader") from source to reduce false
alarms, and the folder version is flagged less often than the single file. Click **More info > Run anyway**.
If antivirus removed it, restore it from quarantine or add an exception for
the file you built yourself.

**Drag and drop doesn't work.**
Windows blocks dragging from a normal window into a program running as
administrator (and the other way round). Run the app normally, not
"as administrator". **Open log...** always works.
