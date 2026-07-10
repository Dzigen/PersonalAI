from dataclasses import dataclass, asdict, field


@dataclass
class Parent:
    field1: str = "Hello World!"
    field2: bool = False
    field3: int = 42

@dataclass
class Child:
    field1: Parent = field(default_factory=lambda: Parent())
    field2: Parent = field(default_factory=lambda: Parent())
    field3: int = 42

dataclass_child = Child()
print(dataclass_child)

dict_child = asdict(dataclass_child)
print(dict_child)
