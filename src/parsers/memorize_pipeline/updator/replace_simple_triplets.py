from typing import List, Dict, Tuple, Set
from collections import defaultdict

from ....utils import Triplet, ReturnStatus
from ....utils.data_structs import create_id

def rs_custom_formate(base_triplet: Triplet, incident_triplets: List[Triplet]) -> Dict[str,str]:
    if len(incident_triplets) < 1:
        raise ValueError

    def _custom_triplet_stringify(triplet: Triplet) -> str:
        return f"{triplet.start_node.name}, {triplet.relation.name}, {triplet.end_node.name}"

    new_str_triplet = f'"{_custom_triplet_stringify(base_triplet)}"'
    existing_str_triplets = '; '.join(map(lambda triplet: f'"{_custom_triplet_stringify(triplet)}"', incident_triplets))

    return {'ex_triplets': existing_str_triplets, 'new_triplets': new_str_triplet}

def rs_custom_parse(raw_response: str, **kwargs) -> Dict[str, object]:
    if len(raw_response) < 1:
        raise ValueError

    raw_replacements = raw_response.lower()
    raw_replacements = raw_replacements.split("[[")[-1] if "[[" in raw_replacements else raw_replacements.split("[\n[")[-1]
    pairs = raw_replacements.replace("[", "").strip("]").split("],")
    triplets_to_remove = defaultdict(set)
    for pair in pairs:
        splitted_pair = pair.split("->")
        if len(splitted_pair) != 2:
            continue

        existing_triplet = splitted_pair[0].split(",")
        if len(existing_triplet) != 3:
            continue
        str_existing_triplet = splitted_pair[0].strip(''' \n'".,/''')

        new_triplet = splitted_pair[1].split(",")
        if len(new_triplet) != 3:
            continue
        str_new_triplet = splitted_pair[1].strip(''' \n'".,/''')

        triplets_to_remove[create_id(str_new_triplet)].add(create_id(str_existing_triplet))

    return triplets_to_remove

def rs_custom_postprocess(parsed_response: Dict[str, Set[str]], base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:
    if len(incident_triplets) < 1:
        raise ValueError

    def _custom_triplet_stringify(triplet: Triplet) -> str:
        return f"{triplet.start_node.name}, {triplet.relation.name}, {triplet.end_node.name}"

    custom_ids_to_triplets = {create_id(_custom_triplet_stringify(triplet)): triplet for triplet in incident_triplets}
    base_triplet_custom_id = create_id(_custom_triplet_stringify(base_triplet))
    obsolete_str_ids = parsed_response.get(base_triplet_custom_id, [])

    triplet_ids_to_remove = []
    for custom_id in custom_ids_to_triplets.keys():
        if custom_id in obsolete_str_ids:
            triplet_ids_to_remove.append(custom_ids_to_triplets[custom_id].id)

    return triplet_ids_to_remove
