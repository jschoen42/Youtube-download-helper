"""
    © Jürgen Schoenemeyer, 27.03.2025 18:53

    src/utils/analyse.py

    .venv/Scripts/activate
    uv run src/analyse.py
    uv run src/analyse.py -l de

    uv run src/analyse.py > test/data/_result.log
    uv run src/analyse.py -l de > test/data/_result-de.log
    uv run src/analyse.py -l en > test/data/_result-en.log
"""
from __future__ import annotations

import sys

import click

from helper.analyse import analyse_json_all
from utils.globals import BASE_PATH
from utils.trace import Trace

TEST_DIR = BASE_PATH / "test" / "data"

@click.command()
@click.option("-l",  "--language", help="force audio language 'de', 'en', 'null'", default="")

def main(language: str) -> None:
    Trace.set(show_caller=True, show_timestamp=False)

    analyse_json_all( TEST_DIR, language=language )

if __name__ == "__main__":
    Trace.set(debug_mode=True, timezone=False)
    Trace.action(f"Python version {sys.version}")
    main()
