from tqdm import tqdm

import timeit
import functools
import asyncio
from itertools import zip_longest

from filework import FileReader, FileWriter
from log import logger

from .settings import SETTINGS
from .raschet import RaschetList
from .sorting import Packager, Sorter, Column


def time_count(func):
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        start = timeit.default_timer()
        try:
            return func(*args, **kwargs)
        finally:
            logger.info(f"{func.__name__} Время выполнения: {timeit.default_timer() - start:.2f}")
    return wrap


class SheetBuilder:
    def __init__(self) -> None:
        self.raschet_lists: list[RaschetList] = []
        self.sheet_width = SETTINGS.SHEET_WIDTH
        self.sheet_height = SETTINGS.SHEET_HEIGHT
        self.one_column_width = SETTINGS.SHEET_WIDTH // 3

    async def read(self, input_file_path: str, on_progress=None) -> None:
        logger.info(f"Начало чтения файла: `{input_file_path}`")
        self.raschet_lists.clear()

        with open(input_file_path, "rb") as f:
            num_lines = sum(1 for _ in f)

        with FileReader(input_file_path) as reader, tqdm(total=num_lines) as progress:
            for lines, block in reader.read_block():
                progress.set_description(f"Чтение файла")
                progress.update(lines)
                await asyncio.sleep(0.01)
                if on_progress:
                    on_progress(progress.n, progress.total)

                if block:
                    self.raschet_lists.append(self._process_block(block))
        logger.info(f"Файл `{input_file_path}` прочитан. Прочитано {len(self.raschet_lists)} расчетных листов.")

    def write(self, output_file_path: str) -> None:
        with FileWriter(output_file_path) as writer:
            lines = self._get_lines()
            for line in lines:
                writer.write(line)

    def _process_block(self, block: list[str]) -> RaschetList:
        raschet_list = RaschetList(self.one_column_width)
        month, year, *_ = block[2].split("\t")[3].split(" ")
        raschet_list.set_month(month, int(year))
        name, tabel_number = block[4].split(" таб. № ")
        raschet_list.set_name(name)
        raschet_list.set_tabel_number(int(tabel_number))
        raschet_list.set_otdel(block[6].split("\t")[2])
        try:
            raschet_list.set_salary(int(block[8].split("\t")[2]))
            raschet_list.set_rate(float(block[8].split("\t")[9].strip()))
        except ValueError:
            raschet_list.set_salary(0)
            raschet_list.set_rate(0)

        start_period = ""
        for line in block[9:]:
            if line.startswith("На начало периода"):
                start_period = line.split("\t")[8].replace(",", ".")
                if start_period == "":
                    start_period = line.split("\t")[9].replace(",", ".")

        raschet_list.set_start_period(float(start_period))

        start_index = 0
        for i, line in enumerate(block[9:]):
            if line.startswith("Начисление"):
                start_index = i + 3 + 9

        for line in block[start_index:]:
            if line == "":
                continue

            line = line.split("\t")

            raschet_list.add_table_row(line[0:1] + line[4:10])

        return raschet_list

    def _get_lines(self) -> list[str]:
        if SETTINGS.OPTIMIZE_SORT:
            output_lists = self.__sort_lists()
        else:
            output_lists = self._get_columns(self.raschet_lists)

        length = 0
        for column in output_lists:
            length += len(column.items)
        logger.info(f"Всего {length} записей")

        lines = []
        sheet_strings = [[], [], []]

        lines.append(SETTINGS.OKI_PARAMETER_LINE)  # Добавляем в начало файла управляющую строку с параметрами

        with tqdm(total=len(output_lists)) as progress:
            pages = 1
            current_col = 0
            for column in output_lists:
                progress.set_description(f"Обработка {pages} листа")

                for item in column.items:
                    sheet_strings[current_col].extend(str(item).split("\n"))

                progress.update()

                current_col += 1
                if current_col == 3:
                    current_col = 0
                    pages += 1
                    lines.extend(self._get_lines_from_sheet(sheet_strings))
                    sheet_strings = [[], [], []]

            lines.extend(self._get_lines_from_sheet(sheet_strings))
            lines.append(SETTINGS.OKI_END_SHEET_LINE)

        return lines

    @time_count
    def __sort_lists(self) -> list[Column]:
        output_lists = []
        not_optimized = self.raschet_lists.copy()

        # Предварительно упаковываем листы в колонки (работает быстрее сортировки)
        package = Packager(not_optimized, self.sheet_height)
        result = package.run()

        not_optimized = []
        for column in result:
            if column.height != self.sheet_height:
                not_optimized.extend(column.items)
            else:
                output_lists.append(column)
        logger.info(
            f"Предварительная оптимизация: {len(output_lists)} оптимизировано и {len(not_optimized)} не оптимизировано")
        length = 0
        for column in output_lists:
            length += len(column.items)
        logger.info(f"Всего: {length + len(not_optimized)} записей")

        # Сортируем листы в колонки
        sorter = Sorter(not_optimized, self.sheet_height)
        result = sorter.run()

        for column in result:
            output_lists.append(column)

        not_optimized = []
        optimized = []
        for column in result:
            if column.height != self.sheet_height:
                not_optimized.extend(column.items)
            else:
                optimized.extend(column.items)

        logger.info(
            f"Оптимизация: {len(optimized) + length} оптимизировано и {len(not_optimized)} не оптимизировано")

        return output_lists

    def _get_columns(self, items: list[RaschetList]) -> list[Column]:
        result = []

        with tqdm(total=len(items)) as progress:
            current_column = Column([], 0, self.sheet_height)
            column_number = 1
            for raschet_list in items:
                progress.set_description(f"Обработка {column_number} колонки")
                progress.update()

                if current_column.height + raschet_list.get_height() > self.sheet_height:
                    result.append(current_column)
                    current_column = Column([raschet_list], raschet_list.get_height(), self.sheet_height)
                    column_number += 1
                    continue

                current_column.add_item(raschet_list)

            result.append(current_column)

        return result

    def _get_lines_from_sheet(self, sheet_strings: list[list[str]]) -> list[str]:
        lines = []
        sheet_lines = list(zip_longest(*sheet_strings, fillvalue=""))
        for line in sheet_lines:
            lines.append(
                f"{line[0].strip():{self.one_column_width}}{line[1].strip():{self.one_column_width}}{line[2].strip():{self.one_column_width}}\n"
            )

        lines.append(SETTINGS.OKI_END_SHEET_LINE)
        return lines
