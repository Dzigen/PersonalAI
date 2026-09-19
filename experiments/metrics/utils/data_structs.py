from dataclasses import dataclass, fields
from typing import Dict, Union
import hashlib
from time import time
from .logger import LogLevel, Logger

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

@dataclass(kw_only=True)
class LoggingConfig:
    """
    :param log: Отладочный класс для журналирования/мониторинга поведения инициализируемой компоненты.
    :type log: Logger, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    :param log_level: Уровень (равный и выше) логирумыех сообщений в файл журналирования. Значение по умолчанию LogLevel.NOTSET.
    :type log_level: LogLevel, optional
    """
    log: Logger
    verbose: bool = False
    log_level: LogLevel = LogLevel.NOTSET

    def synchronize_logging(self, log_level: Union[None, LogLevel] = None, verbose: Union[None, bool] = None):
        """Метод предназначен для синхронизации настроек логированиями между вложенными конфигурациями.

        :param log_level: Уровень логирования, который необходимо установить принудительно. Если None, используется текущее значение self.log_level. Значение по умолчанию None.
        :type log_level: Union[None, LogLevel], optional
        :param verbose: Флаг сохранения лога в stdout, который необходимо установить принудительно. Если None, используется текущее значение self.verbose. Значение по умолчанию None.
        :type verbose: Union[None, bool], optional
        """
        if log_level is not None:
            self.log_level = log_level
        if verbose is not None:
            self.verbose = verbose

        fields_iterator = fields(self)
        for field_object in fields_iterator:
            field_value = getattr(self, field_object.name)

            if isinstance(field_value, LoggingConfig):
                field_value.synchronize_logging(self.log_level, self.verbose)
