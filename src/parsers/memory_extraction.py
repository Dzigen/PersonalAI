from typing import List, Tuple
import ast

def mem_custom_triplet_parse_func(raw_response: str) -> List[Tuple[str, str, str]]:
    if ":" in raw_response:
        raw_response = raw_response.split(":")[-1]
    raw_response = raw_response.lower()
    raw_response = raw_response.split(";")
    raw_triplets = []
    for triplet in raw_response:
        if len(triplet.split(",")) != 3:
            continue
        subj, rel, obj = triplet.split(",")
        subj, rel, obj = subj.split(":")[-1].split(".")[-1].strip(''' \n'".,/'''), rel.strip(''' \n'".,/'''), obj.strip(''' \n'".,/''')
        if len(subj) == 0 or len(rel) == 0 or len(obj) == 0:
            continue
        else:
            raw_triplets.append((subj, rel, obj))
    return raw_triplets

#
def mem_custome_thesis_parse_func(raw_response: str) -> List[Tuple[str, str]]:
    if ":" in raw_response:
        raw_response = raw_response.split(":")[-1]
    raw_response = raw_response.split(".")
    raw_triplets = []
    for raw_thesis in raw_response:
        if ";" not in raw_thesis:
            continue
        try:
            raw_thesis, raw_entities = raw_thesis.split(";")
            thesis = raw_thesis.strip('.-* ')
            entities = ast.literal_eval(raw_entities.strip(''' \n'".,/'''))
        except:
            continue
        raw_triplets.append((thesis, entities))
    return raw_triplets
