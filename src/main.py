# pwsh: .venv/Scripts/activate
# bash: source .venv/Scripts/activate
# deactivate

# python src/main.py
# python src/main.py -id rU5mxh5tsI0
# python src/main.py -a -id zqgbJq3T8Qo

# uv run src/main.py
# uv run src/main.py -id rU5mxh5tsI0
# uv run src/main.py -a zqgbJq3T8Qo

# uv run python src/main.py
# uv run python src/main.py -a

import sys

import click

from helper.youtube import download_video
from utils.globals import BASE_PATH
from utils.trace import Trace

DEST_VIDEO = BASE_PATH / "result" / "video"
DEST_AUDIO = BASE_PATH / "result" / "audio"

def validate_id(_ctx: click.Context, _param: click.Parameter, value: str) -> str:
    if len(value) != 11:
        msg = f"length = {len(value)} (should be 11)"
        raise click.BadParameter(msg)
    return value

@click.command()
@click.option("-id", "--youtube_id", callback=validate_id, prompt="Youtube ID (11 char)", help="Youtube ID - 11 charcters")
@click.option("-l",  "--language", help="audio language", default="de")
@click.option("-a",  "--audio", is_flag=True, help="only audio track")
@click.option("-d",  "--debug", is_flag=True, help="debug: show web traffic")

def main(youtube_id: str, language: str, audio: bool, debug: bool) -> None:

    if audio:
        _ret = download_video(youtube_id, DEST_AUDIO, language, True, debug)
    else:
        _ret = download_video(youtube_id, DEST_VIDEO, language, False, debug)

if __name__ == "__main__":
    Trace.set(debug_mode=False, timezone=False)
    Trace.action(f"Python version {sys.version}")
    Trace.action(f"BASE_PATH: '{BASE_PATH.resolve()}'")

    try:
        main()
    except KeyboardInterrupt:
        print()
        Trace.exception("KeyboardInterrupt")
        sys.exit()
