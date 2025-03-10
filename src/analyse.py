"""
    © Jürgen Schoenemeyer, 01.03.2025 18:41

    src/utils/analyse.py

    .venv/Scripts/activate
    python src/analyse.py
"""
from __future__ import annotations

import sys

from helper.analyse import analyse_json_all  # , analyse_json
from utils.globals import BASE_PATH
from utils.trace import Trace

DIR_JSON = BASE_PATH / "_json"

def main() -> None:
    Trace.set(show_caller=False, show_timestamp=False)
    # analyse_json( DEST_INFO_ML, "Kernfusion： Risiken, Atommüll, Endlager • SuperGAU • Radioaktivität • vAzS (109)  ｜ Josef M. Gaßner.json", "de" )
    # analyse_json( DEST_INFO_SL, "the flight that disappeared 1961.json", "en" )

    # analyse_json( DEST_INFO_SL, "[warpCast #136] Frank Herbert - Der Wüstenplanet.json", "de" )
    analyse_json_all( DIR_JSON, "de")

if __name__ == "__main__":
    Trace.set(debug_mode=True, timezone=False)
    Trace.action(f"Python version {sys.version}")
    main()
