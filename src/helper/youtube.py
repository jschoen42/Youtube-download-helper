import time

from typing import Any, Dict
from pathlib import Path

import yt_dlp                          # type: ignore # mypy
from yt_dlp.utils import DownloadError # type: ignore # mypy

from utils.trace import Trace, Color
from utils.util  import export_json

from helper.analyse import analyse_data

# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278

def download_video(video_id: str, path: Path | str, only_audio: bool, debug: bool = False) -> bool:
    path = Path(path)

    yt_opts: Dict[str, Any] = {
        "verbose": False,
        "quiet": True,
        "force-ipv6": True,
        "debug_printtraffic": debug,

        # "outtmpl": str(path) + "/%(uploader)s/%(title)s.%(ext)s",
    }

    # step 1: audio/video title and available tracks

    try:
        title = ""
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # step 1: metadata: title, ...

        start_time = time.time()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            Trace.info(f"get title '{video_id}'")

            info = ydl.extract_info(video_url, download=False)
            if info is None:
                return False

            title = info["title"]
            channel = info["channel"]
            timestamp = info["timestamp"]

        export_json( path / valid_filename(channel), valid_filename(title) + ".json", ydl.sanitize_info(info), timestamp = timestamp ) # type: ignore

        available_tracks = analyse_data( info, title )
        if only_audio:
            audio = available_tracks["audio"]["mp4a"]
            format = f"{audio}"
        else:
            video = available_tracks["video"]["vp09"]
            audio = available_tracks["audio"]["opus"]

            # video = available_tracks["video"]["avc1"]
            # audio = available_tracks["audio"]["opus"]

            # video = available_tracks["video"]["av01"]
            # audio = available_tracks["audio"]["mp4a"]

            format = f"{video}+{audio}"

        yt_opts = {
            "extract_audio": only_audio,
            "verbose":       False,
            "quiet":         True,
            "force-ipv6":    True,
            "format":        format,
            "outtmpl":       str(path) + f"/%(uploader)s/%(title)s ({format}).%(ext)s",

            # "debug_printtraffic": True,
        }

        # yt_opts["format"] = format
        # yt_opts["verbose"] = True
        # yt_opts["debug_printtraffic"] = True

        Trace.result( f"{time.time() - start_time:.2f} sec => '{title}' ({format})" )

    except DownloadError as err:
        err_no_color = Color.clear(str(err))
        error = err_no_color.replace("ERROR: ", "")
        Trace.fatal( f"{error}" )
        return False

    # step 2: audio/video download

    try:
        start_time = time.time()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.extract_info(video_url, download=True)

        Trace.result( f"downloaded {time.time() - start_time:.2f} sec")
        return True

    except DownloadError as err:
        err_no_color = Color.clear(str(err))
        error = err_no_color.replace("ERROR: ", "")

        Trace.info(f"{error}")
        return False


def valid_filename( text: str ) -> str:

    convert = {
        "<": "˂",  # U+027C
        ">": "˃",  # U+027D
        ":": "：",  # U+3014
        '"': "'",
        "/": "∕",  # U+2215
        "|": "｜",  # U+2663
        "?": "？",  # U+3013
        "*": "˄",  # U+02C4

        "\\": "_",
    }

    for x, y in convert.items():
        text = text.replace(x, y)

    return text
