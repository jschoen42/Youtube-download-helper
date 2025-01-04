# import sys

from typing import Dict
from argparse import ArgumentParser, Namespace

# https://docs.python.org/3.12/howto/argparse.html#argparse-tutorial

def parse_arguments() -> Dict:
    parser = ArgumentParser()

    parser.add_argument("youtube_id", help="Youtube ID - 12 Zeichen", type=str)
    parser.add_argument("-a", "--only_audio",  action="store_true", help="no video track")

    args: Namespace = parser.parse_args()

    return {
        "id": args.youtube_id,
        "only_audio": args.only_audio
    }
