#!./venv/bin/python
import json
import math
import os
import sys
from scipy.integrate import cumtrapz

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from hdrh.histogram import HdrHistogram


class Plotter:
    def __init__(self, files: dict, CONST_TRAFFIC, CONST_DUT, CMP: bool, **kwargs):
        self.files = files
        self.CONST_TRAFFIC = CONST_TRAFFIC
        self.CONST_DUT = CONST_DUT
        self.CMP = CMP
        if CMP:
            if "CMP_NAME" in kwargs:
                self.CMP_NAME = kwargs["CMP_NAME"]
            else:
                raise TypeError("Must give CMP_NAME value if CMP is set")

        d = self.decode(self.files)
        self.hdr_histograms = d["hdrh"]
        self.jitters = d["jitter"]

    def parse_file(self, path):
        f = open(path, "r")
        json_data = json.loads(f.read())
        f.close()

        value_mean = json_data["latency"]["average"]
        tot_max = json_data["latency"]["total_max"]
        tot_min = json_data["latency"]["total_min"]
        jitter = json_data["latency"]["jitter"]
        histogram = json_data["latency"]["histogram"]
        hdrh = json_data["latency"]["hdrh"]

        return {
            "mean": value_mean,
            "tot_max": tot_max,
            "tot_min": tot_min,
            "jitter": jitter,
            "histogram": histogram,
            "hdrh": hdrh,
        }

    def decode(self, files):
        hs = dict.fromkeys(self.CONST_DUT)
        js = dict.fromkeys(self.CONST_DUT)
        for e in hs:
            hs[e] = {}
        for e in js:
            js[e] = {}
        for file in files:
            DUT = file.split("/")[1]
            traffic_type = file.split("/")[2]
            if (DUT in self.CONST_DUT) and (traffic_type in self.CONST_TRAFFIC):
                parsed = self.parse_file(file)
                hdrh = parsed["hdrh"]
                jitter = parsed["jitter"]
                h = HdrHistogram.decode(hdrh)
                hs[DUT][traffic_type] = h
                js[DUT][traffic_type] = jitter
        return {"hdrh": hs, "jitter": js}

    def do_plot(self):

        if self.CMP:
            for traffic in self.CONST_TRAFFIC:
                outs = ""
                for dut in self.hdr_histograms.keys():
                    out = "out/{}/{}_{}.txt".format(
                        dut.strip("."), dut.strip("."), traffic
                    )
                    outs += out + " "
                    self.hdr_histograms[dut][traffic].output_percentile_distribution(
                        open(out, "wb+"), 1000
                    )
                print(outs)

                os.system(
                    "hdr-plot --output out/CMP_{}.png --title '{}' {}".format(
                        f"{traffic}_{self.CMP_NAME}", traffic, outs
                    )
                )

        hdrh_files = []
        for dut in self.hdr_histograms.keys():
            histograms = self.hdr_histograms[dut]
            print(histograms)
            for traffic_type in histograms.keys():
                out = "out/{}/{}.txt".format(dut, traffic_type)
                print(out)
                hdrh_files.append(out)
                histograms[traffic_type].output_percentile_distribution(
                    open(out, "wb+"), 1000
                )

        self.plot_multiple(hdrh_files)

    def plot_multiple(self, hdrh_files):
        for file in hdrh_files:
            os.system(
                "hdr-plot --output {}.png --title '{}' {}".format(
                    file.strip(".txt"), file.strip(".txt"), file
                )
            )
