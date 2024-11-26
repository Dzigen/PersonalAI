from typing import List, Dict, Tuple, Set
from collections import defaultdict

from ....utils import Triplet
from ....utils.data_structs import create_id

def rt_custom_formate(base_triplet: Triplet, incident_triplets: List[Triplet]) -> Dict[str,str]:

    def _custom_thesis_stringify(triplet: Triplet) -> str:
        return triplet.end_node.name

    new_str_thesise = f'["{_custom_thesis_stringify(base_triplet)}"]'
    existing_str_thesises = '[' +', '.join(map(lambda triplet: f'"{_custom_thesis_stringify(triplet)}"', incident_triplets)) + ']'

    return {'ex_thesises': existing_str_thesises, 'new_thesises': new_str_thesise}

def rt_custom_parse(raw_response: str, **kwargs) -> Dict[str, object]:
    raw_replacements = raw_response.lower()
    predicted_outdated = raw_replacements.split("[")[-1].split("]")[0].split(";")
    thesises_to_remove = defaultdict(set)
    for pair in predicted_outdated:
        splitted_pair = pair.split("<-")
        if len(splitted_pair) != 2:
            continue

        str_existing_thesis = splitted_pair[1].strip(''' \n'".,/''')
        str_new_thesis = splitted_pair[0].strip(''' \n'".,/''')
        thesises_to_remove[create_id(str_new_thesis)].add(create_id(str_existing_thesis))

    return thesises_to_remove

def rt_custom_postprocess(parsed_response: Dict[str, Set[str]], base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:

    def _custom_thesis_stringify(triplet: Triplet) -> str:
        return triplet.end_node.name

    custom_ids_to_triplets = {create_id(_custom_thesis_stringify(triplet)): triplet for triplet in incident_triplets}
    base_triplet_custom_id = _custom_thesis_stringify(base_triplet)
    obsolete_str_ids = parsed_response[base_triplet_custom_id]

    triplet_ids_to_remove = []
    for custom_id in custom_ids_to_triplets.keys():
        if custom_id in obsolete_str_ids:
            triplet_ids_to_remove.append(custom_ids_to_triplets[custom_id].id)

    return triplet_ids_to_remove
