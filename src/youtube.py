import time
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError

from src.utils.trace import Trace, Color
from src.utils.util import export_json
from src.analyse import analyse_data

# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278

def download_video(video_id: str, path: Path | str, only_audio: bool) -> bool:

    yt_opts = {
        "verbose": False,
        "quiet": True,
        "outtmpl": str(path) + "/%(uploader)s/%(title)s.%(ext)s",
        "force-ipv6": True,

        # "debug_printtraffic": True,
    }

    # step 1: audio/video title and available tracks

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

        available_tracks = analyse_data( info, title )
        if only_audio:
            yt_opts["extract_audio"] = True
            audio = available_tracks["audio"]["mp4a"]
            format = f"{audio}"
        else:
            video = available_tracks["video"]["vp09"]
            audio = available_tracks["audio"]["opus"]

            video = available_tracks["video"]["avc1"]
            audio = available_tracks["audio"]["opus"]

            format = f"{video}+{audio}"

        yt_opts["format"] = format

        Trace.result( f"{time.time() - start_time:.2f} sec => '{title}' ({format})" )

    except DownloadError as err:
        err_no_color = Color.clear(str(err))
        error = err_no_color.replace("ERROR: ", "")
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
