from pathlib import Path

# from rich import print

from src.utils.trace import Trace
from src.utils.util import import_json
from src.utils.file import list_files

def analyse_json_all( path: Path, language: str = "de" ):
    files = list_files( path, "json" )
    for file in files:
        analyse_json( path, file, language )


def analyse_json( path: Path, filename: str, language: str = "de" ):

    data = import_json( path, filename )
    if data is None:
        return

    audio = {} # mp4a, opus, ac-3, ec-3
    video = {} # avc1, vp09, av01

    video_id = data["id"]

    Trace.info(f"{video_id} - '{filename}'\n")

    formats = data["formats"]
    for format in formats:
        id = format["format_id"]

        # Trace.error(f"format_id: {id}")

        acodec = format.get("acodec", "none")
        vcodec = format.get("vcodec", "none")

        # Audio

        if acodec != "none":
            type = acodec.split(".")[0]

            if type not in audio:
                audio[type] = {}

            audio[type][id] = {
                "language": format["language"],
                "codec":    acodec,
                "ext":      format.get("audio_ext", ""),
                "tbr":      round(format["tbr"]),
                "channels": format["audio_channels"],
                "sampling": format["asr"],
                "filesize": format.get("filesize"),
            }

        # Video

        elif vcodec != "none":
            type = vcodec.split(".")[0]

            if type not in video:
                video[type] = {}

            video[type][id] = {
                "codec":    vcodec,
                "ext":      format.get("video_ext", ""),
                "tbr":      round(format["tbr"]),
                "width":    format["width"],
                "height":   format["height"],
                "fps":      format["fps"],
                "filesize": format.get("filesize"),
            }

        # Images

        else:
            continue

    # video

    best_resolution = ""
    max_id = -1
    for type, group in video.items():
        max_tbr = -1
        for key, value in group.items():
            if value["tbr"] > max_tbr:
                max_tbr = value["tbr"]
                max_id = key
                best_resolution = f"{value["width"]}x{value["height"]}"

            Trace.info(f"video: {key:<3} - codec '{value["codec"]}', {value["width"]}x{value["height"]}, tbr: {value["tbr"]}")

        Trace.result( f"video {type} -> {max_id} > {max_tbr} ({best_resolution})\n" )

    # audio

    # Trace.fatal( audio )

    max_id = -1
    for type, group in audio.items():
        max_tbr =-1
        for key, value in group.items():
            if "-drc" not in key:
                if language in value["language"]:
                    if value["tbr"] > max_tbr:
                        max_tbr = value["tbr"]
                        max_id = key
                    Trace.info(f"audio: {key:<3} '{value["language"]}' - codec '{value["codec"]}', {value["channels"]} channels, tbr: {value["tbr"]}")
                else:
                    Trace.error(f"audio: {key:<3} '{value["language"]}' - codec '{value["codec"]}', {value["channels"]} channels, tbr: {value["tbr"]}")

        Trace.result(f"audio {type} -> {max_id} > {max_tbr}\n")
