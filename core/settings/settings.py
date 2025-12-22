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
    OKI_PARAMETER_LINE: str = ''
    OKI_END_SHEET_LINE: str = ''


@logger.catch
def load_settings() -> Settings:
    if getattr(sys, 'frozen', False):
        bundle_dir = os.path.dirname(sys.executable)
    else:
        bundle_dir = os.getcwd()

    config = configparser.ConfigParser()
    config.read(f"{bundle_dir}/settings.ini")

    settings = Settings(
        int(config['SHEET']['height']),
        int(config['SHEET']['width']),
        bool(config['SHEET']['few_lines_output']),
        bool(config['SHEET']['optimize_sort']),
    )

    with open(f"{bundle_dir}/OKI/OK{settings.SHEET_HEIGHT}_{settings.SHEET_WIDTH}", 'r') as f:
        settings.OKI_PARAMETER_LINE = f.readline()

    with open(f"{bundle_dir}/OKI/OK_END_SHEET", 'r') as f:
        settings.OKI_END_SHEET_LINE = f.readline()

    return settings


SETTINGS = load_settings()
