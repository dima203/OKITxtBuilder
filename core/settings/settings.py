import dataclasses
import configparser
import os


@dataclasses.dataclass
class Settings:
    SHEET_HEIGHT: int = 92
    SHEET_WIDTH: int = 231
    FEW_LINES_OUTPUT: bool = True
    OPTIMIZE_SORT: bool = True
    OKI_PARAMETER_LINE: str = ''
    OKI_END_SHEET_LINE: str = ''


def load_settings() -> Settings:
    config = configparser.ConfigParser()
    config.read("settings.ini")

    settings = Settings(
        int(config['SHEET']['height']),
        int(config['SHEET']['width']),
        bool(config['SHEET']['few_lines_output']),
        bool(config['SHEET']['optimize_sort']),
    )

    with open(f"{os.getcwd()}/OKI/OK{settings.SHEET_HEIGHT}_{settings.SHEET_WIDTH}", 'r') as f:
        settings.OKI_PARAMETER_LINE = f.readline()

    with open(f"{os.getcwd()}/OKI/OK_END_SHEET", 'r') as f:
        settings.OKI_END_SHEET_LINE = f.readline()

    return settings


SETTINGS = load_settings()
