import redis
from typing import List, Tuple, Dict

from src.db_drivers.kv_driver.utils import AbstractKVDatabaseConnection, KVDBConnectionConfig, KeyValueDBInstance

class RedisKVConnector(AbstractKVDatabaseConnection):
    def __init__(self, config: KVDBConnectionConfig):
        self.config = config

    def open_connection(self):
        self.conn = redis.Redis(
            host=self.config.host, port=self.config.port,
            db=self.config.db_info['db'])

    def is_open(self):
        try:
            self.conn.ping()
            return True
        except (redis.exceptions.ConnectionError, ConnectionRefusedError):
            return False

    def close_connection(self):
        self.conn.close()

    def create(self, items: List[KeyValueDBInstance]):
        filtered_items = []
        for item in items:
            item_exists = self.conn.hexists(self.config.params['hs_name'], item.id)
            if not item_exists:
                filtered_items.append(item)

        if len(filtered_items) > 0:
            self.conn.hset(self.config.params['hs_name'], mapping={item.id: str(item.value) for item in filtered_items})
            self.conn.zadd(self.config.params['ss_name'], {item.id: 0 for item in filtered_items})


    def read(self, ids: List[str]):
        values = self.conn.hmget(self.config.params['hs_name'], ids)
        formated_values = []
        for val in values:
            if val is None:
                formated_values.append(val)
            else:
                formated_values.append(self.config.params['value_dtype'](val))

        return formated_values

    def update(self, items: List[KeyValueDBInstance]):
        filtered_items = [item for item in items if self.conn.hexists(self.config.params['hs_name'], item.id)]

        self.conn.hset(self.config.params['hs_name'], mapping={item.id: str(item.value) for item in filtered_items})
        self.conn.zadd(self.config.params['ss_name'], {item.id: 0 for item in filtered_items})

    def delete(self, ids: List[str]):
        filtered_ids = [id for id in ids if self.conn.hexists(self.config.params['hs_name'], id)]

        if len(filtered_ids) > 0:
            self.conn.hdel(self.config.params['hs_name'], *filtered_ids)
            self.conn.zrem(self.config.params['ss_name'], *filtered_ids)

    def update_item_score(self, mapping: Dict[str, int]) -> None:
        """ Обновляем скоры использования элементов в ордер сете.

        :param mapping:
        :type mapping: Dict[str, int]
        """
        existed_keys = [id for id in list(mapping.keys()) if self.conn.hexists(self.config.params['hs_name'], id)]
        filtered_mapping = {k: mapping[k] for k in existed_keys}

        if len(existed_keys) > 0:
            for k,v in filtered_mapping.items():
                self.conn.zincrby(self.config.params['ss_name'], v, k)

    def delete_rare_items(self, num: int) -> None:
        """Удаляем элементы, к которым было сделано наименьшее количество обращений.

        :param num: Количество элементов, которое нужно удалить.
        :type num: int
        """
        rarest_values = self.conn.zrangebyscore(self.config.params['ss_name'], 0, "+inf", start=0, num=num)
        if len(rarest_values) > 0:
            self.conn.zrem(self.config.params['ss_name'], *rarest_values)
            self.conn.hdel(self.config.params['hs_name'], *rarest_values)

    def count_items(self):
        return self.conn.hlen(self.config.params['hs_name'])

    def item_exist(self, id: str):
        return self.conn.hexists(self.config.params['hs_name'], id)

    def clear(self):
        self.conn.delete(self.config.params['hs_name'])
        self.conn.delete(self.config.params['ss_name'])
