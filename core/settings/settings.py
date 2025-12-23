import dataclasses
import configparser
import os
import sys

from log import logger


@dataclasses.dataclass
class Settings:
    SHEET_HEIGHT: int = 92
    SHEET_WIDTH: int = 231
    FEW_LINES_OUTPUT: bool = True
    OPTIMIZE_SORT: bool = True
    OKI_PARAMETER_LINE: str = ""
    OKI_END_SHEET_LINE: str = ""


def load_settings() -> Settings:
    if getattr(sys, "frozen", False):
        bundle_dir = os.path.dirname(sys.executable)
    else:
        bundle_dir = os.getcwd()

    config = configparser.ConfigParser()
    config.read(rf"{bundle_dir}\settings.ini")

    try:
        settings = Settings(
            config.getint("SHEET", "height"),
            config.getint("SHEET", "width"),
            config.getboolean("SHEET", "few_lines_output"),
            config.getboolean("SHEET", "optimize_sort"),
        )
    except KeyError:
        logger.warning(
            rf"Settings file: {bundle_dir}\settings.ini not found. Using default settings."
        )
        settings = Settings()

    with open(
        rf"{bundle_dir}/OKI/OK{settings.SHEET_HEIGHT}_{settings.SHEET_WIDTH}", "r"
    ) as f:
        settings.OKI_PARAMETER_LINE = f.readline()

    with open(rf"{bundle_dir}/OKI/OK_END_SHEET", "r") as f:
        settings.OKI_END_SHEET_LINE = f.readline()

    return settings


SETTINGS = load_settings()
