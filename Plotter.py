#!./venv/bin/python
import json
import math
import os
import sys
from scipy.integrate import cumtrapz

import matplotlib.pyplot as plt
import numpy as np


class Plotter:
    def __init__(
        self, mean: int, tot_max: int, tot_min: int, jitter: int, histogram: dict
    ):
        self.mean = mean
        self.tot_max = tot_max
        self.tot_min = tot_min
        self.jitter = jitter
        self.histogram = histogram

        self.plt = plt
        fig, ax1 = self.plt.subplots(ncols=1)
        ax2 = ax1.twinx()
        self.ax1 = ax1
        self.ax2 = ax2

        lists = sorted(self.histogram.items(), key=lambda point: int(point[0]))
        x, y = zip(*lists)
        self.x = x
        total = sum(y)
        iterator = map(lambda value: (value / total) * 100, y)
        y = list(iterator)
        self.y_pdf = y

    @classmethod
    def from_file(cls, path: str) -> "Plotter":
        data = cls.parse_file(path)
        return cls(
            mean=data["mean"],
            tot_max=data["tot_max"],
            tot_min=data["tot_min"],
            jitter=data["jitter"],
            histogram=data["histogram"],
        )

    @staticmethod
    def parse_file(path):
        f = open(path, "r")
        json_data = json.loads(f.read())
        f.close()

        value_mean = json_data["latency"]["average"]
        tot_max = json_data["latency"]["total_max"]
        tot_min = json_data["latency"]["total_min"]
        jitter = json_data["latency"]["jitter"]
        histogram = json_data["latency"]["histogram"]

        return {
            "mean": value_mean,
            "tot_max": tot_max,
            "tot_min": tot_min,
            "jitter": jitter,
            "histogram": histogram,
        }

    def make_PDF(self):
        textstr = "\n".join(
            (
                r"$\mathrm{mean}=%.2f$" % (self.mean),
                r"$\mathrm{max}=%.2f$" % (self.tot_max),
                r"$\mathrm{min}=%.2f$" % (self.tot_min),
                r"$\mathrm{jitter}=%.2f$" % (self.jitter),
            )
        )

        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

        self.ax1.text(
            0.05,
            0.95,
            textstr,
            transform=self.ax1.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=props,
        )

        self.ax1.bar(self.x, self.y_pdf, color="b", label="PDF")
        self.ax1.set_xlabel("Latency in us")
        self.ax1.set_ylabel("% of packets")
        self.ax1.legend(bbox_to_anchor=(0.95, 0.8))
        self.ax1.tick_params(labelrotation=90)

    def make_CDF(self):
        cdf = cumtrapz(
            x=np.array(list(map(lambda val: int(val), self.x))), y=np.array(self.y_pdf)
        )
        cdf = cdf / max(cdf)
        self.ax2.step(self.x[1:], cdf, color="r", label="CDF")
        self.ax2.set_ylabel("Cumulative prob.")
        self.ax2.legend(bbox_to_anchor=(0.95, 0.7))

    def save_plot(self, path):
        # self.plt.title("PDF and CDF for one run")
        self.plt.savefig(path + ".png", bbox_inches="tight")
