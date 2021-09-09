#!./venv/bin/python

import json
import math
import os
import sys
from collections import Counter
from scipy.integrate import cumtrapz

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


def main():
    filename = str(sys.argv[1])
    path = sys.argv[2]
    sample = parse_file(path)
    mean = sample["mean"]
    tot_max = sample["total_max"]
    tot_min = sample["total_min"]
    jitter = sample["jitter"]
    histogram = sample["histogram"]

    print(histogram)
    lists = sorted(histogram.items(), key=lambda point: int(point[0]))
    x, y = zip(*lists)
    total = sum(y)
    print("x:", x)
    print("y:", y)
    print(total)
    print("jitter", jitter)
    iterator = map(lambda value: (value / total) * 100, y)
    y = list(iterator)

    fig, ax1 = plt.subplots(ncols=1)
    ax2 = ax1.twinx()

    textstr = "\n".join(
        (
            r"$\mathrm{mean}=%.2f$" % (mean),
            r"$\mathrm{max}=%.2f$" % (tot_max),
            r"$\mathrm{min}=%.2f$" % (tot_min),
            r"$\mathrm{jitter}=%.2f$" % (jitter),
        )
    )

    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

    plt.title("PDF and CDF for one run")
    ax1.text(
        0.05,
        0.95,
        textstr,
        transform=ax1.transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=props,
    )

    ax1.bar(x, y, color="b", label="PDF")
    ax1.set_xlabel("Latency in us")
    ax1.set_ylabel("% of packets")
    ax1.legend(bbox_to_anchor=(0.95, 0.8))
    ax1.tick_params(labelrotation=90)

    cdf = cumtrapz(x=np.array(list(map(lambda val: int(val), x))), y=np.array(y))
    cdf = cdf / max(cdf)

    ax2.step(x[1:], cdf, color="r", label="CDF")
    ax2.set_ylabel("Cumulative prob.")
    ax2.legend(bbox_to_anchor=(0.95, 0.7))

    plt.savefig("./plots/" + filename + ".png", bbox_inches="tight")


if __name__ == "__main__":
    main()
