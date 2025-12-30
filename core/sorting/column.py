from core.raschet import RaschetList


class Column:
    def __init__(self, items: list[RaschetList], height: int) -> None:
        self.items = items.copy()
        self.height = height

    def add_item(self, item: RaschetList) -> None:
        self.items.append(item)
        self.height += item.get_height()
