"""
    © Jürgen Schoenemeyer, 12.04.2025 18:38

    src/helper/youtube.py

    PUBLIC:
     - download_video(youtube_id: str, path: Path | str, audio_only: bool, debug: bool = False) -> bool

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
from utils.prefs import Prefs
from utils.trace import Color, Trace

# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278

def download_video(youtube_id: str, path: Path | str, audio_only: bool, force_language: str = "", debug: bool = False) -> bool:
    path = Path(path)

    if audio_only:
        audio_codecs = Prefs.get("format.audio_only.audio_codecs")
        video_codecs = []
    else:
        audio_codecs = Prefs.get("format.normal.audio_codecs")
        video_codecs = Prefs.get("format.normal.video_codecs")

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
        video_url = f"https://www.youtube.com/watch?v={youtube_id}"

        # step 1: metadata: title, ...

        start_time = time.time()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            Trace.info(f"get metadata '{youtube_id}'")

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
            Trace.info(f"languages skipped '{skipped}'")

        if len(available_tracks["audio"]) == 0:
            Trace.fatal(f"no audio '{force_language}' available")

        # audio: mp4a, opus, ac-3, ec-3 (Enhanced AC-3)
        # video: av01 (H.265), vp9, avc1 (H.264)

        audio_id = ""
        video_id = ""
        format = ""

        quality_max = 0
        for audio_codec in audio_codecs:
            if audio_codec in available_tracks["audio"]:
                quality = available_tracks["audio"][audio_codec][1]
                if quality > quality_max:
                    audio_id = available_tracks["audio"][audio_codec][0]
                    quality_max = quality

        if audio_id == "":
            Trace.fatal(f"no audio codec matching {audio_codecs} <-> {available_tracks["audio"]}")

        if audio_only:
            format = f"{audio_id}"
        else:
            quality_max = 0
            for video_codec in video_codecs:
                if video_codec in available_tracks["video"]:
                    quality = available_tracks["video"][video_codec][1]
                    if quality > quality_max:
                        video_id = available_tracks["video"][video_codec][0]
                        quality_max = quality

            if video_id == "":
                Trace.fatal(f"no video codec matching {video_codecs} <-> {available_tracks["video"]}")
            else:
                format = f"{video_id}+{audio_id}"

        yt_opts = {
            "extract_audio": audio_only,
            "verbose":       False,
            "quiet":         True,
            "force-ipv6":    True,
            "format":        format,
            "outtmpl":       str(path) + f"/%(uploader)s/{title} ({format}).%(ext)s",

            # "debug_printtraffic": True,
        }

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
