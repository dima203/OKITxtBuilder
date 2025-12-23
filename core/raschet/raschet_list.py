from prettytable import PrettyTable, TableStyle
import textwrap
from datetime import datetime
from simple_table_dima203 import Table

from log import logger
from core.settings import SETTINGS


class RaschetList:
    def __init__(self, max_width: int) -> None:
        self.max_width = max_width
        self.table = Table(headers=[
            "Наименование платежа",
            "Месяц",
            "Начислено",
            "Удержано",
            "Прим",
            "Дн",
            "Час",
        ])
        self.table.vertical_character = ":"
        # self.table.padding_width = 0
        # self.table.left_padding_width = 0
        # self.table.right_padding_width = 0
        self.table.align["Наименование платежа"] = "<"
        self.table.max_width["Наименование платежа"] = self.max_width // 3
        # self.table.none_format["Прим."] = ""
        # self.table.none_format["Начислено"] = ""
        # self.table.none_format["Удержано"] = ""
        self.table.align["Прим"] = "<"
        self.table.align["Начислено"] = ">"
        self.table.align["Удержано"] = ">"
        self.table.align["Месяц"] = ">"
        self.table.max_width["Месяц"] = 5
        self.table.align["Дн"] = "<"
        self.table.max_width["Дн"] = 2
        self.table.align["Час"] = "<"
        self.table.max_width["Час"] = 3

        self.name = ""
        self.tabel_number = 0
        self.otdel = ""
        self.month = ""
        self.year = 0
        self.salary = 0
        self.rate = 0
        self.start_period = 0

    def add_table_row(self, row: list) -> None:
        row = self._process_row(row)
        # if row[0].startswith("ИТОГО"):
        #     self.table.add_divider()
        # else:
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
        return len(str(self).split("\n")) + 1

    def get_width(self) -> int:
        calculated_max = max(
            len(str(self.table).split("\n")[0]),
            len(f"{self.name} таб. № {self.tabel_number}") + 2,
            len(f"Подразделение {self.otdel}") + 2,
        )
        return calculated_max if calculated_max <= self.max_width else self.max_width

    def __str__(self) -> str:
        min_width = self.get_width()
        self.table.min_table_width = min_width

        return (
            f"""{self.table.top_left_junction_character}{"СП ОАО Брестгазоаппарат":{self.table.horizontal_character}^{self.get_width() - 2}}{self.table.top_right_junction_character}
{self.table.vertical_character}{f"Расчетный листок за {self.month} {self.year}г.": <{self.get_width() - 2}}{self.table.vertical_character}
{self._title_length_formatter(f"{self.name} таб. № {self.tabel_number}")}
{self.table.vertical_character}{"": <{self.get_width() - 2}}{self.table.vertical_character}
{self._title_length_formatter(f"Подразделение {self.otdel}")}
{self.table.vertical_character}{f"Оклад/Тариф {self._number_formatter(str(self.salary))} Ставка {self.rate}": <{self.get_width() - 2}}{self.table.vertical_character}
{self.table.vertical_character}{"На начало периода":<{(self.get_width() - 3) // 2}}{self._number_formatter(str(self.start_period)):>{(self.get_width() - 3) // 2 if (self.get_width() - 3) % 2 == 0 else (self.get_width() - 3) // 2 + 1}} {self.table.vertical_character}
"""
            + str(self.table)
            .replace(self.table.top_left_junction_character, self.table.left_junction_character)
            .replace(self.table.top_right_junction_character, self.table.right_junction_character)
        ).replace(self.table.horizontal_character * 2, self.table.horizontal_character + " ")

    @logger.catch
    def _process_row(self, row: list) -> list:
        assert len(row) == len(self.table.headers)

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
        code, *text = value.strip().split(" ")
        text = " ".join(text)
        if code[0].isnumeric():
            text = f"{code: <3} {text}"
        elif code == "Оклад":
            text = f"    {code} {text}"
        else:
            text = f"{code} {text}"

        return text

    def _title_length_formatter(self, title_string: str) -> str:
        title_string = self._length_formatter(title_string, self.max_width - 2)
        if len(title_string.split("\n")) > 1:
            formatted_string = []
            for string in title_string.split("\n"):
                formatted_string.append(
                    f"{self.table.vertical_character}{string: <{self.max_width - 2}}{self.table.vertical_character}"
                )
            formatted_string = "\n".join(formatted_string)
        else:
            formatted_string = f"{self.table.vertical_character}{title_string: <{self.get_width() - 2}}{self.table.vertical_character}"
        return formatted_string

    def _length_formatter(self, value: str, max_length: int) -> str:
        return textwrap.fill(
            value,
            max_length,
            placeholder="",
            max_lines=None if SETTINGS.FEW_LINES_OUTPUT else 1,
        )

    def _date_formatter(self, value: str) -> str:
        try:
            return f"{datetime.strptime(value, '%d.%m.%Y').strftime('%m/%y')}"
        except ValueError:
            try:
                return f"{datetime.strptime(value, '%m.%Y').strftime('%m/%y')}"
            except ValueError:
                return ""

    def _number_formatter(self, value: str) -> str:
        value = value.replace(",", ".")
        try:
            return f"{float(value):_.2f}".replace("_", " ")
        except ValueError:
            return ""
