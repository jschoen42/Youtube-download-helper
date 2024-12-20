from pathlib import Path

from utils.trace import Trace
from utils.util  import import_json
from utils.file  import list_files

def analyse_json_all( path: Path, language: str = "de" ):
    files, _ = list_files( path, "json" )
    for file in files:
        analyse_json( path, file, language )

def analyse_json( path: Path, filename: str, language: str = "de" ) -> dict:
    data = import_json( path, filename )
    if data is None:
        return

    _result = analyse_data( data, filename, language )
    # Trace.result( result )

def analyse_data( data: dict, name: str = "", language: str = "de",  ) -> dict:

    # pass 1 - find all I


    #   "language": "en-US",
    #   "language_preference": 10,

    #   "language": "de-DE",
    #   "language_preference": -1,

    audios = {} # mp4a, opus, ac-3, ec-3
    videos = {} # avc1, vp09, av01
    combined = []

    video_id = data["id"]

    if name == "":
        Trace.info(f"{video_id}'")
    else:
        Trace.info(f"{video_id} - '{name}'")

    formats = data["formats"]

    # pass 1: find all collisions of format_id

    format_ids = {}
    for format in formats:
        id = format["format_id"]

        if "language_preference" in format and format["language"]:
        # if "language" in format and format["language"]:
            lang = format["language"].split("-")[0]
            lang_pref = format["language_preference"]

            if id not in format_ids:
                format_ids[id] = []
            format_ids[id].append({lang: lang_pref})

    # ToDo: Test mit mehr als zwei Sprachen, es fehlt noch das passende Video

    format_collisions = {}
    for key, value in format_ids.items():
        if len(value) > 1:
            # '139': [{'en': 10}, {'de': -1}] => {'139': [{'de': -1}, {'en': 10}]}
            # format_collisions[key] = sorted(value, key=lambda x: list(x.values())[0])

            # '139': [{'en': 10}, {'de': -1}] => {'139': ['de', 'en']}
            format_collisions[key] = [list(d.keys())[0] for d in sorted(value, key=lambda x: list(x.values())[0])]

    if len(format_collisions) > 0:
        Trace.warning(f"id collisions: {format_collisions}")

    # pass 2: find the highest datarate for each codec

    formats = data["formats"]
    for format in formats:
        id = format["format_id"]
        if id in format_collisions:
            lang = format["language"].split("-")[0]
            id = f"{id}-{format_collisions[id].index(lang)}"

        note = format.get("format_note", "" )
        # if note in ["Premium", "storyboard"]:
        #     continue

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
            lang = format["language"].split("-")[0]

            if lang not in audios:
                audios[lang] = {}

            if type not in audios[lang]:
                audios[lang][type] = {}

            audios[lang][type][id] = {
                "codec":    acodec,
               # "ext":      format.get("audio_ext", ""),
                "tbr":      round(format["tbr"]),
                "quality":  round(format["quality"]),
                "channels": format["audio_channels"],
                "sampling": format["asr"],
                "filesize": format.get("filesize"),
            }

        # only Video

        elif vcodec != "none":
            type = vcodec.split(".")[0]
            if type == "vp9":
                type = "vp09"

            if type not in videos:
                videos[type] = {}

            videos[type][id] = {
                "codec":    vcodec,
                # "ext":      format.get("video_ext", ""),
                "tbr":      round(format["tbr"]),
                "quality":  round(format["quality"]),
                "width":    format["width"],
                "height":   format["height"],
                "fps":      format["fps"],
                "filesize": format.get("filesize"),
            }

        # Images

        else:
            continue

    # if len(combined)>0:
    #     Trace.warning( f"combined video + audio: {combined}\n" )

    # sorted by "tbr" (total bitrate)

    videos_sorted = {}
    for key, value in videos.items():
        videos_sorted[key] = dict(sorted(value.items(), key=lambda item: item[1]["tbr"]))

    audios_sorted = {}
    for lang, value in audios.items():
        audios_sorted[lang] = {}
        for key, data in audios[lang].items():
            audios_sorted[lang][key] = dict(sorted(data.items(), key=lambda item: item[1]["tbr"]))


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
        language = list(audios_sorted.keys())[0]

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