# uv run _basedpyright.py src

import json
import os
import platform
import shutil
import subprocess
import sys
import time

from typing import Dict, List
from argparse import ArgumentParser
from collections import Counter
from datetime import datetime
from pathlib import Path
from subprocess import CompletedProcess

BASE_PATH = Path(sys.argv[0]).parent.parent.resolve()
RESULT_FOLDER = ".type-check-result"

LINEFEET = "\n"

def run_basedpyright(src_path: Path, python_version: str) -> None:

    if python_version == "":
        try:
            with open(".python-version", "r") as f:
                python_version = f.read().strip()
        except OSError:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    # https://microsoft.github.io/pyright/#/configuration?id=diagnostic-settings-defaults

    settings: Dict[str, str | bool | List[str]] = {
        "pythonVersion": python_version,
        # "pythonPlatform": "Linux", # "Windows", "Darwin"

        "venvPath": ".",
        "venv": ".venv",

        # "typeCheckingMode": "off",
        # "typeCheckingMode": "basic",
        # "typeCheckingMode": "standard",
        "typeCheckingMode": "strict",

        # deactivate some Strict rules
        "reportUnknownArgumentType":  False,
        "reportUnknownMemberType":    False,
        "reportUnknownVariableType":  False,

        # extra rules
        "enableExperimentalFeatures":          True,
        "reportImplicitOverride":              True,
        "reportImplicitStringConcatenation":   True,
        "reportImportCycles":                  True,
        "reportMissingSuperCall":              True,
        "reportPropertyTypeMismatch":          True,
        "reportShadowedImports":               True,
        "reportUninitializedInstanceVariable": True,

        "reportCallInDefaultInitializer":      False,
        "reportUnnecessaryTypeIgnoreComment":  False, # mypy <-> pyright

        "deprecateTypingAliases": False,       # always False -> typing: List, Dict, ...
        "reportUnusedCallResult": False,       # always False -> _vars

        "exclude": [
            ".venv/*",
            "src/faster_whisper/*",
            "src/extras/*",
        ]
    }

    if not src_path.exists():
        print(f"Error: path '{src_path}' not found")
        return

    start = time.time()

    folder_path = BASE_PATH / RESULT_FOLDER
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

    name = src_path.stem
    if name == "":
        name = "."

    npx_path = shutil.which("npx")
    if not npx_path:
        print("Error: 'npx' not found")
        return

    text  = f"Python:   {sys.version.replace(LINEFEET, ' ')}\n"
    text += f"Platform: {platform.platform()}\n"
    text += f"Date:     {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
    text += f"Path:     {BASE_PATH}\n"
    text += "\n"

    text += "BasedPyRight [version] settings:\n"
    for key, value in settings.items():
        text += f" - {key}: {value}\n"

    config = "tmp.json"
    with open(config, mode="w") as config_file:
        json.dump(settings, config_file, indent=2)

    try:
        result: CompletedProcess[str] = subprocess.run(["basedpyright", src_path, "--project", config, "--outputjson"], capture_output=True, text=True)
    except Exception as err:
        print(f"error: {err} - basedpyright")
        sys.exit(1)
    finally:
        os.remove(config)

    if result.stderr != "":
        print(f"errorcode: {result.returncode}")
        print(result.stderr)
        sys.exit(result.returncode)

    stdout = result.stdout.encode("cp1252").decode("utf-8").replace("\xa0", " ")
    data = json.loads(stdout)

    # {
    #   "version": "1.1.394",
    #   "time": "1739984210930",
    #   "generalDiagnostics": [
    #     {
    #       "file": "g:\\Python\\Whisper\\whisper-datev-gitlab\\src\\combine_srt.py",
    #       "severity": "error",
    #       "message": "Type \"float\" is not assignable to declared type \"int\"\n  \"float\" is not assignable to \"int\"",
    #       "range": {
    #           "start": {
    #           "line": 49,
    #           "character": 32
    #         },
    #           "end": {
    #           "line": 49,
    #           "character": 40
    #         }
    #       },
    #       "rule": "reportAssignmentType"
    #     }
    #   ],
    #   "summary": {
    #     "filesAnalyzed": 1,
    #     "errorCount": 0,
    #     "warningCount": 0,
    #     "informationCount": 0,
    #     "timeInSec": 2.583
    #   }
    # }

    version     = data["version"]
    diagnostics = data["generalDiagnostics"]
    summary     = data["summary"]

    text = text.replace("[version]", version )

    footer: str =  f"files: {summary['filesAnalyzed']}, "
    footer += f"errors: {summary['errorCount']}, "
    footer += f"warnings: {summary['warningCount']}, "
    footer += f"informations: {summary['informationCount']}, "
    footer += f"duration: {summary['timeInSec']} sec"

    n = len(str(Path(".").absolute())) + 1

    last_file = ""
    error_types: Counter[str] = Counter()
    for diagnostic in diagnostics:
        file       = Path(diagnostic["file"]).as_posix()
        error_type = diagnostic["rule"]
        error      = diagnostic["severity"]
        range      = diagnostic["range"]["start"]

        error_types[error_type] += 1

        msg = file[n:]
        msg += f":{range['line']+1}:{range['character']+1} - {error}: " # 0-based
        msg += diagnostic["message"]
        msg += f" ({error_type})"

        if last_file != file:
            if last_file != "":
                text += "\n"
            text += "\n### " + file[n:] + " ###\n"
            last_file = file

        text += "\n" + msg

    text += "\n"

    if len(error_types)>0:
        text += "\nError types (sorted)"
        for error_type in error_types.most_common():
            text += f"\n - {error_type[0]}: {error_type[1]}"
        text += "\n\n"

    text += footer + "\n"

    result_filename = f"BasedPyRight-{python_version}-'{name}'.txt"
    with open(folder_path / result_filename, mode="w", newline="\n") as f:
        f.write(text)

    duration = time.time() - start
    print(f"[BasedPyRight {version} ({duration:.2f} sec)] {footer} -> {RESULT_FOLDER}/{result_filename}")
    sys.exit(result.returncode)

if __name__ == "__main__":
    parser = ArgumentParser(description="static type check with BasedPyRight")
    parser.add_argument("path", nargs="?", type=str, default=".", help="relative path to a file or folder")
    parser.add_argument("-v", "--version", type=str, default="",  help="Python version 3.10/3.11/...")

    args = parser.parse_args()

    try:
        run_basedpyright(Path(args.path), args.version)
    except KeyboardInterrupt:
        print(" --> KeyboardInterrupt")
        sys.exit(1)
