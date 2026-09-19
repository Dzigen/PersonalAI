from dataclasses import dataclass, asdict, field

dict1 = {"1": 1, "2": "hello world", "3": {"3.1": "hello", "3.2": 3.2}}
dict2_copy = {"1": 1, "2": "hello world", "3": {"3.1": "hello", "3.2": 3.2}}
print(dict1 == dict2_copy)

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

child1 = Child()
child2 = Child()
print( child1 == child2)

parent = Parent()
print( child1.field1 == parent)
