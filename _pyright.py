# python _pyright.py src

# install: npm install --global pyright
# update: npm update --global pyright

import os
import sys
import subprocess
import platform
import json
import shutil
import time
import re
import argparse

from pathlib import Path
from datetime import datetime

BASE_PATH = Path(sys.argv[0]).parent.parent.resolve()
RESULT_FOLDER = ".type-check-result"

LINEFEET = "\n"

def run_pyright(src_path: Path, python_version: str) -> None:

    if python_version == "":
        try:
            with open(".python-version", "r") as f:
                python_version = f.read().strip()
        except OSError:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    # https://microsoft.github.io/pyright/#/configuration?id=diagnostic-settings-defaults

    settings = {
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

    text =  f"Python:   {sys.version.replace(LINEFEET, ' ')}\n"
    text += f"Platform: {platform.platform()}\n"
    text += f"Date:     {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
    text += f"Path:     {BASE_PATH}\n"
    text += "\n"

    text += "PyRight [version] settings:\n"
    for key, value in settings.items():
        text += f" - {key}: {value}\n"

    config = "tmp.json"
    with open(config, "w") as config_file:
        json.dump(settings, config_file, indent=2)

    start = time.time()
    try:
        result = subprocess.run([npx_path, "pyright", src_path, "--verbose", "--project", config], capture_output=True, text=True, shell=True)
    finally:
        os.remove(config)

    if result.returncode == 2:
        print(f"errorcode: {result.returncode}")
        print(result.stderr)
        sys.exit(result.returncode)

    stdout = result.stdout.encode("cp1252").decode("utf-8").replace("\xa0", " ")

    path = str(BASE_PATH)[0].lower() + str(BASE_PATH)[1:]
    version = ""
    num_files = 0
    summary = "no summary"

    verbose_info = False
    for line in stdout.splitlines():
        if line.startswith("Loading configuration"):
            verbose_info = True
            continue

        if line.startswith("pyright"):
            version = line.split(" ")[1]
            text = text.replace("[version]", version)
            verbose_info = False
            continue

        if verbose_info:
            if line.startswith("Found"):
                match = re.search(r"\d+", line)
                if match:
                    num_files = int(match.group())
                continue

        if line.startswith("  "):
            if path in line:
                text += line[3 + len(str(BASE_PATH)):] + "\n"
            else:
                text += " - " + line[4:] + "\n"
        else:
            if "informations" in line:
                summary = line.strip()
                text += f"\n'{src_path}' {num_files} source file(s): {summary}"

            text += "\n"

    result_filename = f"pyright-{python_version}-'{name}'.txt"
    with open(folder_path / result_filename, "w", newline="\n") as file:
        file.write(text)

    duration = time.time() - start
    print(f"[PyRight {version} ({duration:.2f} sec)] '{name}' - {num_files} source file(s): {summary} -> {RESULT_FOLDER}/{result_filename}")

    sys.exit(result.returncode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="static type check with Pyright")
    parser.add_argument("path", nargs="?", type=str, default=".", help="relative path to a file or folder")
    parser.add_argument("-v", "--version", type=str, default="", help="Python version 3.10/3.11/...")

    args = parser.parse_args()

    try:
        run_pyright(Path(args.path), args.version)
    except KeyboardInterrupt:
        print(" --> KeyboardInterrupt")
        sys.exit(1)