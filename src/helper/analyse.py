"""
    © Jürgen Schoenemeyer, 24.02.2025

    src/helper/analyse.py

    PUBLIC:
    - analyse_json_all(path: Path, language: str = "de" ) -> None
    - analyse_json(path: Path, filename: str, language: str = "de" ) -> None
    - analyse_data(data: Dict[str, Any], name: str = "", language: str = "de") -> Dict[str, Any]

"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List  # , cast

from utils.file import import_json, listdir_match_extention
from utils.trace import Trace

if TYPE_CHECKING:
    from pathlib import Path

# yt-dlp https://www.youtube.com/watch?v=37SpumiGHgE --list-formats

def analyse_json_all(path: Path, language: str = "de") -> None:
    files, _ = listdir_match_extention( path, ["json"] )
    for file in files:
        analyse_json( path, file, language )

def analyse_json(path: Path, filename: str, language: str = "de") -> None:
    data = import_json( path, filename )
    if data is None:
        return

    _result = analyse_data( data, filename, language )
    # Trace.result( result )

def analyse_data(data: Dict[str, Any], name: str = "", language: str = "de") -> Dict[str, Any]:

    # pass 1 - find all I

    #   "language": "en-US",
    #   "format_note": "American English - original (default)",

    #   "language": "de-DE",
    #   "format_note": "German (Germany) original, low",

    audios: Dict[str, Any] = {} # mp4a, opus, ac-3, ec-3
    videos: Dict[str, Any] = {} # avc1, vp09, av01
    combined: List[str] = []

    original_language = None

    video_id = data["id"]

    if name == "":
        Trace.info(f"{video_id}'")
    else:
        Trace.info(f"{video_id} - '{name}'")

    formats = data["formats"]

    # find the highest datarate for each codec

    formats = data["formats"]
    for format in formats:
        id = format["format_id"]

        note = format.get("format_note", "" )

        if "DRC" in note:
            continue

        acodec = format.get("acodec", "none")
        vcodec = format.get("vcodec", "none")

        # combined Audio + Video (-> low quality)

        if acodec != "none" and vcodec != "none":
            combined.append(id)

        # only Audio

        elif acodec != "none":
            type = acodec.split(".")[0]
            if "language" in format:
                lang = format["language"].split("-")[0]
            else:
                lang = "unkwown"

            if lang not in audios:
                audios[lang] = {}

            if type not in audios[lang]:
                audios[lang][type] = {}

            audios[lang][type][id] = {
                "codec":    acodec,
                "tbr":      round(format["tbr"]),
                "quality":  round(format["quality"]),
                "channels": format["audio_channels"],
                "sampling": format["asr"],
                "filesize": format.get("filesize"),
            }

            if "original" in note:
                original_language = lang

        # only Video

        elif vcodec != "none":
            type = vcodec.split(".")[0]
            if type == "vp9":
                type = "vp09"

            if type not in videos:
                videos[type] = {}

            videos[type][id] = {
                "codec":    vcodec,
                "tbr":      round(format["tbr"]),
                "quality":  round(format["quality"]),
                "width":    format["width"],
                "height":   format["height"],
                "fps":      round(format["fps"]),
                "filesize": format.get("filesize"),
            }

        # Images

        else:
            continue

    # if len(combined)>0:
    #     Trace.warning( f"combined video + audio: {combined}\n" )

    # sorted by "tbr" (total bitrate)

    """
    videos: {
        'vp09': {
            '602': {'codec': 'vp09.00.10.08', 'tbr':    93, 'quality':  0, 'width':  256, 'height':  144, 'fps': 15, 'filesize': None},
            '603': {'codec': 'vp09.00.11.08', 'tbr':   169, 'quality':  0, 'width':  256, 'height':  144, 'fps': 30, 'filesize': None},
            '278': {'codec': 'vp9',           'tbr':    71, 'quality':  0, 'width':  256, 'height':  144, 'fps': 30, 'filesize': 10016992},
            '604': {'codec': 'vp09.00.20.08', 'tbr':   302, 'quality':  5, 'width':  426, 'height':  240, 'fps': 30, 'filesize': None},
            '242': {'codec': 'vp9',           'tbr':   145, 'quality':  5, 'width':  426, 'height':  240, 'fps': 30, 'filesize': 20533477},
            '605': {'codec': 'vp09.00.21.08', 'tbr':   765, 'quality':  6, 'width':  640, 'height':  360, 'fps': 30, 'filesize': None},
            '243': {'codec': 'vp9',           'tbr':   345, 'quality':  6, 'width':  640, 'height':  360, 'fps': 30, 'filesize': 48873387},
            '606': {'codec': 'vp09.00.30.08', 'tbr':  1177, 'quality':  7, 'width':  854, 'height':  480, 'fps': 30, 'filesize': None},
            '244': {'codec': 'vp9',           'tbr':   503, 'quality':  7, 'width':  854, 'height':  480, 'fps': 30, 'filesize': 71316031},
            '609': {'codec': 'vp09.00.31.08', 'tbr':  2171, 'quality':  8, 'width': 1280, 'height':  720, 'fps': 30, 'filesize': None},
            '247': {'codec': 'vp9',           'tbr':  1053, 'quality':  8, 'width': 1280, 'height':  720, 'fps': 30, 'filesize': 149326182},
            '614': {'codec': 'vp09.00.40.08', 'tbr':  3566, 'quality':  9, 'width': 1920, 'height': 1080, 'fps': 30, 'filesize': None},
            '248': {'codec': 'vp9',           'tbr':  1656, 'quality':  9, 'width': 1920, 'height': 1080, 'fps': 30, 'filesize': 234733705},
            '620': {'codec': 'vp09.00.50.08', 'tbr':  9511, 'quality': 10, 'width': 2560, 'height': 1440, 'fps': 30, 'filesize': None},
            '271': {'codec': 'vp9',           'tbr':  7508, 'quality': 10, 'width': 2560, 'height': 1440, 'fps': 30, 'filesize': 1064199484},
            '625': {'codec': 'vp09.00.50.08', 'tbr': 18853, 'quality': 11, 'width': 3840, 'height': 2160, 'fps': 30, 'filesize': None},
            '313': {'codec': 'vp9',            tbr': 16995, 'quality': 11, 'width': 3840, 'height': 2160, 'fps': 30, 'filesize': 2409020956}
        },

           =>

        'vp09': {
            '278': {'codec': 'vp9',           'tbr':    71, 'quality':  0, 'width':  256, 'height':  144, 'fps': 30, 'filesize': 10016992},
            '602': {'codec': 'vp09.00.10.08', 'tbr':    93, 'quality':  0, 'width':  256, 'height':  144, 'fps': 15, 'filesize': None},
            '242': {'codec': 'vp9',           'tbr':   145, 'quality':  5, 'width':  426, 'height':  240, 'fps': 30, 'filesize': 20533477},
            '603': {'codec': 'vp09.00.11.08', 'tbr':   169, 'quality':  0, 'width':  256, 'height':  144, 'fps': 30, 'filesize': None},
            '604': {'codec': 'vp09.00.20.08', 'tbr':   302, 'quality':  5, 'width':  426, 'height':  240, 'fps': 30, 'filesize': None},
            '243': {'codec': 'vp9',           'tbr':   345, 'quality':  6, 'width':  640, 'height':  360, 'fps': 30, 'filesize': 48873387},
            '244': {'codec': 'vp9',           'tbr':   503, 'quality':  7, 'width':  854, 'height':  480, 'fps': 30, 'filesize': 71316031},
            '605': {'codec': 'vp09.00.21.08', 'tbr':   765, 'quality':  6, 'width':  640, 'height':  360, 'fps': 30, 'filesize': None},
            '247': {'codec': 'vp9',           'tbr':  1053, 'quality':  8, 'width': 1280, 'height':  720, 'fps': 30, 'filesize': 149326182},
            '606': {'codec': 'vp09.00.30.08', 'tbr':  1177, 'quality':  7, 'width':  854, 'height':  480, 'fps': 30, 'filesize': None},
            '248': {'codec': 'vp9',           'tbr':  1656, 'quality':  9, 'width': 1920, 'height': 1080, 'fps': 30, 'filesize': 234733705},
            '609': {'codec': 'vp09.00.31.08', 'tbr':  2171, 'quality':  8, 'width': 1280, 'height':  720, 'fps': 30, 'filesize': None},
            '614': {'codec': 'vp09.00.40.08', 'tbr':  3566, 'quality':  9, 'width': 1920, 'height': 1080, 'fps': 30, 'filesize': None},
            '271': {'codec': 'vp9',           'tbr':  7508, 'quality': 10, 'width': 2560, 'height': 1440, 'fps': 30, 'filesize': 1064199484},
            '620': {'codec': 'vp09.00.50.08', 'tbr':  9511, 'quality': 10, 'width': 2560, 'height': 1440, 'fps': 30, 'filesize': None},
            '313': {'codec': 'vp9',           'tbr': 16995, 'quality': 11, 'width': 3840, 'height': 2160, 'fps': 30, 'filesize': 2409020956},
            '625': {'codec': 'vp09.00.50.08', 'tbr': 18853, 'quality': 11, 'width': 3840, 'height': 2160, 'fps': 30, 'filesize': None}
        },
        ...
    }
    """

    videos_sorted: Dict[str, Any] = {}
    for key, value in videos.items():
        videos_sorted[key] = dict(sorted(value.items(), key=lambda item: item[1]["tbr"])) # type: ignore[call-overload]

    audios_sorted: Dict[str, Any] = {}
    for lang in audios:
        audios_sorted[lang] = {}
        for key, audio_data in audios[lang].items():
            audios_sorted[lang][key] = dict(sorted(audio_data.items(), key=lambda item: item[1]["tbr"])) # type: ignore[call-overload]

    # all video tracks

    for key, value in videos_sorted.items():
        Trace.debug( f"video: {key}")
        for type, types in value.items():
            size = f"{types['width']}x{types['height']}"
            Trace.debug( f"id: {type:3} - tbr: {types['tbr']:4} - size: {size:9} - codec: {types['codec']}")

    video_best = {}
    for type, value in videos_sorted.items():
        video_best[type] = list(value.keys())[-1]

    # all audio tracks

    for lang, data_lang in audios_sorted.items():
        for key, value in data_lang.items():
            Trace.debug( f"audio: {lang} - {key}")
            for type, types in value.items():
                Trace.debug( f"id: {type:3} - tbr: {types['tbr']:4} - codec: {types['codec']}")

    if len( audios_sorted ) == 1:
        language = next(iter(audios_sorted.keys()))
    elif original_language:
        language = original_language

    audio_best = {}
    if language not in audios_sorted:
        Trace.error( f"language '{language}' not found" )
    else:
        for type, value in audios_sorted[language].items():
            audio_best[type] = list(value.keys())[-1]

    result = {
        "language": language,
        "video": video_best,
        "audio": audio_best,
    }
    Trace.result(f"{result}")
    return result
