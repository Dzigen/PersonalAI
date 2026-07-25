import redis
from typing import List, Dict, Union
from collections import defaultdict
import pickle

from .configs import DEFAULT_REDISKV_CONFIG
from ..utils import AbstractKVDatabaseConnection, KVDBConnectionConfig, KeyValueDBInstance
from ...utils import restore_connection, retry


class RedisKVConnector(AbstractKVDatabaseConnection):
    def __init__(self, config: Union[Dict, KVDBConnectionConfig] = DEFAULT_REDISKV_CONFIG):
        if isinstance(config, dict):
            config = KVDBConnectionConfig.from_dict(config)
        else:
            config.formate_fields()
        self.config: KVDBConnectionConfig = config

        self.config.params['ss_name'] = f"{self.config.db_info['table']}_{self.config.params['ss_name']}"
        self.config.params['hs_name'] = f"{self.config.db_info['table']}_{self.config.params['hs_name']}"

    @retry
    def open_connection(self):
        self.conn = redis.Redis(
            host=self.config.host, port=self.config.port,
            db=self.config.db_info['db'])

        self.operators: Dict = {
            'hexists': self.conn.hexists,
            'delete': self.conn.delete,
            'hset': self.conn.hset,
            'zadd': self.conn.zadd,
            'hdel': self.conn.hdel,
            'zrem': self.conn.zrem,
            'hlen': self.conn.hlen,
            'zincrby': self.conn.zincrby,
            'zrangebyscore': self.conn.zrangebyscore,
            'hmget': self.conn.hmget
        }

        if self.config.need_to_clear:
            self.clear()

    def is_open(self):
        try:
            self.conn.ping()
            return True
        except (redis.exceptions.ConnectionError, ConnectionRefusedError):
            return False

    @retry
    def close_connection(self):
        try:
            self.conn.close()
        except (AttributeError, TypeError):
            pass

    @restore_connection
    def execute(self, mode: str, *args, **kwargs) -> Union[object, None]:
        output = self.operators[mode](*args, **kwargs)
        return output

    def create(self, items: List[KeyValueDBInstance]):
        for item in items:
            if item is None or item.id is None or item.value is None:
                raise ValueError(f"item: {item}")

            if not isinstance(item.id, str):
                raise ValueError(
                    f"id: t - {type(item.id)}; v - {item.id} value: t - {type(item.value)}; v - {item.value}")

        unique_ids = set(map(lambda item: item.id, items))
        if len(items) != len(unique_ids):
            raise ValueError(f"* len(unique_ids): {len(unique_ids)}\n* items: {items}")

        filtered_items: List[KeyValueDBInstance] = []
        for item in items:
            item_exists = self.execute('hexists', self.config.params['hs_name'], item.id)
            if not item_exists:
                filtered_items.append(item)

        # находимся в фиксированном размере хранилища
        if self.config.params['max_storage'] > 0:
            n_items_to_delete = (
                self.count_items() + len(filtered_items)) - self.config.params['max_storage']
            if n_items_to_delete > 0:
                self.delete_rare_items(n_items_to_delete)

        if len(filtered_items) > 0:
            formated_items = []
            for item in filtered_items:
                if isinstance(item.value, bytes):
                    dumped_value = pickle.dumps((item.value, 'bytes'))
                else:
                    dumped_value = pickle.dumps((item.value, 'notbytes'))
                formated_items.append((item.id, dumped_value))

            self.execute('hset', self.config.params['hs_name'], mapping={
                item[0]: item[1] for item in formated_items})
            self.execute('zadd', self.config.params['ss_name'], {
                item[0]: 0 for item in formated_items})

    def read(self, ids: List[str]):
        for id in ids:
            if not isinstance(id, str):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")
        if len(ids) < 1:
            return []

        values = self.execute('hmget', self.config.params['hs_name'], ids)
        formated_items = []
        item_scores = defaultdict(lambda: 0)
        for i, val in enumerate(values):
            if val is None:
                formated_items.append(val)
            else:
                item_scores[ids[i]] += 1

                loaded_value = pickle.loads(val)[0]
                formated_items.append(
                    KeyValueDBInstance(id=ids[i], value=loaded_value))

        # Обновляем метрику использования элементов
        self.update_item_scores(item_scores)

        return formated_items

    def update(self, items: List[KeyValueDBInstance]):
        for item in items:
            if item is None or item.id is None or item.value is None:
                raise ValueError(f"item: {item}")

            if not isinstance(item.id, str) or type(item.value) not in [str, float, int, list, dict, set]:
                raise ValueError(f"item: {item}")

        filtered_items = [item for item in items if self.execute('hexists', self.config.params['hs_name'], item.id)]

        if len(filtered_items) > 0:
            formated_items = []
            for item in filtered_items:
                if isinstance(item.value, bytes):
                    dumped_value = pickle.dumps((item.value, 'bytes'))
                else:
                    dumped_value = pickle.dumps((item.value, 'notbytes'))
                formated_items.append((item.id, dumped_value))

            self.execute('hset', self.config.params['hs_name'], mapping={
                item[0]: item[1] for item in formated_items})
            self.execute('zadd', self.config.params['ss_name'], {
                item[0]: 0 for item in formated_items})

    def delete(self, ids: List[str]):
        for id in ids:
            if not isinstance(id, str):
                raise ValueError(f"* bad id: {id}\n* ids: {ids}")

        filtered_ids = [id for id in ids if self.execute('hexists', self.config.params['hs_name'], id)]

        if len(filtered_ids) > 0:
            self.execute('hdel', self.config.params['hs_name'], *filtered_ids)
            self.execute('zrem', self.config.params['ss_name'], *filtered_ids)

    def update_item_scores(self, mapping: Dict[str, int]) -> None:
        existed_keys = [id for id in list(mapping.keys()) if
                        self.execute('hexists', self.config.params['hs_name'], id)]
        filtered_mapping = {k: mapping[k] for k in existed_keys}

        if len(existed_keys) > 0:
            for k, v in filtered_mapping.items():
                self.execute('zincrby', self.config.params['ss_name'], v, k)

    def delete_rare_items(self, num: int) -> None:
        rarest_values = self.execute('zrangebyscore',
                                     self.config.params['ss_name'], 0, "+inf", start=0, num=num)
        if len(rarest_values) > 0:
            self.execute('zrem', self.config.params['ss_name'], *rarest_values)
            self.execute('hdel', self.config.params['hs_name'], *rarest_values)

    def count_items(self):
        return self.execute('hlen', self.config.params['hs_name'])

    def item_exist(self, id: str):
        if not isinstance(id, str):
            raise ValueError(f"id: {id}")
        return self.execute('hexists', self.config.params['hs_name'], id)

    def clear(self):
        self.execute('delete', self.config.params['hs_name'])
        self.execute('delete', self.config.params['ss_name'])

    def __del__(self):
        self.close_connection()
