#!./venv/bin/python

import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

# Read file from argument
path = str(sys.argv[1])
# JSON file
f = open(path, "r")

# Reading from file
data = json.loads(f.read())

# Closing file
f.close()

lists = sorted(data["latency"]["histogram"].items(), key=lambda point: int(point[0]))
x, y = zip(*lists)
total = sum(y)
print(total)
iterator = map(lambda value: (value / total) * 100, y)
y = list(iterator)

value_mean = data["latency"]["average"]

fig, ax = plt.subplots()
textstr = r"$\mathrm{average}=%.2f$" % (value_mean)
# these are matplotlib.patch.Patch properties
props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
# place a text box in upper left in axes coords
ax.text(
    0.05,
    0.95,
    textstr,
    transform=ax.transAxes,
    fontsize=14,
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
filename = "plots/PLOT_" + os.path.basename(path)[:-5]
plt.savefig(filename + ".png")
