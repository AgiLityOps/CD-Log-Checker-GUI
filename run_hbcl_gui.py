"""Launcher used by PyInstaller (and handy for running from a checkout)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from hbcl_gui.app import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
