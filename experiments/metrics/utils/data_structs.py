from dataclasses import dataclass, fields
from typing import Dict, Union
import hashlib
from time import time

def create_id(seed: Union[None, str] = None) -> str:
    if seed is None:
        seed = f"{time()}"
    return hashlib.md5(seed.encode()).hexdigest()

@dataclass
class BaseConfigOperations:
    """Базовый класс для конфигурационных объектов. Определяет типовые операции по созданию конфигураций из словаря
    и рекурсивному приведению вложенных полей к корректному формату.
    """

    def to_str(self) -> str:
        """Метод предназначен для получения строкового представления конфигурационного объекта.

        :return: Строковое представление конфигурации.
        :rtype: str
        """
        pass

    def formate_fields(self) -> None:
        """Метод предназначен для рекурсивного приведения вложенных полей конфигурации к корректному формату.

        Обходит все поля dataclass-объекта и вызывает метод formate_fields()
        для тех полей, которые также являются экземплярами BaseConfigOperations.
        """
        fields_iterator = fields(self)
        for field_object in fields_iterator:
            field_value = getattr(self, field_object.name)

            if isinstance(field_value, BaseConfigOperations):
                field_value.formate_fields()

    @staticmethod
    def from_dict(dict_config: Dict):
        """Метод предназначен для создания экземпляра конфигурационного объекта из словаря параметров.

        :param dict_config: Словарь с параметрами конфигурации.
        :type dict_config: Dict
        :return: Инициализированный объект конфигурации.
        :rtype: BaseConfigOperations
        """
        pass
