from itertools import zip_longest

from filework import FileReader, FileWriter
from log import logger

from .settings import SETTINGS
from .raschet import RaschetList


class SheetBuilder:
    def __init__(self) -> None:
        self.raschet_lists: list[RaschetList] = []
        self.sheet_width = SETTINGS.SHEET_WIDTH
        self.sheet_height = SETTINGS.SHEET_HEIGHT
        self.one_column_width = SETTINGS.SHEET_WIDTH // 3
        self.few_lines_output = SETTINGS.FEW_LINES_OUTPUT

    def read(self, input_file_path: str) -> None:
        self.raschet_lists.clear()
        with FileReader(input_file_path) as reader:
            for block in reader.read_block():
                self.raschet_lists.append(self._process_block(block))

    def write(self, output_file_path: str) -> None:
        with FileWriter(output_file_path) as writer:
            lines = self._get_lines()
            for line in lines:
                writer.write(line)

    def _process_block(self, block: list[str]) -> RaschetList:
        raschet_list = RaschetList(self.one_column_width - 1, self.few_lines_output)
        month, year, *_ = block[2].split('\t')[3].split(' ')
        raschet_list.set_month(month, int(year))
        name, tabel_number = block[4].split(' таб. № ')
        raschet_list.set_name(name)
        raschet_list.set_tabel_number(int(tabel_number))
        raschet_list.set_otdel(block[6].split('\t')[2])
        try:
            raschet_list.set_salary(int(block[8].split('\t')[2]))
            raschet_list.set_rate(float(block[8].split('\t')[9].strip()))
        except ValueError:
            raschet_list.set_salary(0)
            raschet_list.set_rate(0)

        start_period = ''
        for line in block[9:]:
            if line.startswith('На начало периода'):
                start_period = line.split('\t')[8].replace(',', '.')
                if start_period == '':
                    start_period = line.split('\t')[9].replace(',', '.')

        raschet_list.set_start_period(float(start_period))

        start_index = 0
        for i, line in enumerate(block[9:]):
            if line.startswith('Начисление'):
                start_index = i + 3 + 9

        for line in block[start_index:]:
            if line == '':
                continue

            line = line.split('\t')

            raschet_list.add_table_row(line[0:1] + line[4:10])

        return raschet_list

    def _get_lines(self) -> list[str]:
        lines = []
        current_line = 0
        current_col = 0
        sheet_strings = [[], [], []]

        lines.append(SETTINGS.OKI_PARAMETER_LINE)

        if SETTINGS.OPTIMIZE_SORT:
            output_lists = self._optimise_sort()
        else:
            output_lists = self.raschet_lists.copy()

        for raschet_list in output_lists:
            if current_line + raschet_list.get_height() > self.sheet_height:
                current_line = 0
                current_col += 1
                if current_col >= 3:
                    current_col = 0
                    lines.extend(self._get_lines_from_sheet(sheet_strings))
                    sheet_strings[0].clear()
                    sheet_strings[1].clear()
                    sheet_strings[2].clear()

            current_line += raschet_list.get_height()

            sheet_strings[current_col].extend(str(raschet_list).split('\n'))
            sheet_strings[current_col].append('\n')

        lines.extend(self._get_lines_from_sheet(sheet_strings))
        lines.append(SETTINGS.OKI_END_SHEET_LINE)

        return lines

    def _get_lines_from_sheet(self, sheet_strings: list[list[str]]) -> list[str]:
        lines = []
        sheet_lines: list[tuple[str, str, str]] = list(zip_longest(*sheet_strings, fillvalue=''))
        for line in sheet_lines:
            lines.append(f'{line[0].strip():{self.one_column_width - 1}} {line[1].strip():{self.one_column_width - 1}} {line[2].strip():{self.one_column_width - 1}}\n')

        lines.append(SETTINGS.OKI_END_SHEET_LINE)
        return lines

    @logger.catch
    def _optimise_sort(self) -> list[RaschetList]:
        list_copy = self.raschet_lists.copy()
        result_lists = []
        while len(list_copy) > 0:
            result = self.__max_sum_less_or_equal(list_copy, self.sheet_height)
            result_lists.extend(result)
            for el in result:
                list_copy.remove(el)
        return result_lists

    @staticmethod
    def __max_sum_less_or_equal(objects, target_height):
        """
        Находит подмножество объектов с максимальной суммарной высотой ≤ target_height.
        Объекты должны иметь метод get_height(), возвращающий числовое значение.
        """
        if not objects:
            return []

        # Получаем высоты всех объектов
        heights = [obj.get_height() for obj in objects]
        n = len(objects)

        # Создаем таблицу динамического программирования
        # dp[s] - максимальная суммарная высота для ограничения s
        dp = [0] * (target_height + 1)
        # subsets[s] - список объектов, дающих максимальную сумму для ограничения s
        subsets = [[] for _ in range(target_height + 1)]

        for i in range(n):
            height = heights[i]
            for s in range(target_height, height - 1, -1):
                # Проверяем, улучшает ли добавление текущего объекта результат
                if dp[s] < dp[s - height] + height:
                    dp[s] = dp[s - height] + height
                    subsets[s] = subsets[s - height] + [objects[i]]

        # Находим максимальную достижимую сумму
        max_height = dp[target_height]

        # Если максимальная сумма достигнута не при полном target_height,
        # ищем лучшее решение среди всех возможных сумм
        if max_height < target_height:
            # Находим максимальное значение в dp
            max_height = max(dp)
            # Находим индекс, где достигнуто максимальное значение
            best_index = dp.index(max_height)
            return subsets[best_index]

        return subsets[target_height]