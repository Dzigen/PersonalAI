from datasets import load_from_disk
from typing import Tuple, List

def mine_load(dataset_path: str) -> List[Tuple[str, List[str], List[str]]]:
    original_dataset = load_from_disk(f"{dataset_path}/original") # 101
    packs = []
    for i in range(len(original_dataset)):
        pack_name = original_dataset['id'][i]
        queries = original_dataset['generated_queries'][i]
        if len(queries) < 1:
            continue
        else:
            packs.append((pack_name, queries))
    print(f"packs: {len(packs)}")
    return packs

CUSTOM_LOAD_KGEVAL_DS_FUNCS = {
    'mine_train_kgeval': mine_load
}