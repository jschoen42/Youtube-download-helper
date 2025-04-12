"""
    © Jürgen Schoenemeyer, 12.04.2025 18:38

    src/main.py

    uv run src/main.py
    uv run src/main.py -id rU5mxh5tsI0
    uv run src/main.py -l de -id zqgbJq3T8Qo
    uv run src/main.py -a zqgbJq3T8Qo
"""
from __future__ import annotations

import sys

import click

from helper.youtube import download_video
from utils.globals import BASE_PATH
from utils.prefs import Prefs
from utils.trace import Trace

DEST_VIDEO = BASE_PATH / "data" / "video"
DEST_AUDIO = BASE_PATH / "data" / "audio"

def validate_id(_ctx: click.Context, _param: click.Parameter, value: str) -> str:
    if len(value) != 11:
        msg = f"length = {len(value)} (should be 11)"
        raise click.BadParameter(msg)
    return value

@click.command()
@click.option("-id", "--youtube_id", callback=validate_id, prompt="Youtube ID (11 char)", help="Youtube ID - 11 characters")
@click.option("-a",  "--audio", is_flag=True, help="only audio track")
@click.option("-l",  "--language", help="force audio language 'de', 'en', 'null'", default="")
@click.option("-d",  "--debug", is_flag=True, help="debug: show web traffic")

def main(youtube_id: str, audio: bool, language: str, debug: bool) -> None:

    if audio:
        _ret = download_video(youtube_id, DEST_AUDIO, True, language, debug)
    else:
        _ret = download_video(youtube_id, DEST_VIDEO, False, language, debug)

if __name__ == "__main__":
    Trace.set(debug_mode=True, show_caller=False, timezone=False)
    Trace.action(f"Python version {sys.version}")

    Prefs.init("settings")
    Prefs.load("settings.yaml")

    try:
        main()
    except KeyboardInterrupt:
        print()
        Trace.exception("KeyboardInterrupt")
        sys.exit()
