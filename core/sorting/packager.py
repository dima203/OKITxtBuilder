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
        for bins in results:
            result.extend(bins)

        for i in range(len(result)):
            result[i] = Column(result[i]["items"], result[i]["sum"])

        return result

    def first_fit_decreasing(self, objects: list):
        """
        Алгоритм First-Fit Decreasing (FFD).
        Сортирует объекты по убыванию и распределяет их в первый подходящий контейнер.
        """
        # Сортируем объекты по убыванию высоты
        sorted_objects = sorted(objects, key=lambda x: x.get_height(), reverse=True)

        # Создаем первую корзину
        bins = []

        with tqdm(total=len(sorted_objects)) as progress:
            for obj in sorted_objects:
                progress.set_description(f"Упаковка записей")
                obj_height = obj.get_height()

                # Ищем подходящую корзину
                placed = False
                for bin in bins:
                    if bin['remaining'] >= obj_height:
                        bin['items'].append(obj)
                        bin['sum'] += obj_height
                        bin['remaining'] -= obj_height
                        placed = True
                        break

                # Если не нашли подходящую корзину, создаем новую
                if not placed:
                    new_bin = {
                        'items': [obj],
                        'sum': obj_height,
                        'remaining': self.height - obj_height
                    }
                    bins.append(new_bin)
                progress.update()

        return bins

    def best_fit_decreasing(self, objects: list[RaschetList]):
        """
        Алгоритм Best-Fit Decreasing (BFD).
        Сортирует по убыванию и размещает объект в корзину с наименьшим остаточным местом.
        """
        sorted_objects = sorted(objects, key=lambda x: x.get_height(), reverse=True)
        bins = []

        for obj in sorted_objects:
            obj_height = obj.get_height()

            # Ищем корзину с минимальным остаточным местом, куда поместится объект
            best_bin_idx = -1
            min_remaining = float('inf')

            for i, bin in enumerate(bins):
                if obj_height <= bin['remaining'] < min_remaining:
                    min_remaining = bin['remaining']
                    best_bin_idx = i

            # Если нашли подходящую корзину
            if best_bin_idx != -1:
                bins[best_bin_idx]['items'].append(obj)
                bins[best_bin_idx]['sum'] += obj_height
                bins[best_bin_idx]['remaining'] -= obj_height
            else:
                # Создаем новую корзину
                new_bin = {
                    'items': [obj],
                    'sum': obj_height,
                    'remaining': self.height - obj_height
                }
                bins.append(new_bin)

        return bins

    def worst_fit_decreasing(self, objects: list[RaschetList]):
        """
        Алгоритм Worst-Fit Decreasing (WFD).
        Сортирует по убыванию и размещает объект в корзину с наибольшим остаточным местом.
        """
        sorted_objects = sorted(objects, key=lambda x: x.get_height(), reverse=True)
        bins = []

        for obj in sorted_objects:
            obj_height = obj.get_height()

            # Ищем корзину с максимальным остаточным местом, куда поместится объект
            worst_bin_idx = -1
            max_remaining = -1

            for i, bin in enumerate(bins):
                if bin['remaining'] >= obj_height and bin['remaining'] > max_remaining:
                    max_remaining = bin['remaining']
                    worst_bin_idx = i

            # Если нашли подходящую корзину
            if worst_bin_idx != -1:
                bins[worst_bin_idx]['items'].append(obj)
                bins[worst_bin_idx]['sum'] += obj_height
                bins[worst_bin_idx]['remaining'] -= obj_height
            else:
                # Создаем новую корзину
                new_bin = {
                    'items': [obj],
                    'sum': obj_height,
                    'remaining': self.height - obj_height
                }
                bins.append(new_bin)

        return bins
