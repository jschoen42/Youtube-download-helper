"""
    © Jürgen Schoenemeyer, 26.03.2025 19:45

    src/utils/analyse.py

    .venv/Scripts/activate
    uv run src/analyse.py
"""
from __future__ import annotations

import sys

from helper.analyse import analyse_json_all
from utils.globals import BASE_PATH
from utils.trace import Trace

DIR_JSON = BASE_PATH / "_json"

def main() -> None:
    Trace.set(show_caller=False, show_timestamp=False)

    analyse_json_all( DIR_JSON )

if __name__ == "__main__":
    Trace.set(debug_mode=True, timezone=False)
    Trace.action(f"Python version {sys.version}")
    main()
