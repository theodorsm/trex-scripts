#!./venv/bin/python

import sys
from Plotter import Plotter


def main():
    filename = str(sys.argv[1])
    path = sys.argv[2]
    plotter = Plotter.from_file(path)
    plotter.make_PDF()
    plotter.make_CDF()
    plotter.save_plot("./plots/" + filename)


if __name__ == "__main__":
    main()
