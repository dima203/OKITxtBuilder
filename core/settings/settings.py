import dataclasses
import configparser
import os
import sys
from pathlib import Path

from log import logger


@dataclasses.dataclass
class Settings:
    SHEET_HEIGHT: int = 92
    SHEET_WIDTH: int = 231
    COLUMNS_SPACING: int = 1
    FEW_LINES_OUTPUT: bool = True
    OPTIMIZE_SORT: bool = True
    BLOCK_TITLE: str = ""
    OKI_PARAMETER_LINE: str = ""
    OKI_END_SHEET_LINE: str = ""


def load_settings() -> Settings:
    if getattr(sys, "frozen", False):
        bundle_dir = Path(os.path.dirname(sys.executable))
    else:
        bundle_dir = Path(os.getcwd())

    default_dir = bundle_dir / "assets"
    assets_path = Path(os.environ.get("FLET_ASSETS_DIR", str(default_dir)))

    config = configparser.ConfigParser()
    config.read(assets_path /  "settings" / "settings.ini", encoding="utf-8")

    try:
        settings = Settings(
            config.getint("SHEET", "height"),
            config.getint("SHEET", "width"),
            config.getint("SHEET", "columns_spacing"),
            config.getboolean("SHEET", "few_lines_output"),
            config.getboolean("SHEET", "optimize_sort"),
            config.get("BLOCK", "title")
        )
        logger.debug(settings)
    except KeyError:
        logger.warning(
            rf"Settings file: {bundle_dir}\settings.ini not found. Using default settings."
        )
        settings = Settings()

    with open(
        assets_path / "settings" / "OKI" / f"OK{settings.SHEET_HEIGHT}_{settings.SHEET_WIDTH}", "r"
    ) as f:
        settings.OKI_PARAMETER_LINE = f.readline()

    with open(assets_path / "settings" / "OKI" / "OK_END_SHEET", "r") as f:
        settings.OKI_END_SHEET_LINE = f.readline()

    return settings


SETTINGS = load_settings()
