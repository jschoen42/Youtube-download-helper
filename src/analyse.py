"""
    © Jürgen Schoenemeyer, 27.03.2025 18:45

    src/utils/analyse.py

    .venv/Scripts/activate
    uv run src/analyse.py
    uv run src/analyse.py -l de

    uv run src/analyse.py -l de > result-de.log > data/test/_result-de.log

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
