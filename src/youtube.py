import time
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError

from src.utils.trace import Trace, remove_colors
from src.utils.util import export_json

# https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128-L278

"""
Video: 1920x1080
399 avc1 841
137 avc1 996
270 avc1 1736

248 vp09 1096
614 vp09 2136
616 vp09 3394 +++

Audio
600 Opus 35
249 opus 51
250 opus 69
251 opus 121 +++

599 mp4a 31
139 mp4a 48
140 mp4a 129 +++

Dynamic range compression
600-drc opus 35
249-drc opus 51
250-drc opus 69
251-drc opus 121

599-drc mp4a 31
149-drc mp4a 48
140-drc mp4a 129

"""
def download_video(video_id: str, path: Path | str, only_audio: bool) -> bool:

    yt_opts = {
        "verbose": False,
        "quiet": True,
        # "debug_printtraffic": True,
        "outtmpl": str(path) + "/%(uploader)s/%(title)s.%(ext)s",
        # "language": "de-DE",
    }

    # -> /extractor/youtube.py:4254

    if only_audio:
        tracks = "audio"
        yt_opts["extract_audio"] = True
        yt_opts["format"] = "129" # mp4a
    else:
        tracks = "video/audio"
        # yt_opts["format"] = "616+140"   # vp09 (3394) + mp4a (129) => .mp4
        yt_opts["format"] = "616+251" # vp09 (3394) + opus (121) => .webm

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
