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
        "outtmpl": path + "/%(uploader)s/%(title)s.%(ext)s"
    }

    if only_audio:
        tracks = "audio"
        yt_opts["extract_audio"] = True
        yt_opts["format"] = "m4a" # 'bestaudio'
    else:
        tracks = "video/audio"

    try:
        title = ""
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # step 1: metadata: title, ...

        start_time = time.time()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            Trace.info(f"get title '{video_id}'")
            info = ydl.extract_info(video_url, download=False)
            title = info["title"]
            channel = info["channel"]
            timestamp = info["timestamp"]

        export_json( Path(path, get_valid_filename(channel)), get_valid_filename(title) + ".json", info, timestamp = timestamp )

        Trace.result( f"{time.time() - start_time:.2f} sec => '{title}' ({tracks})" )

        # step 2: audio/video

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
