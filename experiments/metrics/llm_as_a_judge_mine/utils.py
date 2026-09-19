from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
import os
import sys
import json
import logging
import torch
import datetime

LOGGER = logging.getLogger(__name__)

def _clean(xs):
    return [float(x) for x in xs if x is not None]

def plot_accuracy_histogram(acc_dict: Dict[str, List[int]], color_map: Dict[str, str], savefile_path: str) -> None:
    plt.figure(figsize=(13, 6))

    model_keys = list(acc_dict.keys())
    n_models = len(model_keys)

    # Prepare global bins for the range [0, 100]
    all_values = []
    for key in model_keys:
        all_values.extend(_clean(acc_dict[key]))
    # Use fixed bins from 0 to 100
    bins = np.linspace(0, 100, 12)
    bin_width = bins[1] - bins[0]

    for model_idx, key in enumerate(model_keys):
        values = _clean(acc_dict[key])
        color = color_map.get(key, "gray")  # Use gray as fallback if key not found
        # Shift bars for not overlapped bins
        shift = (model_idx - (n_models - 1) / 2) * (bin_width / n_models)
        hist_vals, _ = np.histogram(values, bins=bins, density=False)
        plt.bar(
            bins[:-1] + shift,
            hist_vals,
            width=bin_width / n_models,
            align="edge",
            alpha=0.3,
            edgecolor="black",
            color=color,
            # label=f"{key} histogram"
        )
        # KDE
        if len(values) > 1:
            kde = gaussian_kde(values)
            x_grid = np.linspace(0, 100, 1000)
            # Scale KDE from density to counts by multiplying by number of values and bin width
            kde_values = kde(x_grid) * len(values) * bin_width
            plt.plot(x_grid, kde_values, label=f"{key}", color=color, linewidth=2)
            # Plot the mean as a vertical line
            mean_val = np.mean(values)
            plt.axvline(
                mean_val,
                color=color,
                linestyle="dashed",
                linewidth=2,
                alpha=0.9,
                # label=f"{key} mean"
            )
        elif len(values) == 1:
            plt.axvline(values[0], color=color, label=f"{key} (single value)")

    plt.xlabel("Facts captured, %", fontsize=16)
    plt.ylabel("Frequency (Articles)", fontsize=16)
    # plt.title('Histogram (Not Overlapped) and KDE of Accuracy Values for All Models')
    plt.xlim(0, 100)  # Ensures the frame of the plot starts at 0 and ends at 1
    plt.xticks(np.arange(0, 101, 10), fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend(fontsize=16)
    # plt.show()
    plt.savefig(savefile_path, format="pdf")

def init_logger(args, stdout_only=False):
    if torch.distributed.is_initialized():
        torch.distributed.barrier()
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [stdout_handler]
    if not stdout_only:
        file_handler = logging.FileHandler(
            filename=os.path.join(args.output_dir, "run.log"))
        handlers.append(file_handler)
    logging.basicConfig(
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
    )
    return LOGGER


class Logger:
    def __init__(self, path):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def __call__(self, text, filename="log.txt", verbose=True, debug=True):
        if debug:
            text = str(text)
            if verbose:
                print(text)
            with open(self.path + "/" + filename, "a") as file:
                file.write(f"[{str(datetime.datetime.now())}] {text}\n")

    def to_json(self, obj, filename="history.json"):
        try:
            with open(self.path + "/" + filename, "w") as file:
                json.dump(obj, file)
        except BaseException:
            raise "Object isn't json serializible"