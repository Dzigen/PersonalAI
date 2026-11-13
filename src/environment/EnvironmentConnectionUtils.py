from typing import Dict, Union
from dataclasses import fields
import pandas as pd

from ..db_drivers.utils import AbstractDatabaseConnection

class EnvironmentConnectionUtils:

    def open_connections(self) -> None:
        fields_iterator = dir(self)
        for field_name in fields_iterator:
            if field_name.endswith("_ref"):
                continue
            field_value = getattr(self, field_name)
            if isinstance(field_value, AbstractDatabaseConnection):
                if not field_value.is_open():
                    field_value.open_connection()
            if isinstance(field_value, EnvironmentConnectionUtils):
                field_value.open_connections()

    def close_connections(self) -> None:
        fields_iterator = dir(self)
        for field_name in fields_iterator:
            if field_name.endswith("_ref"):
                continue
            field_value = getattr(self, field_name)
            if isinstance(field_value, AbstractDatabaseConnection):
                if field_value.is_open():
                    field_value.close_connection()
            if isinstance(field_value, EnvironmentConnectionUtils):
                field_value.close_connections()

    def is_connections_open(self, detailed: bool = True) -> Union[Dict, bool]:
        connections_info: Dict = dict()
        fields_iterator = dir(self)
        for field_name in fields_iterator:
            if field_name.endswith("_ref"):
                continue
            field_value = getattr(self, field_name)
            if isinstance(field_value, AbstractDatabaseConnection):
                connections_info[field_name] = field_value.is_open()
            if isinstance(field_value, EnvironmentConnectionUtils):
                connections_info[field_name] = field_value.is_connections_open()

        if not detailed:
            df = pd.json_normalize(connections_info, sep='_')
            connections_info_flat: Dict = df.to_dict(orient='records')[0]
            connections_summary: bool = (sum(connections_info_flat.values()) == len(connections_info_flat))
            connections_info = connections_summary

        return connections_info