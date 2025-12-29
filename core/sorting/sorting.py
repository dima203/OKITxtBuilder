class Packager:
    """
    Решатель задачи упаковки: распределить все объекты по группам,
    чтобы сумма в каждой группе ≤ target, минимизируя количество групп.
    """

    def __init__(self, objects, target):
        self.objects = objects.copy()
        self.target = target
        self.bins = []

    def first_fit_decreasing(self):
        """
        Алгоритм First-Fit Decreasing (FFD).
        Сортирует объекты по убыванию и распределяет их в первый подходящий контейнер.
        """
        # Сортируем объекты по убыванию высоты
        sorted_objects = sorted(self.objects, key=lambda x: x.get_height(), reverse=True)

        # Создаем первую корзину
        self.bins = []

        for obj in sorted_objects:
            obj_height = obj.get_height()

            # Ищем подходящую корзину
            placed = False
            for bin in self.bins:
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
                    'remaining': self.target - obj_height
                }
                self.bins.append(new_bin)

        # # Пытаемся улучшить упаковку
        # improved = True
        # iteration = 0
        #
        # while improved and iteration < 100:  # Ограничим количество итераций
        #     improved = False
        #
        #     # Для каждой пары корзин
        #     for i in range(len(self.bins)):
        #         for j in range(i + 1, len(self.bins)):
        #             if self._try_improve_pair(self.bins[i], self.bins[j]):
        #                 improved = True
        #
        #     iteration += 1
        #
        # # Удаляем пустые корзины (если они появились)
        # self.bins = [bin for bin in self.bins if bin['items']]
        #
        # # Попытка объединить частично заполненные корзины
        # self.bins = self._merge_bins(self.bins)

        return self.bins

    def best_fit_decreasing(self):
        """
        Алгоритм Best-Fit Decreasing (BFD).
        Сортирует по убыванию и размещает объект в корзину с наименьшим остаточным местом.
        """
        sorted_objects = sorted(self.objects, key=lambda x: x.get_height(), reverse=True)
        self.bins = []

        for obj in sorted_objects:
            obj_height = obj.get_height()

            # Ищем корзину с минимальным остаточным местом, куда поместится объект
            best_bin_idx = -1
            min_remaining = float('inf')

            for i, bin in enumerate(self.bins):
                if bin['remaining'] >= obj_height and bin['remaining'] < min_remaining:
                    min_remaining = bin['remaining']
                    best_bin_idx = i

            # Если нашли подходящую корзину
            if best_bin_idx != -1:
                self.bins[best_bin_idx]['items'].append(obj)
                self.bins[best_bin_idx]['sum'] += obj_height
                self.bins[best_bin_idx]['remaining'] -= obj_height
            else:
                # Создаем новую корзину
                new_bin = {
                    'items': [obj],
                    'sum': obj_height,
                    'remaining': self.target - obj_height
                }
                self.bins.append(new_bin)

        return self.bins

    def worst_fit_decreasing(self):
        """
        Алгоритм Worst-Fit Decreasing (WFD).
        Сортирует по убыванию и размещает объект в корзину с наибольшим остаточным местом.
        """
        sorted_objects = sorted(self.objects, key=lambda x: x.get_height(), reverse=True)
        self.bins = []

        for obj in sorted_objects:
            obj_height = obj.get_height()

            # Ищем корзину с максимальным остаточным местом, куда поместится объект
            worst_bin_idx = -1
            max_remaining = -1

            for i, bin in enumerate(self.bins):
                if bin['remaining'] >= obj_height and bin['remaining'] > max_remaining:
                    max_remaining = bin['remaining']
                    worst_bin_idx = i

            # Если нашли подходящую корзину
            if worst_bin_idx != -1:
                self.bins[worst_bin_idx]['items'].append(obj)
                self.bins[worst_bin_idx]['sum'] += obj_height
                self.bins[worst_bin_idx]['remaining'] -= obj_height
            else:
                # Создаем новую корзину
                new_bin = {
                    'items': [obj],
                    'sum': obj_height,
                    'remaining': self.target - obj_height
                }
                self.bins.append(new_bin)

        return self.bins

    def get_stats(self):
        """Возвращает статистику по упаковке"""
        if not self.bins:
            return {}

        total_objects = sum(len(bin['items']) for bin in self.bins)
        total_sum = sum(bin['sum'] for bin in self.bins)
        avg_fill = sum(bin['sum'] for bin in self.bins) / (len(self.bins) * self.target)

        return {
            'bins_count': len(self.bins),
            'total_objects': total_objects,
            'total_sum': total_sum,
            'average_fill_rate': avg_fill,
            'bins': [
                {
                    'index': i,
                    'item_count': len(bin['items']),
                    'sum': bin['sum'],
                    'remaining': bin['remaining'],
                    'fill_rate': bin['sum'] / self.target
                }
                for i, bin in enumerate(self.bins)
            ]
        }

    def _try_improve_pair(self, bin1, bin2):
        """
        Пытается улучшить упаковку между двумя корзинами.
        Возвращает True, если удалось улучшить.
        """
        # Ищем объект из bin1, который можно переместить в bin2
        for obj1 in bin1['items']:
            h1 = obj1.get_height()

            # Если объект помещается в bin2
            if h1 <= bin2['remaining']:
                # Пытаемся найти объект из bin2, который можно переместить в bin1
                for obj2 in bin2['items']:
                    h2 = obj2.get_height()

                    # Если обмен улучшает заполнение
                    if (h1 > h2 and
                            h1 - h2 <= bin1['remaining'] + h2 and
                            h2 <= bin1['remaining'] + h1):
                        # Выполняем обмен
                        bin1['items'].remove(obj1)
                        bin2['items'].append(obj1)
                        bin1['sum'] -= h1
                        bin2['sum'] += h1
                        bin1['remaining'] += h1
                        bin2['remaining'] -= h1

                        bin2['items'].remove(obj2)
                        bin1['items'].append(obj2)
                        bin2['sum'] -= h2
                        bin1['sum'] += h2
                        bin2['remaining'] += h2
                        bin1['remaining'] -= h2

                        return True

        return False

    def _merge_bins(self, bins):
        """Пытается объединить частично заполненные корзины"""
        # Сортируем корзины по заполненности (наиболее пустые сначала)
        bins.sort(key=lambda b: b['sum'])

        i = 0
        while i < len(bins):
            j = i + 1
            while j < len(bins):
                # Если две корзины можно объединить в одну
                if bins[i]['sum'] + bins[j]['sum'] <= self.target:
                    # Объединяем
                    bins[i]['items'].extend(bins[j]['items'])
                    bins[i]['sum'] += bins[j]['sum']
                    bins[i]['remaining'] = self.target - bins[i]['sum']

                    # Удаляем вторую корзину
                    bins.pop(j)
                else:
                    j += 1
            i += 1

        return bins