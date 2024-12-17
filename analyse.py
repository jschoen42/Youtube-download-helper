# .venv\Scripts\activate
# python test_analyse.py

import sys

from src.utils.globals import BASE_PATH
from src.utils.trace   import Trace

from src.analyse import analyse_json_all # , analyse_json

DIR_JSON = BASE_PATH / "_json"

def main():
    Trace.set(show_caller=False, show_timestamp=False)
    # analyse_json( DEST_INFO_ML, "Kernfusion： Risiken, Atommüll, Endlager • SuperGAU • Radioaktivität • vAzS (109)  ｜ Josef M. Gaßner.json", "de" )
    # analyse_json( DEST_INFO_SL, "the flight that disappeared 1961.json", "en" )

    # analyse_json( DEST_INFO_SL, "[warpCast #136] Frank Herbert - Der Wüstenplanet.json", "de" )
    analyse_json_all( DIR_JSON, "de")

if __name__ == "__main__":
    Trace.action(f"Python version {sys.version}")
    main()
