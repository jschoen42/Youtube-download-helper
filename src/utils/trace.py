"""
    PUBLIC:
    remove_colors(text: str) -> str:

    class Trace:

        Trace.set(appl_folder="/trace/", debug_mode=False, reduced_mode=False, show_timestamp=True, time_zone='')

        Trace.start(["action", "result", "warning", "error"], csv=False) # csv with TAB instead of comma
        Trace.end("./logs", "testTrace")

        Trace.action()
        Trace.result()
        Trace.empty()    # not in reduced mode
        Trace.info()     # not in reduced mode
        Trace.update()   # not in reduced mode
        Trace.download() # not in reduced mode

        Trace.warning()
        Trace.error()
        Trace.exception()
        Trace.fatal()

        Trace.debug()    # only in debug mode
        Trace.wait()     # only in debug mode

  class ProcessLog (array cache)
    - add
    - get

"""

import sys
import os
import re
import inspect

from typing import Any
from enum import StrEnum
from pathlib import Path
from datetime import datetime

from pytz import timezone

#DEFAULT_TIMEZONE = "UTC"
DEFAULT_TIMEZONE = "Europe/Berlin"

# https://en.wikipedia.org/wiki/ANSI_escape_code#Colors

class Color(StrEnum):
    RESET         = "\033[0m"
    BOLD          = "\033[1m"
    DISABLE       = "\033[2m"
    ITALIC        = "\033[3m"
    UNDERLINE     = "\033[4m"
    INVERSE       = "\033[7m"
    INVISIBLE     = "\033[8m"
    STRIKETHROUGH = "\033[9m"
    NORMAL        = "\033[22m"

    BLACK         = "\033[30m"
    RED           = "\033[31m"
    GREEN         = "\033[32m"
    BLUE          = "\033[34m"
    PURPLE        = "\033[35m"
    CYAN          = "\033[36m"

    BLACK_BG      = "\033[40m"
    RED_BG        = "\033[41m"
    GREEN_BG      = "\033[42m"
    BLUE_BG       = "\033[44m"
    PURPLE_BG     = "\033[45m"
    CYAN_BG       = "\033[46m"

def remove_colors(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text)

pattern = {
    "action":    " >>> ",
    "result":    " ==> ",

    "empty":     "-----", # no text
    "info":      "-----",
    "update":    "+++++",
    "download":  ">>>>>",

    "warning":   "*****",
    "error":     "#####",
    "exception": "!!!!!",
    "fatal":     "FATAL",

    "debug":     "@@@@@",
    "wait":      "WAIT ", # only in debug mode
}

class Trace:
    default_base_folder = os.getcwd().replace("\\", "/").split("/")[-1]

    settings = {
        "appl_folder":   "/" + default_base_folder + "/",

        "reduced_mode":   False,
        "debug_mode":     False,

        "show_timestamp": True,
        "show_caller":    True,
        "time_zone":      DEFAULT_TIMEZONE,
    }

    pattern:list[str]  = []
    messages:list[str] = []
    csv = False

    @classmethod
    def set(cls, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in cls.settings:
                cls.settings[key] = value
            else:
                print(f"trace settings: unknown parameter {key}")

    @classmethod
    def file_init(cls, pattern_list: None | list = None, csv: bool = False) -> None:
        if pattern_list is None:
            cls.pattern = []
        else:
            cls.pattern = pattern_list
        cls.csv = csv
        cls.messages = []

    @classmethod
    def file_save(cls, path: Path | str, filename: str) -> None:
        trace_path = Path(path)

        text = ""
        for message in Trace.messages:
            text += message + "\n"

        curr_time = datetime.now(timezone(cls.settings["time_zone"])).strftime("%Y-%d-%m_%H-%M-%S")
        try:
            if not trace_path.is_dir():
                os.makedirs(path)

            with open(Path(trace_path, filename + "_" + curr_time + ".txt"), "w", encoding="utf-8") as file:
                file.write(text)

        except OSError as err:
            Trace.error(f"[trace_end] write {err}")

        cls.messages = []

    # action, result, empty, info, update, download

    @classmethod
    def action(cls, message: str, *optional: Any) -> None:
        pre = f"{cls.__get_time()}{cls.__get_pattern()}{cls.__get_caller()}"
        cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def result(cls, message: str, *optional: Any) -> None:
        pre = f"{cls.__get_time()}{cls.__get_pattern()}{cls.__get_caller()}"
        cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def empty(cls):
        if not cls.settings["reduced_mode"]:
            pre = f"{cls.__get_time()}{cls.__get_pattern()}"
            cls.__show_message(cls.__check_file_output(), pre, "")

    @classmethod
    def info(cls, message: str, *optional: Any) -> None:
        if not cls.settings["reduced_mode"]:
            pre = f"{cls.__get_time()}{cls.__get_pattern()}{cls.__get_caller()}"
            cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def update(cls, message: str, *optional: Any) -> None:
        if not cls.settings["reduced_mode"]:
            pre = f"{cls.__get_time()}{cls.__get_pattern()}{cls.__get_caller()}"
            cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def download(cls, message: str, *optional: Any) -> None:
        if not cls.settings["reduced_mode"]:
            pre = f"{cls.__get_time()}{cls.__get_pattern()}{cls.__get_caller()}"
            cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    # warning, error, exception, fatal => RED

    @classmethod
    def warning(cls, message: str, *optional: Any) -> None:
        pre = f"{cls.__get_time()}{cls.__get_pattern()}{cls.__get_caller()}"
        cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def error(cls, message: str, *optional: Any) -> None:
        pre = f"{cls.__get_time()}{Color.RED}{cls.__get_pattern()}{cls.__get_caller()}"
        cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def exception(cls, message: str, *optional: Any) -> None:
        pre = f"{cls.__get_time()}{Color.RED}{cls.__get_pattern()}{cls.__get_caller()}"
        cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def fatal(cls, message: str, *optional: Any) -> None:
        pre = f"{cls.__get_time()}{Color.RED}{Color.BOLD}{cls.__get_pattern()}{cls.__get_caller()}"
        cls.__show_message(cls.__check_file_output(), pre, message, *optional)
        raise SystemExit

    # debug, wait

    @classmethod
    def debug(cls, message: str, *optional: Any) -> None:
        if cls.settings["debug_mode"] and not cls.settings["reduced_mode"]:
            pre = f"{cls.__get_time()}{cls.__get_pattern()}{cls.__get_caller()}"
            cls.__show_message(cls.__check_file_output(), pre, message, *optional)

    @classmethod
    def wait(cls, message: str, *optional: Any) -> None:
        if cls.settings["debug_mode"]:
            pre = f"{cls.__get_time()}{cls.__get_pattern()} {cls.__get_caller()}"
            cls.__show_message(cls.__check_file_output(), pre, message, *optional)
            try:
                input(f"{Color.RED}{Color.BOLD} >>> Press any key <<< {Color.RESET}")
            except KeyboardInterrupt:
                sys.exit()

    @classmethod
    def __show_message(cls, file_output: bool, pre: str, message: str, *optional: Any) -> None:
        extra = ""
        for opt in optional:
            extra += " > " + str(opt)

        text = f"{pre}{message}{extra}"
        text_no_tabs = text.replace("\t", " ")

        if file_output: # remove all colors
            if cls.csv:
                cls.messages.append(remove_colors(text))
            else:
                cls.messages.append(remove_colors(text_no_tabs))

        print(text_no_tabs)

    @classmethod
    def __get_time(cls) -> str:
        if cls.settings["show_timestamp"]:
            return f"{Color.BLACK}{datetime.now(timezone(cls.settings['time_zone'])).strftime('%H:%M:%S.%f')[:-3]}{Color.RESET}\t"
        return ""

    @classmethod
    def __get_caller(cls) -> str:
        if cls.settings["show_caller"] is False:
            return f"{Color.RESET} "

        path = inspect.stack()[2][1].replace("\\", "/")
        path = path.split(cls.settings["appl_folder"])[-1]

        lineno = str(inspect.currentframe().f_back.f_back.f_lineno).zfill(3)

        caller = inspect.currentframe().f_back.f_back.f_code.co_qualname # .co_qualname (erst ab 3.11)
        caller = caller.replace(".<locals>.", " → ")

        if caller == "<module>":
            return f"\t{Color.BLUE}[{path}:{lineno}]{Color.RESET}\t"
        else:
            return f"\t{Color.BLUE}[{path}:{lineno} » {caller}]{Color.RESET}\t"

    @classmethod
    def __check_file_output(cls) -> bool:
        trace_type = inspect.currentframe().f_back.f_code.co_name
        return trace_type in list(cls.pattern)

    @staticmethod
    def __get_pattern() -> str:
        trace_type = inspect.currentframe().f_back.f_code.co_name
        if trace_type in pattern:
            return pattern[trace_type]
        else:
            return "     "

#######################

class ProcessLog:
    def __init__(self):
        self.log = []

    def add(self, info):
        self.log.append(info)

    def get(self):
        return self.log
