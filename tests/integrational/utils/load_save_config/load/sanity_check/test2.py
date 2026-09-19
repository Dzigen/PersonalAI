from dataclasses import dataclass


class Parent:

    @staticmethod
    def modified():
        pass

    @classmethod
    def test(cls):
        return cls.modified()


class Child(Parent):
    field1: int = 2
    field2: int = 4

    @staticmethod
    def modified():
        return Child()


print(Child.test())
