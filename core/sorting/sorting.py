import os
from multiprocessing import Pool
from tqdm import tqdm

from core.raschet import RaschetList

from .column import Column


class Sorter:
    def __init__(self, items: list[RaschetList], height: int) -> None:
        self.items = items.copy()
        self.height = height

    def run(self) -> list[Column]:
        result = []

        # Запускаем несколько процессов вычисления
        if len(self.items) < 100:
            results = [self._sort(self.items)]
        elif len(self.items) < 500:
            with Pool() as p:
                results = p.map(self._sort, [self.items[i::os.cpu_count()] for i in range(os.cpu_count())])
        else:
            with Pool() as p:
                results = p.map(self._sort, [self.items[i:i+100:] for i in range(0, len(self.items), 100)])

        for columns in results:
            result.extend(columns)

        return result

    def _sort(self, objects: list[RaschetList]) -> list[Column]:
        list_copy = objects.copy()
        result_lists: list[Column] = []

        with tqdm(total=len(list_copy)) as progress:  # Создание полосы прогресса
            while len(list_copy) > 0:
                progress.set_description("Sorting lists")

                result = self.__max_sum_less_or_equal(list_copy, self.height)  # Находим очередной столбик
                if len(result.items) != 0:
                    result_lists.append(result)

                progress.update(len(result.items))

                # Удаление выбранных элементов
                for el in result.items:
                    list_copy.remove(el)

        return result_lists

    @staticmethod
    def __max_sum_less_or_equal(objects: list[RaschetList], target_height: int) -> Column:
        """
        Находит подмножество объектов с максимальной суммарной высотой ≤ target_height.
        Объекты должны иметь метод get_height(), возвращающий числовое значение.
        """
        if not objects:
            return Column([], 0, target_height)

        # Получаем высоты всех объектов
        heights = [obj.get_height() for obj in objects]

        if sum(heights) <= target_height:
            return Column(objects.copy(), sum(heights), target_height)

        # Создаем таблицу динамического программирования
        # dp[s] - максимальная суммарная высота для ограничения s
        dp = [0] * (target_height + 1)
        # subsets[s] - список объектов, дающих максимальную сумму для ограничения s
        subsets = [[] for _ in range(target_height + 1)]

        for i in range(len(objects)):
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
            max_height = max(dp)
            best_index = dp.index(max_height)
            result = subsets[best_index]
        else:
            result = subsets[target_height]

        return Column(result, max_height, target_height)
