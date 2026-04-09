from typing import Generator, Self

from log import logger


class FileReader:
    def __init__(self, path: str) -> None:
        self.file_path = path
        self.__file = None

    def read_block(self) -> Generator:
        is_block_start = False
        block = []
        lines = 0

        for line in self.__file:
            lines += 1
            if line.strip() == "СП ОАО Брестгазоаппарат":
                if is_block_start:
                    yield lines, block
                    block.clear()
                    lines = 0

                is_block_start = True

            if is_block_start:
                block.append(line.lstrip().replace(" ", ""))
        else:
            yield lines, block

    @logger.catch
    def __enter__(self) -> Self:
        self.__file = open(self.file_path, "r")
        return self

    @logger.catch
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__file.close()
