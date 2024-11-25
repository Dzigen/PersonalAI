from typing import List, Dict, Tuple

from ....utils import Triplet

def rt_custom_formate(base_triplet: Triplet, incident_triplets: List[Triplet]) -> Dict[str,str]:

    def _custom_thesis_stringify(triplet: Triplet) -> str:
        return triplet.end_node.name

    existing_str_thesise = f'["{_custom_thesis_stringify(base_triplet)}"]'
    new_str_thesises = '[' +', '.join(map(lambda triplet: f'"{_custom_thesis_stringify(triplet)}"', incident_triplets)) + ']'

    return {'ex_thesises': existing_str_thesise, 'new_thesises': new_str_thesises}

def rt_custom_parse(raw_response: str, **kwargs) -> Dict[str, object]:
    raw_replacements = raw_response.lower()
    predicted_outdated = raw_replacements.split("[")[-1].split("]")[0].split(";")
    predicted_outdated = [pair.strip().split("<-")[1].strip(''' \n'".,/''') for pair in predicted_outdated if "<-" in pair]
    triplets_to_remove = []
    for outdated_thesis in predicted_outdated:
        pass
        # TODO

def rt_custom_postprocess(parsed_response: Dict[str, object], base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:
    # TODO
    pass
