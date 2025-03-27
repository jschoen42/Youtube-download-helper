"""
    © Jürgen Schoenemeyer, 27.03.2025 17:02

    src/helper/youtube.py

    PUBLIC:
     - download_video(video_id: str, path: Path | str, only_audio: bool, debug: bool = False) -> bool

    PRIVATE:
     - valid_filename_utf16( text: str ) -> str
"""
from __future__ import annotations

import time

from pathlib import Path
from typing import Any, Dict

import yt_dlp  # type: ignore[import-untyped]

from yt_dlp.utils import DownloadError  # type: ignore[import-untyped]

from helper.analyse import analyse_data
from utils.file import export_json
from utils.trace import Color, Trace

# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278

def download_video(video_id: str, path: Path | str, only_audio: bool, force_language: str = "", debug: bool = False) -> bool:
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

            title     = valid_filename_utf16(str(info["title"]))
            channel   = valid_filename_utf16(str(info["channel"]))
            timestamp = float(str(info["timestamp"]))

        data_info = ydl.sanitize_info(info)
        export_json( path / channel, title + ".json", data_info, timestamp = timestamp ) # type: ignore[reportArgumentType] # -> ydl.sanitize_info(info)

        available_tracks = analyse_data( info, title, force_language )
        skipped = available_tracks["languages_skipped"]
        if len(skipped)>0:
            Trace.info(f"languages sikked '{skipped}'")

        if len(available_tracks["audio"]) == 0:
            Trace.fatal(f"no audio '{force_language}' available")

        # video: 'vp9', 'avc1', 'av01'
        # audio: 'opus', 'mp4a'

        if only_audio:
            audio = available_tracks["audio"]["mp4a"][0]
            # audio = available_tracks["audio"]["opus"][0]
            format = f"{audio}"
        else:
            video = available_tracks["video"]["vp9"][0]
            if available_tracks["video"]["vp9"][1] < available_tracks["video"]["avc1"][1]:
                video = available_tracks["video"]["avc1"][0]
                Trace.info( "switch from 'vp9' to 'avc1'" )

            if "opus" in available_tracks["audio"]:
                audio = available_tracks["audio"]["opus"][0]
            else:
                audio = available_tracks["audio"]["mp4a"][0]

            format = f"{video}+{audio}"

        yt_opts = {
            "extract_audio": only_audio,
            "verbose":       False,
            "quiet":         True,
            "force-ipv6":    True,
            "format":        format,
            "outtmpl":       str(path) + f"/%(uploader)s/{title} ({format}).%(ext)s",

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


def valid_filename_utf16( text: str ) -> str:

    convert = {
        "<":  "\uff1c", # "＜" -> Fullwidth Less-Than Sign    - alternative: "\u02c2" -> "˂" -> Modifier Letter Left Arrowhead
        ">":  "\uff1e", # "＞" -> Fullwidth Greater-Than Sign - alternative: "\u02c3" -> "˃" -> Modifier Letter Right Arrowhead
        ":":  "\uff1a", # "：" -> Fullwidth Colon
        "/":  "\uff0f", # "／" -> Fullwidth Solidus           - alternative: "\u2215" -> "∕" -> Division Slash
        "|":  "\uff5c", # "｜" -> Fullwidth Vertical Line
        "?":  "\uff1f", # "？" -> Fullwidth Question Mark
        "*":  "\uff0a", # "＊" -> Fullwidth Asterisk          - alternative: "\u204e" -> "⁎" -> Low Asterisk
        "\\": "\uff3c", # "＼" -> Low Line
        '"':  "\u0027", # "'" -> Apostrophe                   - alternative: "\u2233" -> "″" -> Double Prime
    }

    for x, y in convert.items():
        text = text.replace(x, y)

    return text
