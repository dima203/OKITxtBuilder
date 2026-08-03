import textwrap
from datetime import datetime
from simple_table_dima203 import Table

from log import logger
from core.settings import SETTINGS


class RaschetList:
    def __init__(self, max_width: int) -> None:
        self.max_width = max_width
        self.table = Table(keys=[
            "Наименование платежа",
            "Месяц",
            "Начислено",
            "Удержано",
            "Прим",
            "Дн",
            "Час",
        ])
        self.table.wrap = SETTINGS.FEW_LINES_OUTPUT
        self.table.max_table_width = self.max_width
        self.table.style.vertical_character = "∙"
        self.table.title_border = True
        self.table.title_align = "<"

        self.table.align["Наименование платежа"] = "<"
        self.table.align["Прим"] = "<"
        self.table.align["Начислено"] = ">"
        self.table.align["Удержано"] = ">"
        self.table.align["Месяц"] = ">"
        self.table.align["Дн"] = "<"
        self.table.align["Час"] = "<"

        self.table.max_width["Наименование платежа"] = 30

        self.table.min_width["Начислено"] = 9

        self.table.min_width["Удержано"] = 8

        self.table.min_width["Прим"] = 4

        self.table.max_width["Месяц"] = 5
        self.table.min_width["Месяц"] = 5

        self.table.max_width["Дн"] = 2
        self.table.min_width["Дн"] = 2

        self.table.max_width["Час"] = 6
        self.table.min_width["Час"] = 3

        self.name = ""
        self.tabel_number = "-"
        self.otdel = ""
        self.otdel_code = ""
        self.month = ""
        self.year = 0
        self.salary = 0
        self.rate = 0
        self.start_period = 0
        self.is_income = True

    def add_table_row(self, row: list) -> None:
        row = self._process_row(row)
        if "".join(row[1:]) == "":
            self.table.add_delimiter(self._position_formatter(row[0]))
        elif self.is_income and row[2] == "" and row[3] != "":
            self.table.add_delimiter()
            self.is_income = False
        elif row[0].startswith("ИТОГО"):
            self.table.add_delimiter(row[0])
        else:
            self.table.add_row(row)

    def set_name(self, name: str) -> None:
        self.name = name

    def set_tabel_number(self, tabel_number: str) -> None:
        self.tabel_number = tabel_number

    def set_otdel(self, otdel: str) -> None:
        self.otdel = otdel

    def set_otdel_code(self, otdel_code: str) -> None:
        self.otdel_code = otdel_code

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
        return len(str(self).split("\n"))

    def get_width(self) -> int:
        calculated_max = max(
            len(str(self.table).split("\n")[0]),
            len(f"{self.name} таб. № {self.tabel_number}") + 2,
            len(f"Подразделение {self.otdel}") + 2,
        )
        return calculated_max if calculated_max <= self.max_width else self.max_width

    def __str__(self) -> str:
        self.table.min_table_width = self.get_width()

        self.table.supertitle = SETTINGS.BLOCK_TITLE
        self.table.title = f'''Расчетный листок за {self.month} {self.year}г.
{self.name} таб. № {self.tabel_number}
Подразделение {self.otdel}
Оклад/Тариф {self._number_formatter(str(self.salary))} Ставка {self.rate}
На начало периода {self._number_formatter(str(self.start_period))}'''

        return (
                str(self.table) + "\n"
        ).replace(self.table.style.horizontal_character * 2, self.table.style.horizontal_character + " ")

    @logger.catch
    def _process_row(self, row: list) -> list:
        assert len(row) == len(self.table.keys)

        return [
            self._name_formatter(row[0]),
            self._date_formatter(row[4]),
            self._number_formatter(row[5]),
            self._number_formatter(row[6]),
            row[1],
            row[2],
            row[3],
        ]

    @staticmethod
    def _name_formatter(value: str) -> str:
        code, *text = value.strip().split(" ")
        text = " ".join(text)
        if code[0].isnumeric():
            text = f"{code: <4} {text}"
        else:
            text = f"{code} {text}"

        return text

    # def _title_length_formatter(self, title_string: str) -> str:
    #     title_string = self._length_formatter(title_string, self.max_width - 2)
    #     if len(title_string.split("\n")) > 1:
    #         formatted_string = []
    #         for string in title_string.split("\n"):
    #             formatted_string.append(
    #                 f"{self.table.style.vertical_character}{string: <{self.max_width - 2}}{self.table.style.vertical_character}"
    #             )
    #         formatted_string = "\n".join(formatted_string)
    #     else:
    #         formatted_string = f"{self.table.style.vertical_character}{title_string: <{self.get_width() - 2}}{self.table.style.vertical_character}"
    #     return formatted_string

    @staticmethod
    def _position_formatter(value: str) -> str:
        index = value.find("(СП ОАО БРЕСТГАЗОАППАРАТ/")
        return value[:index].strip()

    @staticmethod
    def _length_formatter(value: str, max_length: int) -> str:
        return textwrap.fill(
            value,
            max_length,
            placeholder="",
            max_lines=None if SETTINGS.FEW_LINES_OUTPUT else 1,
        )

    @staticmethod
    def _date_formatter(value: str) -> str:
        try:
            return f"{datetime.strptime(value, '%d.%m.%Y').strftime('%m/%y')}"
        except ValueError:
            try:
                return f"{datetime.strptime(value, '%m.%Y').strftime('%m/%y')}"
            except ValueError:
                return ""

    @staticmethod
    def _number_formatter(value: str) -> str:
        value = value.replace(",", ".")
        try:
            return f"{float(value):_.2f}".replace("_", " ")
        except ValueError:
            return ""
