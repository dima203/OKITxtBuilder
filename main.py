import os
from typing import Self, Generator
from prettytable import PrettyTable, TableStyle
import textwrap
from datetime import datetime
from itertools import zip_longest
from flet import Page, Button, app, FilePicker, FilePickerResultEvent, ElevatedButton, Row, Icons, Text, Column, MainAxisAlignment


SHEET_HEIGHT = 92
SHEET_WIDTH = 231

FEW_LINES_OUTPUT = True
OPTIMISE_SORT = True


class RaschetList:
    def __init__(self, max_width: int, few_lines_output: bool) -> None:
        self.max_width = max_width
        self.few_lines_output = few_lines_output
        self.table = PrettyTable(max_table_width=max_width)
        self.table.field_names = ['Наименование платежа', 'Месяц', 'Начислено', 'Удержано', 'Прим', 'Дн', 'Час']
        self.table.set_style(TableStyle.DEFAULT)
        self.table.vertical_char = ':'
        self.table.padding_width = 0
        self.table.left_padding_width = 0
        self.table.right_padding_width = 0
        self.table.align['Наименование платежа'] = 'l'
        self.table.max_width['Наименование платежа'] = self.max_width // 3
        self.table.none_format['Прим.'] = ''
        self.table.none_format['Начислено'] = ''
        self.table.none_format['Удержано'] = ''
        self.table.align['Прим'] = 'l'
        self.table.align['Начислено'] = 'r'
        self.table.align['Удержано'] = 'r'
        self.table.align['Месяц'] = 'r'
        self.table.min_width['Месяц'] = 5
        self.table.max_width['Месяц'] = 5
        self.table.align['Дн'] = 'l'
        self.table.min_width['Дн'] = 2
        self.table.max_width['Дн'] = 2
        self.table.align['Час'] = 'l'
        self.table.min_width['Час'] = 3
        self.table.max_width['Час'] = 6

        self.name = ''
        self.tabel_number = 0
        self.otdel = ''
        self.month = ''
        self.year = 0
        self.salary = 0
        self.rate = 0
        self.start_period = 0

    def add_table_row(self, row: list) -> None:
        row = self._process_row(row)
        if row[0].startswith("ИТОГО"):
            self.table.add_divider()
        else:
            self.table.add_row(row)

    def set_name(self, name: str) -> None:
        self.name = name

    def set_tabel_number(self, tabel_number: int) -> None:
        self.tabel_number = tabel_number

    def set_otdel(self, otdel: str) -> None:
        self.otdel = otdel

    def set_month(self, month: str, year: int) -> None:
        self.month = month
        self.year = year

    def set_salary(self, salary: float) -> None:
        self.salary = salary

    def set_rate(self, rate: float) -> None:
        self.rate = rate

    def set_start_period(self, start_period: float) -> None:
        self.start_period = start_period

    def get_height(self) -> int:
        return len(str(self).split('\n')) + 1

    def get_width(self) -> int:
        return max(
            len(self.table.get_string().split('\n')[0]),
            len(f'{self.name} таб. № {self.tabel_number}') + 2,
            len(f'Подразделение {self.otdel}') + 2,
        )

    def __str__(self) -> str:
        min_width = self.get_width()
        self.table.min_table_width = min_width
        return (f'''{self.table.top_left_junction_char}{'СП ОАО Брестгазоаппарат':{self.table.horizontal_char}^{self.get_width()-2}}{self.table.top_right_junction_char}
{self.table.vertical_char}{f'Расчетный листок за {self.month} {self.year}г.': <{self.get_width()-2}}{self.table.vertical_char}
{self.table.vertical_char}{f'{self.name} таб. № {self.tabel_number}': <{self.get_width()-2}}{self.table.vertical_char}
{self.table.vertical_char}{'': <{self.get_width()-2}}{self.table.vertical_char}
{self.table.vertical_char}{f'Подразделение {self.otdel}': <{self.get_width()-2}}{self.table.vertical_char}
{self.table.vertical_char}{f'Оклад/Тариф {self._number_formatter(str(self.salary))} Ставка {self.rate}': <{self.get_width()-2}}{self.table.vertical_char}
{self.table.vertical_char}{'На начало периода':<{(self.get_width() - 3) // 2}}{self._number_formatter(str(self.start_period)):>{(self.get_width() - 3) // 2 if (self.get_width() - 3) % 2 == 0 else (self.get_width() - 3) // 2 + 1}} {self.table.vertical_char}
''' +
            self.table.get_string().replace(self.table.top_left_junction_char, self.table.left_junction_char).replace(self.table.top_right_junction_char, self.table.right_junction_char)
        ).replace(self.table.horizontal_char*2, self.table.horizontal_char + ' ')

    def _process_row(self, row: list) -> list:
        assert len(row) == len(self.table.field_names)
        """[NAME, %, DAY, HOUR, PERIOD, NACH, UDER]"""

        return [
            self._name_formatter(row[0]),
            self._date_formatter(row[4]),
            self._number_formatter(row[5]),
            self._number_formatter(row[6]),
            row[1],
            row[2],
            row[3],
        ]

    def _name_formatter(self, value: str) -> str:
        code, *text = value.strip().split(' ')
        text = ' '.join(text)
        if code[0].isnumeric():
            text = f'{code: <3} {text}'
        elif code == 'Оклад':
            text = f'    {code} {text}'
        else:
            text = f'{code} {text}'

        return text

    def _length_formatter(self, value: str, max_length) -> str:
        return textwrap.fill(
            value,
            max_length,
            placeholder='',
            max_lines=None if self.few_lines_output else 1,
        )

    def _date_formatter(self, value: str) -> str:
        try:
            return f'{datetime.strptime(value, "%d.%m.%Y").strftime("%m/%y")}'
        except ValueError:
            try:
                return f'{datetime.strptime(value, "%m.%Y").strftime("%m/%y")}'
            except ValueError:
                return ''

    def _number_formatter(self, value: str) -> str:
        value = value.replace(',', '.')
        try:
            return f'{float(value):_.2f}'.replace('_', ' ')
        except ValueError:
            return ''


class FileReader:
    def __init__(self, path: str) -> None:
        self.file_path = path
        self.__file = None

    def read_block(self) -> Generator:
        is_block_start = False
        block = []

        for line in self.__file:
            if line.strip() == 'СП ОАО Брестгазоаппарат':
                if is_block_start:
                    yield block
                    block.clear()

                is_block_start = True

            if is_block_start:
                block.append(line.lstrip().replace(' ', ''))
        else:
            yield block

    def __enter__(self) -> Self:
        self.__file = open(self.file_path, 'r')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__file.close()


class FileWriter:
    def __init__(self, path: str) -> None:
        self.file_path = path
        self.__file = None

    def write(self, line: str) -> None:
        self.__file.write(line)

    def __enter__(self) -> Self:
        self.__file = open(self.file_path, 'w', encoding='OEM')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        with open(f"{os.path.dirname(__file__)}/OKI/OK_END_SHEET", 'r') as parameter_file:
            self.__file.write(parameter_file.readline())
        self.__file.close()


class SheetBuilder:
    def __init__(self, sheet_width: int, sheet_height: int, few_lines_output: bool) -> None:
        self.raschet_lists: list[RaschetList] = []
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.one_column_width = sheet_width // 3
        self.few_lines_output = few_lines_output

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
        with open(f"{os.path.dirname(__file__)}/OKI/OK{self.sheet_height}_{self.sheet_width}", 'r') as parameter_file:
            lines.append(parameter_file.readline())

        if OPTIMISE_SORT:
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

        return lines

    def _get_lines_from_sheet(self, sheet_strings) -> list[str]:
        lines = []
        sheet_lines = list(zip_longest(*sheet_strings, fillvalue=''))
        for line in sheet_lines:
            lines.append(f'{line[0].strip():{self.one_column_width - 1}} {line[1].strip():{self.one_column_width - 1}} {line[2].strip():{self.one_column_width - 1}}\n')
        with open(f"{os.path.dirname(__file__)}/OKI/OK_END_SHEET", 'r') as parameter_file:
            lines.append(parameter_file.readline())
        return lines

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


def main(page: Page):
    page.title = "Подготовка файла к печати"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.window.width = 500
    page.window.height = 500
    page.window.resizable = False
    page.window.center()
    page.update()
    sheet_builder = SheetBuilder(SHEET_WIDTH, SHEET_HEIGHT, FEW_LINES_OUTPUT)

    def pick_file_result(e: FilePickerResultEvent):
        sheet_builder.read(e.files[0].path)
        selected_files.value = e.files[0].path
        selected_files.update()

    def save_file_result(e: FilePickerResultEvent):
        sheet_builder.write(e.path)
        result_text.value = 'Готово'
        result_text.update()

    pick_file_dialog = FilePicker(on_result=pick_file_result)
    save_file_dialog = FilePicker(on_result=save_file_result)
    selected_files = Text()
    result_text = Text()

    page.overlay.append(pick_file_dialog)
    page.overlay.append(save_file_dialog)

    page.add(
        Column(
            height=page.window.height,
            alignment=MainAxisAlignment.CENTER,
            spacing=30,
            controls=[
                Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ElevatedButton(
                            "Файл",
                            width=300,
                            height=70,
                            icon=Icons.UPLOAD_FILE,
                            on_click=lambda _: pick_file_dialog.pick_files(),
                        ),
                        selected_files,
                    ]
                ),
                Row(
                    alignment=MainAxisAlignment.CENTER,
                    controls=[
                        ElevatedButton(
                            "Сохранить",
                            width=300,
                            height=70,
                            icon=Icons.SAVE,
                            on_click=lambda _: save_file_dialog.save_file(),
                        ),
                        result_text,
                    ]
                )
            ]
        )
    )


app(main)
