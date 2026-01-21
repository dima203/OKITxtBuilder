from core.raschet import RaschetList


class Column:
    def __init__(self, items: list[RaschetList], height: int, max_height: int) -> None:
        self.items = items.copy()
        self.height = height
        self.remaining = max_height - height

    def add_item(self, item: RaschetList | list[RaschetList]) -> None:
        if isinstance(item, list):
            for i in item:
                self.__add_item(i)
        else:
            self.__add_item(item)

    def __add_item(self, item: RaschetList) -> None:
        self.items.append(item)
        self.height += item.get_height()
        self.remaining -= item.get_height()
