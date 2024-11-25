from typing import List, Dict, Tuple

from ....utils import Triplet, ReturnStatus

def rs_custom_formate(base_triplet: Triplet, incident_triplets: List[Triplet]) -> Dict[str,str]:

    def _custom_triplet_stringify(triplet: Triplet) -> str:
        return f"{triplet.start_node.name}, {triplet.relation.name}, {triplet.end_node.name}"

    existing_str_triplet = f'"{_custom_triplet_stringify(base_triplet)}".'
    new_str_triplets = '; '.join(map(lambda triplet: f'"{_custom_triplet_stringify(triplet)}"', incident_triplets)) + '.'

    return {'ex_triplets': existing_str_triplet, 'new_triplets': new_str_triplets}

def rs_custom_parse(raw_response: str, **kwargs) -> Dict[str, object]:
    raw_replacements = raw_response.lower()
    raw_replacements = raw_replacements.split("[[")[-1] if "[[" in raw_replacements else raw_replacements.split("[\n[")[-1]
    pairs = raw_replacements.replace("[", "").strip("]").split("],")
    triplets_to_remove = []
    for pair in pairs:
        splitted_pair = pair.split("->")
        if len(splitted_pair) != 2:
            continue
        first_triplet = splitted_pair[0].split(",")
        if len(first_triplet) != 3:
            continue
        subj, rel, obj = first_triplet[0].strip(''' \n'".,/'''), first_triplet[1].strip(''' \n'".,/'''), first_triplet[2].strip(''' \n'".,/''')

        # TODO

def rs_custom_postprocess(parsed_response: Dict[str, object], base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:
    # TODO
    pass
