# import sys
import argparse

# https://docs.python.org/3.12/howto/argparse.html#argparse-tutorial

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("youtube_id", help="Youtube ID - 12 Zeichen")
    parser.add_argument("-a", "--only_audio",  action="store_true", help="no video track")

    args = parser.parse_args()

    # print( args )

    return {
        "id": args.youtube_id,
        "only_audio": args.only_audio
    }
