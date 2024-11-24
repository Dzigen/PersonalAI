from typing import List, Dict

from ....utils import Triplet

def en_rs_parse(raw_agent_answer: str, **kwargs) -> object:
    # TODO
    pass

def en_rs_postprocess(foramted_agent_answer: object, base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:
    # TODO
    pass

def ru_rs_parse(agent_raw_output: str, **kwargs) -> object:
    # TODO
    pass

def ru_rs_postprocess(foramted_agent_answer: object, base_triplet: Triplet, incident_triplets: List[Triplet]) -> List[str]:
    # TODO
    pass

def rs_formate(base_triplet: Triplet, incident_triplets: List[Triplet]) -> Dict[str,str]:
    # TODO
    pass

@staticmethod
    def parse_replacements_thesis(raw_replacements):
        raw_replacements = raw_replacements.lower()
        predicted_outdated = raw_replacements.split("[")[-1].split("]")[0].split(";")
        predicted_outdated = [pair.strip().split("<-")[1].strip(''' \n'".,/''') for pair in predicted_outdated if "<-" in pair]
        triplets_to_remove = []
        for outdated_thesis in predicted_outdated:
            triplets_to_remove.append(
                [
                    {"name": "remove", "type": "remove", "prop": {}},
                    {"name": "hyper", "prop": {"type": "hyper"}},
                    {"name": outdated_thesis, "type": "hyper", "prop": {}}
                ]
            )
        return triplets_to_remove

    @staticmethod
    def parse_replacements_simple(raw_replacements):
        raw_replacements = raw_replacements.lower()
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
            triplets_to_remove.append(
                [
                    {"name": subj, "type": "remove", "prop": {}},
                    {"name": rel, "prop": {"type": "remove"}},
                    {"name": obj, "type": "remove", "prop": {}}
                ]
            )
        return triplets_to_remove
