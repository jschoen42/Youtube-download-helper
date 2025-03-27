"""
    © Jürgen Schoenemeyer, 27.03.2025 11:24

    src/utils/analyse.py

    .venv/Scripts/activate
    uv run src/analyse.py
"""
from __future__ import annotations

import sys

from helper.analyse import analyse_json_all
from utils.globals import BASE_PATH
from utils.trace import Trace

TEST_DIR = BASE_PATH / "data" / "test"
LANGUAGE = "de"

def main() -> None:
    Trace.set(show_caller=True, show_timestamp=False)

    analyse_json_all( TEST_DIR, language = LANGUAGE )

if __name__ == "__main__":
    Trace.set(debug_mode=True, timezone=False)
    Trace.action(f"Python version {sys.version}")
    main()
