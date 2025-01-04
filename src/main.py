# pwsh: .venv/Scripts/activate
# bash: source .venv/Scripts/activate
# deactivate

# python src/main.py
# python src/main.py rU5mxh5tsI0
# python src/main.py -a zqgbJq3T8Qo

# uv run src/main.py
# uv run src/main.py rU5mxh5tsI0
# uv run src/main.py -a zqgbJq3T8Qo

# Sonderfall:
# python src/main.py -YyWIuo-zUQ
#  -> python src/main.py YyWIuo-zUQ
#  -> python src/main.py -- -YyWIuo-zUQ

# uv run python src/main.py
# uv run python src/main.py -a

import sys

from utils.globals import BASE_PATH
from utils.trace import Trace

from helper.argsparse import parse_arguments
from helper.youtube import download_video

DEST_VIDEO = BASE_PATH / "result" / "video"
DEST_AUDIO = BASE_PATH / "result" / "audio"

def main() -> None:
    args = parse_arguments()
    Trace.info(f"Arguments: {args}")

    yt_id = ("-" + args["id"])[-11:]

    only_audio = args["only_audio"]

    if only_audio:
        _ret = download_video( yt_id, DEST_AUDIO, True )
    else:
        _ret = download_video( yt_id, DEST_VIDEO, False )

if __name__ == "__main__":
    Trace.set( debug_mode=False, timezone=False )
    Trace.action(f"Python version {sys.version}")
    Trace.action(f"BASE_PATH: '{BASE_PATH.resolve()}'")

    try:
        main()
    except KeyboardInterrupt:
        print()
        Trace.exception("KeyboardInterrupt")
        sys.exit(0)
