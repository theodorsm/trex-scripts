#!./venv/bin/python

import json
import math
import os
import sys
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np


# {"mean": int, "x": [], "y": []}
def parse_file(path):
    f = open(path, "r")
    json_data = json.loads(f.read())
    f.close()

    value_mean = json_data["latency"]["average"]
    total_max = json_data["latency"]["total_max"]
    total_min = json_data["latency"]["total_min"]
    jitter = json_data["latency"]["jitter"]
    histogram = json_data["latency"]["histogram"]

    return {
        "mean": value_mean,
        "total_max": total_max,
        "total_min": total_min,
        "jitter": jitter,
        "histogram": histogram,
    }


def calc_SD(values, N, mean):
    SS = sum(list(map(lambda value: (value - mean) ** 2, values)))
    return math.sqrt(SS / (N - 1))


def calc_conf(sigma, N):
    return 1.960 * (sigma / math.sqrt(N))


def main():
    # 1. arg: filename to save to.
    # 2. arg: number of samples

    filename = str(sys.argv[1])
    N = int(sys.argv[2])
    paths = sys.argv[3 : 3 + N]
    data = []
    mean_samples = []
    max_samples = []
    min_samples = []
    jitter_samples = []
    tot_histogram = {}

    for path in paths:
        sample = parse_file(path)
        data.append(sample)
        mean_samples.append(sample["mean"])
        max_samples.append(sample["total_max"])
        min_samples.append(sample["total_min"])
        jitter_samples.append(sample["jitter"])
        h = sample["histogram"]
        tot_histogram = Counter(tot_histogram) + Counter(h)

    print(tot_histogram)
    lists = sorted(tot_histogram.items(), key=lambda point: int(point[0]))
    x, y = zip(*lists)
    total = sum(y)
    print("x:", x)
    print("y:", y)
    print(total)
    print("jitter", jitter_samples)
    iterator = map(lambda value: (value / total) * 100, y)
    y = list(iterator)

    mean = sum(mean_samples) / N
    total_max = sum(max_samples) / N
    total_min = sum(min_samples) / N
    jitter = sum(jitter_samples) / N

    mean_SD = calc_SD(mean_samples, N, mean)
    total_max_SD = calc_SD(max_samples, N, total_max)
    total_min_SD = calc_SD(min_samples, N, total_min)
    jitter_SD = calc_SD(jitter_samples, N, jitter)

    mean_conf = calc_conf(mean_SD, N)
    total_max_conf = calc_conf(total_max_SD, N)
    total_min_conf = calc_conf(total_min_SD, N)
    jitter_conf = calc_conf(jitter_SD, N)

    fig, ax = plt.subplots()
    textstr = "\n".join(
        (
            r"$\mathrm{mean}=%.2f$ +/- %.2f" % (mean, mean_conf),
            r"$\mathrm{max}=%.2f$ +/- %.2f" % (total_max, total_max_conf),
            r"$\mathrm{min}=%.2f$ +/- %.2f" % (total_min, total_min_conf),
            r"$\mathrm{jitter}=%.2f$ +/- %.2f" % (jitter, jitter_conf),
        )
    )

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    # place a text box in upper left in axes coords
    ax.text(
        0.05,
        0.95,
        textstr,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=props,
    )

    # Plot values
    plt.bar(x, y, color="b")

    # Uncomment for grid
    # plt.grid(color="r", linestyle=":", linewidth=1)

    plt.xlabel("Latency in ms")
    plt.ylabel("% of packets")
    # Plot the average line
    plt.savefig("./plots/" + filename + ".png")


if __name__ == "__main__":
    main()
