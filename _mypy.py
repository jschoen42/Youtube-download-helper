# python _mypy.py src/main.py

import os
import re
import sys
import subprocess
import platform
import time
import argparse

from typing import List
from pathlib import Path
from datetime import datetime

BASE_PATH = Path(sys.argv[0]).parent.parent.resolve()
RESULT_FOLDER = ".type-check-result"

LINEFEET = "\n"

# temp.toml

CONFIG: str = \
"""
[tool.mypy]
mypy_path = "src"
python_version = "[version]"
exclude = [
    "/extras/*",
]

[[tool.mypy.overrides]]
module = "*.models"
ignore_errors = true

[[tool.mypy.overrides]]
module = "faster_whisper.*"
ignore_errors = true
"""

def run_mypy(src_path: Path, python_version: str) -> None:

    if python_version == "":
        try:
            with open(".python-version", "r") as f:
                python_version = f.read().strip()
        except OSError:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    configuration = CONFIG.replace("[version]", python_version )

    # https://mypy.readthedocs.io/en/stable/command_line.html
    # https://gist.github.com/Michael0x2a/36c5948a7ea571b722686226639b0859

    settings: List[str] = [

        "--sqlite-cache",                 # default: False

        ### Import discovery
        "--namespace-packages",           # default: True
        "--explicit-package-bases",       # default: False
        # "--ignore-missing-imports",     # default: False
        # "--follow-untyped-imports",     # default: False
        # "--follow-imports",             # default: str normal (normal, silent, skip, error)
        # "--follow-imports-for-stubs",   # default: False
        # "--python-executable",          # default: str
        # "--no-site-packages",           # default: False
        # "--no-silence-site-packages",   # default: False

        ### Platform configuration
        # "--python-version",             # default: str -> pyproject.toml
        # "--platform",                   # default: str
        # "--always-true",                # default: str constant, constant, ...

        ### Disallow dynamic typing
        # "--disallow-any-unimported",    # default: False
        # "--disallow-any-expr",          # default: False
        # "--disallow-any-decorated",     # default: False
        # "--disallow-any-explicit",      # default: False
        # "--disallow-any-generics",      # default: False
        # "--disallow-subclassing-any",   # default: False

        ### Untyped definitions and calls
        "--disallow-untyped-calls",       # default: False
        # "--untyped-calls-exclude",      # default: str call, call, ...
        "--disallow-untyped-defs",        # default: False
        "--disallow-incomplete-defs",     # default: False
        # "--check-untyped-defs",         # default: False
        "--disallow-untyped-decorators",  # default: False

        ###  None and Optional handling
        # "--implicit-optional",          # default: False
        # "--strict-optional",            # default: False

        ###  Configuring warnings
        "--warn-redundant-casts",         # default: False
        # "--warn-unused-ignores",        # default: False
        "--warn-no-return",               # default: False
        # "--warn-return-any",            # default: False
        "--warn-unreachable",             # default: False

        ### Suppressing errors
        # "--ignore-errors",              # default: False

        ### Miscellaneous strictness flags
        # "--allow-untyped-globals",      # default: False
        "--allow-redefinition",           # default: False
        # "--local-partial-types",        # default: False
        # "--disable-error-code",         # default: str error, error, ...
        # "--enable-error-code",          # default: str error, error, ...
        "--extra-checks",                 # default: False
        # "--implicit-reexport",          # default: True
        # "--strict-concatenate",         # default: False
        # "--strict",                     # default: False

        ### Configuring error messages
        # "--show-error-context"          # default: False
        # "--show-column-numbers",        # default: False
        # "--show-error-code-links".      # default: False
        # "--hide-error-codes",           # default: False
        # "--show-error-end",             # default: False
        # "--pretty",                     # default: False
        # "--error-summary",              # default: True
        # "--show-absolute-path",         # default: False
        "--force-uppercase-builtins",     # default: False
        # "--force-union-syntax",         # default: False

        ### Advanced options
        # "--plugins",                    # default: [str] plugin, plugin, ...
        # "--pdb",                        # default: False
        # "--show-traceback",             # default: False
        # "--raise-exceptions",           # default: False
        # "--custom-typing-module",       # default: str
        # "--custom-typeshed-dir",        # default: str
        # "--warn-incomplete-stub",       # default: False

        ### Report generation
        # "--any-exprs-report",           # default: str
        # "--cobertura-xml-report",       # default: str
        # "--html-report",                # default: str
        # "--xslt-html-report",           # default: str
        # "--linecount-report",           # default: str
        # "--linecoverage-report",        # default: str
        # "--lineprecision-report",       # default: str
        # "--txt-report",                 # default: str
        # "--xslt-txt-report",            # default: str
        # "--xml-report",                 # default: str

        ### Miscellaneous
        # "--junit-xml",                  # default: str
        # "--scripts-are-modules",        # default: False
        # "--warn-unused-configs",        # default: False
        # "--verbosity",                  # default: 0

        ### Miscellaneous strictness flags
        "--strict-equality",
        # "--allow-untyped-globals",
        # "--local-partial-types",

        # strict mode enables the following flags:
        #     --warn-unused-configs
        #     --disallow-untyped-calls
        #     --disallow-untyped-defs
        #     --disallow-incomplete-defs
        #     --check-untyped-defs
        #     --no-implicit-optional
        #     --warn-redundant-casts
        #     --warn-return-any
        #     --warn-unused-ignores
        #     --disallow-subclassing-any
        #     --disallow-untyped-decorators

        # Advanced options
        # "--show-traceback", # -> fatal error

        # Enabling incomplete/experimental features
        # "--enable-incomplete-feature", # Tuple[int, ...]
    ]

    start = time.time()

    if not src_path.exists():
        print(f"Error: path '{src_path}' not found ")
        return

    name = src_path.stem
    if name == "":
        name = "."

    folder_path = BASE_PATH / RESULT_FOLDER
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

    text =  f"Python:   {sys.version.replace(LINEFEET, ' ')}\n"
    text += f"Platform: {platform.platform()}\n"
    text += f"Date:     {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
    text += f"Path:     {BASE_PATH}\n"
    text += "\n"

    text += "MyPy [version] settings:\n"
    text += f" » Python version {python_version}\n"
    for setting in settings:
        text += f" {setting}\n"
    text += "\n"

    config = "tmp.toml"
    with open(config, "w") as config_file:
        config_file.write(configuration)

    result = subprocess.run(["mypy", str(src_path), "--config-file", "tmp.toml", "--verbose"] + settings, capture_output=True, text=True)

    os.remove(config)

    sources = []
    version = ""
    for line in result.stderr.splitlines():
        if "Mypy Version:" in line:
            version = line.split("Mypy Version:")[-1].strip()
            text = text.replace("[version]", version)

        if "Found source:" in line:
            pattern = r"path='([^']*)'"
            matches = re.search(pattern, line)
            if matches:
                path = matches.group(1).replace("\\\\", "/")
                # if not path.endswith("__init__.py"):
                sources.append(path)
            continue

    text += "Source files:\n"
    for source in sources:
        text += f" - {source}\n"
    text += "\n"

    summary = ""
    current_file = None
    for line in result.stdout.splitlines():
        if line.startswith("Found") or line.startswith("Success"):
            summary = line.strip()

        if line and not line.startswith(" "):
            file_path = line.split(":")[0]
            if file_path != current_file:
                if current_file is not None:
                    text += "\n"
                current_file = file_path

        text += f"{line}\n"

    result_filename = f"mypy-{python_version}-'{name}'.txt"
    with open(folder_path / result_filename, "w", newline="\n") as file:
        file.write(text)

    duration = time.time() - start
    print(f"[MyPy {version} ({duration:.2f} sec)] '{name}': {summary} -> {RESULT_FOLDER}/{result_filename}")
    sys.exit(result.returncode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="static type check with mypy")
    parser.add_argument("path", nargs="?", type=str, default=".", help="relative path to a file or folder")
    parser.add_argument("-v", "--version", type=str, default="", help="Python version 3.10/3.11/...")

    args = parser.parse_args()

    try:
        run_mypy(Path(args.path), args.version)
    except KeyboardInterrupt:
        print(" --> KeyboardInterrupt")
        sys.exit(1)