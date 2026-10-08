from prometheus_client.parser import text_string_to_metric_families
import requests
from typing import Dict, Tuple, Union
from collections import defaultdict
from functools import reduce


class OllamaProxyMetrics:

    def __init__(self, host: str = 'localhost', port: int = 9836):
        self.url = f"http://{host}:{port}/metrics"
        self.raw_metrics = requests.get(self.url).text
        self.formatted_metrics = defaultdict(dict)
        for family in text_string_to_metric_families(self.raw_metrics):
            formatted_samples = defaultdict(dict)
            for sample in family.samples:
                formatted_labels = self.formate_labels(sample.labels)
                formatted_samples[sample.name][formatted_labels] = sample.value
            formatted_samples = dict(formatted_samples)

            self.formatted_metrics[family.name][family.type] = formatted_samples

        self.formatted_metrics = dict(self.formatted_metrics)

    def formate_labels(self, labels: Dict = None) -> Tuple:
        formatted_labels = tuple()
        if labels is not None:
            sorted_labels = sorted(list(labels.items()), key=lambda item: item[0], reverse=False)
            formatted_labels = tuple(reduce(lambda acc, v: acc + list(v), sorted_labels, []))
        return formatted_labels

    def get(self, field_name: str, field_type: str, labels: Dict = None) -> Union[float, str]:
        field_family = None
        for family_name in self.formatted_metrics[field_type].keys():
            if field_name.startswith(family_name):
                field_family = family_name
                break
        if field_family is None:
            raise ValueError

        formatted_labels = self.formate_labels(labels)
        value = self.formatted_metrics[field_family][field_type][field_name][formatted_labels]

        return value
