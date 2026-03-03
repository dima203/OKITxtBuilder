import os
from multiprocessing import Pool
from tqdm import tqdm

from core.raschet import RaschetList

from .column import Column


class Packager:
    """
    Решатель задачи упаковки: распределить все объекты по группам,
    чтобы сумма в каждой группе ≤ target, минимизируя количество групп.
    """

    def __init__(self, items: list[RaschetList], height: int) -> None:
        self.items = items.copy()
        self.height: int = height

    def run(self, mode="FFD") -> list[Column]:
        cpu = os.cpu_count()
        function = None

        match mode:
            case "FFD":
                function = self.first_fit_decreasing
            case "BFD":
                function = self.best_fit_decreasing
            case "WFD":
                function = self.worst_fit_decreasing
            case _:
                function = self.first_fit_decreasing

        with Pool() as p:
            results = p.map(function, [self.items[i::cpu] for i in range(cpu)])

        result = []
        for columns in results:
            result.extend(columns)

        return result

    def first_fit_decreasing(self, objects: list):
        """
        Алгоритм First-Fit Decreasing (FFD).
        Сортирует объекты по убыванию и распределяет их в первый подходящий контейнер.
        """
        # Сортируем объекты по убыванию высоты
        sorted_objects = sorted(objects, key=lambda x: x.get_height(), reverse=True)

        # Создаем первую корзину
        columns: list[Column] = []

        with tqdm(total=len(sorted_objects)) as progress:
            for obj in sorted_objects:
                progress.set_description(f"Упаковка записей")
                obj_height = obj.get_height()

                # Ищем подходящую корзину
                placed = False
                for column in columns:
                    if column.remaining >= obj_height:
                        column.add_item(obj)
                        placed = True
                        break

                # Если не нашли подходящую корзину, создаем новую
                if not placed:
                    columns.append(
                        Column([obj], obj_height, self.height)
                    )
                progress.update()

        return columns

    def best_fit_decreasing(self, objects: list[RaschetList]):
        """
        Алгоритм Best-Fit Decreasing (BFD).
        Сортирует по убыванию и размещает объект в корзину с наименьшим остаточным местом.
        """
        sorted_objects = sorted(objects, key=lambda x: x.get_height(), reverse=True)
        columns: list[Column] = []

        for obj in sorted_objects:
            obj_height = obj.get_height()

            # Ищем корзину с минимальным остаточным местом, куда поместится объект
            best_column_idx = -1
            min_remaining = float('inf')

            for i, column in enumerate(columns):
                if obj_height <= column.remaining < min_remaining:
                    min_remaining = column.remaining
                    best_column_idx = i

            # Если нашли подходящую корзину
            if best_column_idx != -1:
                columns[best_column_idx].add_item(obj)
            else:
                # Создаем новую корзину
                columns.append(
                    Column([obj], obj_height, self.height)
                )

        return columns

    def worst_fit_decreasing(self, objects: list[RaschetList]):
        """
        Алгоритм Worst-Fit Decreasing (WFD).
        Сортирует по убыванию и размещает объект в корзину с наибольшим остаточным местом.
        """
        sorted_objects = sorted(objects, key=lambda x: x.get_height(), reverse=True)
        columns: list[Column] = []

        for obj in sorted_objects:
            obj_height = obj.get_height()

            # Ищем корзину с максимальным остаточным местом, куда поместится объект
            worst_column_idx = -1
            max_remaining = -1

            for i, column in enumerate(columns):
                if column.remaining >= obj_height and column.remaining > max_remaining:
                    max_remaining = column.remaining
                    worst_column_idx = i

            # Если нашли подходящую корзину
            if worst_column_idx != -1:
                columns[worst_column_idx].add_item(obj)
            else:
                # Создаем новую корзину
                columns.append(
                    Column([obj], obj_height, self.height)
                )

        return columns
