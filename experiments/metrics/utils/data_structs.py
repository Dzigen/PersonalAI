from dataclasses import dataclass, fields, asdict
from typing import Dict, Union
import hashlib
from time import time
import os
import yaml
from enum import Enum
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

    @classmethod
    def load(cls, file_path: str):
        """Метод предназначен для загрузки конфигурации компоненты из yaml-файла и создания соответствующего структурированного объекта

        :param file_path: Путь до файла с параметрами конфигурационного объекта
        :type file_path: str
        :return: Экземпляр конфигурационного объекта.
        :rtype: BaseConfigOperations
        """
        with open(file_path, "r") as fd:
            dict_config: Dict = yaml.safe_load(fd)
        return cls.from_dict(dict_config)

    def custom_formatter(self, data):
        formatted_dict = dict()
        for key, val in data:
            # print(key, val, type(val))

            if key in ["task_to_selector_mapping", "AVAILABLE_RCONFIGS"]:
                continue

            elif isinstance(val, Enum):
                formatted_dict[key] = val.value
                
            else:
                formatted_dict[key] = val

        return formatted_dict

    def save(self, file_path: str, force_rewrite: bool = True) -> None:
        """Метод предназначен для сохранения конфигурации объекта в yaml-файл

        :param file_path: Путь и название файла для сохранения конфигурации.
        :type file_path: str
        :param force_rewrite: Если True, то в случае существования файла по заданному пути он будет перезаписан, иначе False. Значение по умолчанию True.
        :type force_rewrite: bool, optional
        :raises FileExistsError: Файл с таким именем уже существует/создан по заданному пути
        """
        dict_config: Dict = asdict(self, dict_factory=self.custom_formatter)
        if not force_rewrite and os.path.isfile(file_path):
            raise FileExistsError(f"file_path: {file_path}")

        with open(file_path, "w") as fd:
            yaml.dump(dict_config, fd, default_flow_style=False, sort_keys=False, allow_unicode=True)


@dataclass(kw_only=True)
class LoggingConfig:
    """
    :param log_base_path: ... . Значение по умолчанию '.'.
    :type log_base_path: Union[None, str], optional   
    :param log_relative_path: Относительный путь до каталога для хранения журнала мониторинга/поведения инициализируемой компоненты. Значение по умолчанию 'log'.
    :type log_relative_path: str, optional
    :param verbose: Если True, то информация о поведении класса будет сохраняться в stdout и файл-журналирования (log), иначе только в файл. Значение по умолчанию False.
    :type verbose: bool, optional
    :param log_level: Уровень (равный и выше) логирумыех сообщений в файл журналирования. Значение по умолчанию LogLevel.DISABLED (логирование выключено).
    :type log_level: LogLevel, optional
    """
    log_base_path: Union[None, str] = "."
    log_relative_path: str = "log"
    verbose: bool = False
    log_level: LogLevel = LogLevel.DEBUG

    def synchronize_logging(self, log_base_path: Union[None, str] = None, log_level: Union[None, LogLevel] = None, verbose: Union[None, bool] = None):
        """Метод предназначен для синхронизации настроек логированиями между вложенными конфигурациями.
        
        :param log_base_path: ... . Если None, используется текущее значение log_base_path. Значение по умолчанию None.
        :type log_base_path: Union[None, str], optional   
        :param log_level: Уровень логирования, который необходимо установить принудительно. Если None, используется текущее значение self.log_level. Значение по умолчанию None.
        :type log_level: Union[None, LogLevel], optional
        :param verbose: Флаг сохранения лога в stdout, который необходимо установить принудительно. Если None, используется текущее значение self.verbose. Значение по умолчанию None.
        :type verbose: Union[None, bool], optional
        """

        if log_base_path is not None:
            self.log_base_path = log_base_path
        if log_level is not None:
            self.log_level = log_level
        if verbose is not None:
            self.verbose = verbose

        fields_iterator = fields(self)
        for field_object in fields_iterator:
            field_value = getattr(self, field_object.name)

            if isinstance(field_value, LoggingConfig):
                field_value.synchronize_logging(self.log_base_path, self.log_level, self.verbose)
