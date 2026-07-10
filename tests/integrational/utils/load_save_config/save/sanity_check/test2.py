from dataclasses import dataclass, asdict, field


@dataclass
class Parent:
    field1: str = "Hello World!"
    field2: bool = False
    field3: int = 42


class Utils:
    def __init__(self):
        self.field = 2

    def example_method(self):
        self.field += 1

@dataclass
class Child:
    field1: Parent = field(default_factory=lambda: Parent())
    field2: Utils = field(default_factory=lambda: Utils())
    field3: int = 42

dataclass_child = Child()
print(dataclass_child)

dict_child = asdict(dataclass_child)
print(dict_child)
