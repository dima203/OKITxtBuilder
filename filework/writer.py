from typing import Self

from log import logger


class FileWriter:
    def __init__(self, path: str) -> None:
        self.file_path = path
        self.__file = None

    @logger.catch
    def write(self, line: str) -> None:
        self.__file.write(line)

    @logger.catch
    def __enter__(self) -> Self:
        self.__file = open(self.file_path, 'w', encoding='OEM')
        return self

    @logger.catch
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__file.close()
