from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Union, Set
from copy import deepcopy

from .utils import Logger, Triplet
from .utils.data_structs import BaseComponentConfig, Node, Relation, NODES_TYPES_MAP, RELATIONS_TYPES_MAP
from .db_drivers.kv_driver import KeyValueDriverConfig, KeyValueDriver, KeyValueDBInstance
from .config import DEFAULT_TEXTTOTRIPLETS_STORE_CONFIG, DEFAULT_TRIPLETTOTEXTS_STORE_CONFIG, TEXTIDSTORE_LOG_PATH


@dataclass
class TextIdStoreConfig(BaseComponentConfig):
    """Конфигурация хранилища отображений между исходными текстами и извлечёнными (из данных текстов) триплетами.

    :param texttotriplets_store_config: Конфигурация хранилища пар: идентификатор исходного фрагмента текста, сохранённого в модель памяти; идентификторы триплетов, которые были извлечены из данного текста и добавлены в граф знаний. Значение по умолчанию DEFAULT_TEXTTOTRIPLETS_STORE_CONFIG.
    :type texttotriplets_store_config: Union[KeyValueDriverConfig, Dict], optional
    :param triplettotexts_store_config: Конфигурация хранилища пар: идентификатор триплета, который был добавлен в граф знаний; идентификаторы исходных фрагментов текста, сохранённого в модель памяти, из которых данный триплет был извлечён. Значение по умолчанию DEFAULT_TRIPLETTOTEXT_STORE_CONFIG.
    :type triplettotexts_store_config: Union[KeyValueDriverConfig, Dict], optional
    """
    texttotriplets_store_config: Union[KeyValueDriverConfig, Dict] = field(default_factory=lambda: DEFAULT_TEXTTOTRIPLETS_STORE_CONFIG)
    triplettotexts_store_config: Union[KeyValueDriverConfig, Dict] = field(default_factory=lambda: DEFAULT_TRIPLETTOTEXTS_STORE_CONFIG)

    log: Logger = field(default_factory=lambda: Logger(TEXTIDSTORE_LOG_PATH))

    def to_str(self):
        return f"{self.texttotriplets_store_config.to_str()}|{self.triplettotexts_store_config.to_str()}"

    @staticmethod
    def from_dict(dict_config: Dict):
        dictconfig_copy = deepcopy(dict_config)
        formated_config = TextIdStoreConfig(**dictconfig_copy)
        formated_config.formate_fields()
        return formated_config

    def formate_fields(self):
        if isinstance(self.texttotriplets_store_config, dict):
            self.texttotriplets_store_config = KeyValueDriverConfig.from_dict(self.texttotriplets_store_config)
        else:
            self.texttotriplets_store_config.formate_fields()

        if isinstance(self.triplettotexts_store_config, dict):
            self.triplettotexts_store_config = KeyValueDriverConfig.from_dict(self.triplettotexts_store_config)
        else:
            self.triplettotexts_store_config.formate_fields()


class TextIdStore:
    """Хранилище отображений между множеством исходных текстов (их идентификаторов), сохранённых в модель памяти, и множеством триплетов (их идентификаторов), которые представляют данные тексты в графе знаний.

    :param config: Конфигурация хранилища. Значение по умолчанию TextIdStoreConfig().
    :type config: Union[Dict,TextIdStoreConfig], optional
    """

    def __init__(self, config: Union[Dict, TextIdStoreConfig] = TextIdStoreConfig()):
        if isinstance(config, dict):
            config: TextIdStoreConfig = TextIdStoreConfig.from_dict(config)
        else:
            config.formate_fields()

        self.textid_to_tripletsid_store = KeyValueDriver.connect(config.texttotriplets_store_config)
        self.tripletid_to_textsid_store = KeyValueDriver.connect(config.triplettotexts_store_config)

    def save_info(self, text_id: str, triplets: List[Triplet]) -> None:
        self.save_tripletsinfo_by_textid(text_id, triplets)
        self.save_textinfo_by_triplets(text_id, triplets)

    def save_tripletsinfo_by_textid(self, text_id: str, triplets: List[Triplet]) -> None:
        if not (isinstance(text_id, str) or isinstance(triplets, list)):
            raise TypeError
        for triplet in triplets:
            if not isinstance(triplet, Triplet):
                raise TypeError

        if self.textid_to_tripletsid_store.item_exist(text_id):
            raise ValueError

        # saving ids-mapping to kv-database
        filtered_triplets = {triplet.id: {
            'snode': {'id': triplet.start_node.id, 'type': triplet.start_node.type.value},
            'rel': {'id': triplet.relation.id, 'type': triplet.relation.type.value},
            'enode': {'id': triplet.end_node.id, 'type': triplet.end_node.type.value}
        } for triplet in triplets}
        textid_to_tripletsid_inst = KeyValueDBInstance(id=text_id, value=filtered_triplets)
        self.textid_to_tripletsid_store.create([textid_to_tripletsid_inst])

    def load_tripletsinfo_by_textid(self, text_id: str) -> List[Triplet]:
        if not isinstance(text_id, str):
            raise TypeError
        if not self.textid_to_tripletsid_store.item_exist(text_id):
            raise ValueError

        textid_to_tripletsid_inst: KeyValueDBInstance = self.textid_to_tripletsid_store.read(ids=[text_id])[0]
        formated_triplets = [
            Triplet(
                id=t_id,
                start_node=Node(id=raw_triplet['snode']['id'], type=NODES_TYPES_MAP[raw_triplet['snode']['type']], name=None),
                relation=Relation(id=raw_triplet['rel']['id'], type=RELATIONS_TYPES_MAP[raw_triplet['rel']['type']], name=None),
                end_node=Node(id=raw_triplet['enode']['id'], type=NODES_TYPES_MAP[raw_triplet['enode']['type']], name=None)
            )
            for t_id, raw_triplet in textid_to_tripletsid_inst.value.items()
        ]
        return formated_triplets

    def save_textinfo_by_triplets(self, text_id: str, triplets: List[Triplet]) -> None:
        if not (isinstance(text_id, str) and isinstance(triplets, list)):
            raise TypeError
        for triplet in triplets:
            if not isinstance(triplet, Triplet):
                raise TypeError

        for triplet in triplets:
            if not self.tripletid_to_textsid_store.item_exist(triplet.id):
                tripletid_to_textsid_inst = KeyValueDBInstance(id=triplet.id, value=set([text_id]))
                self.tripletid_to_textsid_store.create([tripletid_to_textsid_inst])
            else:
                tripletid_to_textsid_inst: KeyValueDBInstance = self.tripletid_to_textsid_store.read([triplet.id])[0]
                tripletid_to_textsid_inst.value.add(text_id)
                self.tripletid_to_textsid_store.update([tripletid_to_textsid_inst])

    def load_textsinfo_by_tripletid(self, triplet_id: str) -> Set[str]:
        if not isinstance(triplet_id, str):
            raise TypeError
        if not self.tripletid_to_textsid_store.item_exist(triplet_id):
            raise ValueError

        output: KeyValueDBInstance = self.tripletid_to_textsid_store.read([triplet_id])[0]
        return output.value

    def clear_info(self, text_id: str) -> Tuple[Set[str], Set[str]]:
        if not isinstance(text_id, str):
            raise TypeError

        triplets = self.load_tripletsinfo_by_textid(text_id)
        self.textid_to_tripletsid_store.delete(ids=[text_id])

        deleted_tripletsid, updated_tripletsid = set(), set()
        tripletid_to_textsid_insts: List[KeyValueDBInstance] = self.tripletid_to_textsid_store.read([triplet.id for triplet in triplets])
        for tripletid_to_textsid_inst in tripletid_to_textsid_insts:
            if len(tripletid_to_textsid_inst.value) > 1:
                tripletid_to_textsid_inst.value.remove(text_id)
                self.tripletid_to_textsid_store.update([tripletid_to_textsid_inst])
                updated_tripletsid.add(tripletid_to_textsid_inst.id)
            else:
                self.tripletid_to_textsid_store.delete([tripletid_to_textsid_inst.id])
                deleted_tripletsid.add(tripletid_to_textsid_inst.id)

        return deleted_tripletsid, updated_tripletsid

    def clear_store(self) -> None:
        self.textid_to_tripletsid_store.clear()
        self.tripletid_to_textsid_store.clear()

    def select_triplets_to_delete(self, text_id: str) -> List[Triplet]:
        formated_triplets = self.load_tripletsinfo_by_textid(text_id)
        # оставляем триплеты, на которые ссылается только один text_id (которые принадлежат только одному text_id)
        filtered_triplets = self.filter_triplets_by_numrefs(formated_triplets, num_references=1)
        return filtered_triplets

    def filter_triplets_by_numrefs(self, triplets: List[Triplet], num_references: int = 1) -> List[Triplet]:
        if not isinstance(num_references, int):
            raise TypeError
        for triplet in triplets:
            if not isinstance(triplet, Triplet):
                raise TypeError

        filtered_triplets: List[Triplet] = []
        for triplet in triplets:
            textid_refs = self.load_textsinfo_by_tripletid(triplet.id)
            if len(textid_refs) == num_references:
                filtered_triplets.append(triplet)
        return filtered_triplets

    def check_consistency(self) -> bool:
        # TODO
        raise NotImplementedError

    def __del__(self):
        self.textid_to_tripletsid_store.close_connection()
        self.tripletid_to_textsid_store.close_connection()
