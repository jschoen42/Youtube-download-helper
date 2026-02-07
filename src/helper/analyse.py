"""
    © Jürgen Schoenemeyer, 07.02.2026 21:23

    src/helper/analyse.py

    PUBLIC:
    - analyse_json_all( path: Path ) -> None
    - analyse_json( path: Path, filename: str ) -> None

    - analyse_data( data: Dict[str, Any], name: str = "") -> Dict[str, Any]
        {
            'language': 'de',
            'video': {
                'vp09': ['303', 9],
                'avc1': ['299', 9],
                'av01': ['399', 9],
            },
            'audio': {
                'opus': ['251-5', 3],
                'mp4a': ['140-5', 3],
            }
        }

    video:
     - vp09 [248], [625]
     - avc1 [137]
     - av01 [399], [401]

    audio:
     - opus [251]
     - mp4a [140]
     - ac-3 [380]
     - ec-3 [328]

    quality video:
     -  0:  256x144
     -  5:  426x240
     -  6:  640x360
     -  7:  854x480
     -  8: 1280x720
     -  9: 1920x1080
     - 10: 2560x1440
     - 11: 3840x2160

    quality audio:
     - 2: ~  64 kbit/sec
     - 3: ~ 128 kbit/sec
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

# utils
from src.utils.file import import_json, listdir_match_extention
from src.utils.trace import Trace

if TYPE_CHECKING:
    from pathlib import Path

# yt-dlp https://www.youtube.com/watch?v=37SpumiGHgE --list-formats

def analyse_json_all(path: Path, language: str) -> None:
    files, _ = listdir_match_extention( path, ["json"] )
    for file in files:
        analyse_json( path, file, language )

def analyse_json(path: Path, filename: str, language: str) -> None:
    data = import_json( path, filename )
    if data is None:
        return

    _result = analyse_data( data, filename, language )

def analyse_data(data: Dict[str, Any], name: str = "", fource_language: str = "") -> Dict[str, Any]:

    if fource_language != "":
        Trace.info( f"force language '{fource_language}'" )

    videos: Dict[str, Any] = {}            # avc1, vp09, av01
    audios: Dict[str, Dict[str, Any]] = {} # mp4a, opus, ac-3, ec-3 (per language)

    original_language = None

    video_id = data["id"]

    if name == "":
        Trace.info(f"{video_id}'")
    else:
        Trace.info(f"{video_id} - '{name}'")

    formats = data["formats"]

    # pass 1: get max. 'language_preference' == original language (?)

    max_language_pref = -1
    for format in formats:
        protokoll = format["protocol"]
        if protokoll != "https":
            continue

        max_language_pref = max(max_language_pref, format.get("language_preference", -1))

    # pass 2: find the highest data rate for each codec

    languages_skipped = set()
    for format in formats:
        id = format["format_id"]

        acodec = format.get("acodec", "none")
        vcodec = format.get("vcodec", "none")

        if acodec == "none" and vcodec == "none":
            continue

        protokoll = format["protocol"]
        if protokoll in {"mhtml", "m3u8_native", "http_dash_segments"}:
            Trace.info(f"skip '{protokoll}'")
            continue

        if protokoll != "https":
            Trace.error(f"unknown protokoll '{protokoll}' - expected 'https'")
            continue

        # Audio + Video -> low quality

        if acodec != "none" and vcodec != "none":
            continue

        # Audio

        if acodec != "none":
            type = acodec.split(".")[0]
            if format.get("language"):
                lang = format["language"]
            else:
                lang = "null"

            lang_pref = format.get("language_preference", -1)

            if fource_language != "":
                if lang.split("-")[0] != fource_language:
                    languages_skipped.add(lang)
                    continue

            elif max_language_pref > lang_pref:
                languages_skipped.add(lang)
                continue

            note = format.get("format_note", "" )  # "English (United States) original (default), medium",
            if "DRC" in note:
                continue
            if "original" in note:
                original_language = lang

            if lang not in audios:
                audios[lang] = {}

            if type not in audios[lang]:
                audios[lang][type] = {}

            audios[lang][type][id] = {
                "codec":    acodec,
                "pref":     lang_pref,
                "tbr":      round(format["tbr"]),
                "quality":  round(format["quality"]),
                "channels": format.get("audio_channels", 0),
                "sampling": format.get("asr", 0),
                "filesize": format.get("filesize"),
            }

        # Video

        if vcodec != "none":
            type = vcodec.split(".")[0]

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

    # all available video tracks

    for key, value in videos.items():
        Trace.debug()
        Trace.debug( f"video: {key}")
        for type, types in value.items():
            size = f"{types['width']}x{types['height']}"
            Trace.debug( f"id: {type:3} - quality: {types['quality']:2} - tbr: {types['tbr']:4} - size: {size:9} - codec: {types['codec']}")

    # video type -> vp09, avc1, av01

    video_best = {}
    for type, value in videos.items(): # -> last entry
        last    = list(value)[-1]
        quality = value[last]["quality"]
        video_best[type] = [last, quality]

    # all available audio tracks

    for lang, data_lang in audios.items():
        for key, value in data_lang.items():
            Trace.debug()
            Trace.debug( f"audio: {lang} - {key}")
            for type, types in value.items():
                Trace.debug( f"id: {type:3} - quality: {types['quality']:2} - tbr: {types['tbr']:4} - codec: {types['codec']} - pref: {types['pref']}")

    language = fource_language
    if len( audios ) == 1:
        language = next(iter(audios.keys()))
    elif original_language:
        language = original_language

    # audio type -> opus, mp4a

    audio_best = {}
    if language not in audios:
        Trace.error( f"language '{language}' empty" )
    else:
        for type, value in audios[language].items(): # -> last entry
            last    = list(value)[-1]
            quality = audios[language][type][last]["quality"]
            audio_best[type] = [last, quality]

    result = {
        "language": language,
        "video": video_best,
        "audio": audio_best,
        "languages_skipped": list(languages_skipped),
    }

    Trace.result(f"{result}")
    return result
