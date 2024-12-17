# .venv\Scripts\activate

# python main.py
# python main.py rU5mxh5tsI0
# python main.py -a zqgbJq3T8Qo

# Sonderfall:
# python main.py -YyWIuo-zUQ
#  -> python main.py YyWIuo-zUQ
#  -> python main.py -- -YyWIuo-zUQ

# uv run python main.py
# uv run python main.py -a

import sys

from src.utils.globals import BASE_PATH
from src.utils.trace import Trace
from src.helper.argsparse import parse_arguments

from src.youtube import download_video

DEST_VIDEO = BASE_PATH / "_video"
DEST_AUDIO = BASE_PATH / "_audio"

def main():
    args = parse_arguments()
    Trace.info(f"Arguments: {args}")

    yt_id = ("-" + args["id"])[-11:]
    #if len(yt_id) != 11:
    #    Trace.fatal(f"Invalid YouTube ID: {yt_id}")

    only_audio = args["only_audio"]

    if only_audio:
        _ret = download_video( yt_id, DEST_AUDIO, True )
    else:
        _ret = download_video( yt_id, DEST_VIDEO, False )

if __name__ == "__main__":
    Trace.set( debug_mode=False, timezone=False )
    Trace.action(f"Python version {sys.version}")

    main()
