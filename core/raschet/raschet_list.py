from prettytable import PrettyTable, TableStyle
import textwrap
from datetime import datetime

from log import logger
from core.settings import SETTINGS


class RaschetList:
    def __init__(self, max_width: int) -> None:
        self.max_width = max_width
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
        self.table.align['Дн'] = 'l'
        self.table.min_width['Дн'] = 2
        self.table.align['Час'] = 'l'
        self.table.min_width['Час'] = 3

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
        calculated_max = max(
            len(self.table.get_string().split('\n')[0]),
            len(f'{self.name} таб. № {self.tabel_number}') + 2,
            len(f'Подразделение {self.otdel}') + 2,
        )
        return calculated_max if calculated_max <= self.max_width else self.max_width

    def __str__(self) -> str:
        min_width = self.get_width()
        self.table.min_table_width = min_width
        self.table.title = f'''
СП ОАО Брестгазоаппарат
Расчетный листок за {self.month} {self.year}г.
{self.name} таб. № {self.tabel_number}

Подразделение {self.otdel}
Оклад/Тариф {self._number_formatter(str(self.salary))} Ставка {self.rate}
'''

#         return (f'''{self.table.top_left_junction_char}{'СП ОАО Брестгазоаппарат':{self.table.horizontal_char}^{self.get_width()-2}}{self.table.top_right_junction_char}
# {self.table.vertical_char}{f'Расчетный листок за {self.month} {self.year}г.': <{self.get_width()-2}}{self.table.vertical_char}
# {self._title_length_formatter(f'{self.name} таб. № {self.tabel_number}')}
# {self.table.vertical_char}{'': <{self.get_width()-2}}{self.table.vertical_char}
# {self._title_length_formatter(f'Подразделение {self.otdel}')}
# {self.table.vertical_char}{f'Оклад/Тариф {self._number_formatter(str(self.salary))} Ставка {self.rate}': <{self.get_width()-2}}{self.table.vertical_char}
# {self.table.vertical_char}{'На начало периода':<{(self.get_width() - 3) // 2}}{self._number_formatter(str(self.start_period)):>{(self.get_width() - 3) // 2 if (self.get_width() - 3) % 2 == 0 else (self.get_width() - 3) // 2 + 1}} {self.table.vertical_char}
# ''' +
        return  (self.table.get_string().replace(self.table.top_left_junction_char, self.table.left_junction_char).replace(self.table.top_right_junction_char, self.table.right_junction_char)
        ).replace(self.table.horizontal_char*2, self.table.horizontal_char + ' ')

    @logger.catch
    def _process_row(self, row: list) -> list:
        assert len(row) == len(self.table.field_names)

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
        value = self._length_formatter(value, self.max_width // 3 - 4)
        code, *text = value.strip().split(' ')
        text = ' '.join(text)
        if code[0].isnumeric():
            text = f'{code: <3} {text}'
        elif code == 'Оклад':
            text = f'    {code} {text}'
        else:
            text = f'{code} {text}'

        return text

    def _title_length_formatter(self, title_string: str) -> str:
        title_string = self._length_formatter(title_string, self.max_width-2)
        if len(title_string.split('\n')) > 1:
            formatted_string = []
            for string in title_string.split('\n'):
                formatted_string.append(f'{self.table.vertical_char}{string: <{self.max_width - 2}}{self.table.vertical_char}')
            formatted_string = '\n'.join(formatted_string)
        else:
            formatted_string = f'{self.table.vertical_char}{title_string: <{self.get_width() - 2}}{self.table.vertical_char}'
        return formatted_string

    def _length_formatter(self, value: str, max_length: int) -> str:
        return textwrap.fill(
            value,
            max_length,
            placeholder='',
            max_lines=None if SETTINGS.FEW_LINES_OUTPUT else 1,
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
