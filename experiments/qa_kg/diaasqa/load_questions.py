import os
import json

def load_dataset(dir_path: str):
    pack_files = os.listdir(dir_path)
    packs = []

    for pack_f in pack_files:
        with open(f"{dir_path}/{pack_f}", 'r', encoding='utf-8') as fd:
            data = json.loads(fd.read())

        pack_name = '.'.join(pack_f.split('.')[:-1])
        questions = list(map(lambda item: item['question'], data))
        answers = list(map(lambda item: item['answer'], data))

        packs.append((pack_name, questions, answers))

    return packs
