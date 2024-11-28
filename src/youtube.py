import time
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError

from src.utils.trace import Trace, remove_colors
from src.utils.util import export_json

# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278


def download_video(video_id: str, path: Path | str, only_audio: bool) -> bool:

    yt_opts = {
        "verbose": False,
        "quiet": True,
        # "debug_printtraffic": True,
        "outtmpl": str(path) + "/%(uploader)s/%(title)s.%(ext)s",

        # "simulate": True,
        "force-ipv6": True,

    }

    # -> /extractor/youtube.py:4254

    if only_audio:
        tracks = "audio"
        yt_opts["extract_audio"] = True
        yt_opts["format"] = "140" # "m4a"
    else:
        tracks = "video/audio"
        # yt_opts["format"] = "616+140"   # vp09 (3394) + mp4a (129) => .mp4
        # yt_opts["format"] = "616+251" # vp09 (3394) + opus (121) => .webm
        # yt_opts["format"] = "299+251" # 4k
        # yt_opts["format"] = "248+251"
        yt_opts["format"] = "webm+webm"
    # step 1: audio/video title

    try:
        title = ""
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # step 1: metadata: title, ...

        start_time = time.time()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            Trace.info(f"get title '{video_id}'")
            info = ydl.extract_info(video_url, download=False, process=False)
            title = info["title"]
            channel = info["channel"]
            timestamp = info["timestamp"]

        export_json( Path(path, get_valid_filename(channel)), get_valid_filename(title) + ".json", info, timestamp = timestamp )

        Trace.result( f"{time.time() - start_time:.2f} sec => '{title}' ({tracks})" )

    except DownloadError as err:
        err_no_color = remove_colors(str(err))
        error = err_no_color.replace("ERROR: ", "")
        return False

    Trace.fatal("STOP")

    # step 2: audio/video download

    try:
        start_time = time.time()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.extract_info(video_url, download=True)

        Trace.result( f"downloaded {time.time() - start_time:.2f} sec")
        return True

    except DownloadError as err:
        err_no_color = remove_colors(str(err))
        error = err_no_color.replace("ERROR: ", "")

        Trace.info(f"{error}")
        return False


def get_valid_filename( text ):

    convert = {
        "<": "˂",
        ">": "˃",
        ":": "：",
        '"': "'",
        "/": "∕",
        "|": "｜",
        "?": "？",
        "*": "˄",

        "\\": "_",
    }

    for x, y in convert.items():
        text = text.replace(x, y)

    return text
