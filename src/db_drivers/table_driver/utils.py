from typing import Dict, Union, Tuple, List
from dataclasses import dataclass, field
from copy import deepcopy

from ..utils import AbstractDatabaseConnection, BaseDatabaseConfig

@dataclass
class TableDBConnectionConfig(BaseDatabaseConfig):
    db_info: Dict = field(default_factory=lambda: {'db': 'DefaultPersonalAITableDB', 'table': 'DefaultPersonalAITable'})
    host: str = None
    port: str = None

    def to_str(self):
        str_hostport = f"{self.host};{self.port}"
        str_needto = f"{self.need_to_clear};{self.create_index}"
        return f"{self.db_info};{str_hostport};{str_needto};{self.params}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = TableDBConnectionConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config


@dataclass
class BaseTableStucture:
    pass


@dataclass
class TableDBInstance:
    values: BaseTableStucture
    id: Union[None, str] = None


class AbstractTableDatabaseConnection(AbstractDatabaseConnection):
    TABLE_STRUCTURE: BaseTableStucture = None

    def create_table(self, query: str, params: Tuple[object]) -> None:
        pass

    def validate_items(self, items: List[TableDBInstance]) -> bool:
        if self.TABLE_STRUCTURE is None:
            raise ValueError
        for item in items:
            if not isinstance(item.values, self.TABLE_STRUCTURE):
                raise TypeError
            if item.id is not None and not isinstance(item.id, str):
                raise TypeError

        not_null_ids = [item.id for item in items if item.id is not None]
        unique_ids_wo_null = set(not_null_ids)
        if len(not_null_ids) != len(unique_ids_wo_null):
            raise ValueError

        return True

    def validate_ids(self, ids: List[str]) -> bool:
        for id in ids:
            if (id is None) or (not isinstance(id, str)):
                raise ValueError

        return True
