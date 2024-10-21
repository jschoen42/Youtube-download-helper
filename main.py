# .venv-3.12\Scripts\activate

# python main.py rU5mxh5tsI0
# python main.py -a zqgbJq3T8Qo

# Sonderfall:
# python main.py -YyWIuo-zUQ
#  -> python main.py YyWIuo-zUQ
#  -> python main.py -- -YyWIuo-zUQ

import sys

from src.utils.trace import Trace

from src.youtube import download_video
from src.helper.argsparse import parse_arguments

DEST_VIDEO = "./_video"
DEST_AUDIO = "./_audio"

def main():
    args = parse_arguments()

    Trace.action(f"Python version {sys.version}")
    Trace.info(f"Arguments: {args}")

    yt_id = ("-" + args['id'])[-11:]
    #if len(yt_id) != 11:
    #    Trace.fatal(f"Invalid YouTube ID: {yt_id}")

    only_audio = args['only_audio']

    if only_audio:
        _ret = download_video( yt_id, DEST_AUDIO, True )
    else:
        _ret = download_video( yt_id, DEST_VIDEO, False )

if __name__ == "__main__":
    main()
