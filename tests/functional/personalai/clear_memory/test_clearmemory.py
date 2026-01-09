import pytest
from typing import List, Dict
from tqdm import tqdm
import sys
# TO CHANGE
PROJECT_BASE_DIR = '../'
sys.path.insert(0, PROJECT_BASE_DIR)

from src import PersonalAI
from src.utils.data_structs import Triplet

from .cases import POPULATED_CLEARMEMORY_TEST_CASES

@pytest.mark.parametrize("triplet_groups_to_create, expected_pre_memorysize, textids_to_delete, expected_post_memorysize, personalai_inst",
                         POPULATED_CLEARMEMORY_TEST_CASES, indirect=['personalai_inst'])
def test_clearmemory(triplet_groups_to_create: Dict[str, List[Triplet]], expected_pre_memorysize: Dict,
                     textids_to_delete: List[str], expected_post_memorysize: Dict, personalai_inst: PersonalAI):
    personalai_inst.kg_model.clear()
    personalai_inst.textid_store.clear_store()

    # наполняем пространство памяти информацией
    for text_id, triplet_group in triplet_groups_to_create.items():
        personalai_inst.textid_store.save_info(text_id, triplet_group)
        personalai_inst.kg_model.add_knowledge(triplets=triplet_group)
    real_pre_memorysize = personalai_inst.kg_model.count_items(detailed=True)
    assert expected_pre_memorysize['graph_info'] == real_pre_memorysize['graph_info']
    assert expected_pre_memorysize['embeddings_info'] == real_pre_memorysize['embeddings_info']

    # удаляем куски информации из памяти по text_id
    for text_id in textids_to_delete:
        personalai_inst.clear_memory(text_id)
    real_post_memorysize = personalai_inst.kg_model.count_items(detailed=True)
    assert expected_post_memorysize['graph_info'] == real_post_memorysize['graph_info']
    assert expected_post_memorysize['embeddings_info'] == real_post_memorysize['embeddings_info']

    # проверяем:
    # (1) триплетов, удалённых по соответствующим text_id, нет в памяти;
    # (2) триплеты по нетронутым text_id в памяти присутствуют.
    existing_textids = list(set(triplet_groups_to_create.keys()).difference(set(textids_to_delete)))
    for cur_textid in existing_textids:
        cur_triplet_group = triplet_groups_to_create[cur_textid]
        for triplet in cur_triplet_group:
            # graph struct
            personalai_inst.kg_model.graph_struct.db_conn.item_exist(item_id=triplet.id, id_type='triplet')
            personalai_inst.kg_model.graph_struct.db_conn.item_exist(item_id=triplet.start_node.get_info(), id_type='node')
            personalai_inst.kg_model.graph_struct.db_conn.item_exist(item_id=triplet.end_node.get_info(), id_type='node')
            personalai_inst.kg_model.graph_struct.db_conn.item_exist(item_id=triplet.relation.get_info(), id_type='relation')
            # embeddings struct
            personalai_inst.kg_model.graph_embeddings.triplets_vcomposer.item_exist(triplet.relation.id)
            personalai_inst.kg_model.graph_embeddings.nodes_vcomposers[triplet.start_node.type].item_exist(triplet.start_node.id)
            personalai_inst.kg_model.graph_embeddings.nodes_vcomposers[triplet.end_node.type].item_exist(triplet.end_node.id)
