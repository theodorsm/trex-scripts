#!./venv/bin/python

import sys
from Plotter import Plotter


def main():
    files = [
        "results/switch/UDP_LOW/lat_2021_10_08-01_21.json",
        "results/switch/UDP_HIGH/lat_2021_10_08-01_23.json",
        "results/switch/TCP_HIGH/lat_2021_10_08-01_25.json",
        "results/switch/MULTIPLE_TCP/lat_2021_10_08-01_27.json",
        "results/switch/MULTIPLE_UDP/lat_2021_10_08-01_27.json",
        "results/switch/UDP_BURST/lat_2021_10_08-01_43.json",
        "results/switch/UDP_SMALL/lat_2021_10_08-01_45.json",
    ]

    files += [
        "results/stock/UDP_LOW/lat_2021_10_08-03_48.json",
        "results/stock/UDP_HIGH/lat_2021_10_08-03_50.json",
        "results/stock/TCP_HIGH/lat_2021_10_08-03_52.json",
        "results/stock/MULTIPLE_TCP/lat_2021_10_08-03_54.json",
        "results/stock/MULTIPLE_UDP/lat_2021_10_08-03_54.json",
        "results/stock/UDP_BURST/lat_2021_10_08-03_56.json",
        "results/stock/UDP_SMALL/lat_2021_10_08-03_58.json",
    ]

    files += [
        "results/dpdk/UDP_LOW/lat_2021_10_15-02_11.json",
        "results/dpdk/UDP_HIGH/lat_2021_10_15-02_13.json",
        "results/dpdk/TCP_HIGH/lat_2021_10_15-02_15.json",
        "results/dpdk/MULTIPLE_TCP/lat_2021_10_15-02_17.json",
        "results/dpdk/MULTIPLE_UDP/lat_2021_10_15-02_17.json",
        "results/dpdk/UDP_BURST/lat_2021_10_15-02_19.json",
        "results/dpdk/UDP_SMALL/lat_2021_10_15-02_21.json",
    ]

    files += [
        "results/rt-kernel/UDP_LOW/lat_2021_10_15-11_29.json",
        "results/rt-kernel/UDP_HIGH/lat_2021_10_15-11_31.json",
        "results/rt-kernel/TCP_HIGH/lat_2021_10_15-11_33.json",
        "results/rt-kernel/MULTIPLE_TCP/lat_2021_10_15-11_35.json",
        "results/rt-kernel/MULTIPLE_UDP/lat_2021_10_15-11_35.json",
        "results/rt-kernel/UDP_BURST/lat_2021_10_15-11_37.json",
        "results/rt-kernel/UDP_SMALL/lat_2021_10_15-11_39.json",
    ]

    files += [
        "results/stock-load/UDP_LOW/lat_2021_10_20-17_39.json",
        "results/stock-load/UDP_HIGH/lat_2021_10_20-17_41.json",
        "results/stock-load/TCP_HIGH/lat_2021_10_20-17_43.json",
        "results/stock-load/MULTIPLE_TCP/lat_2021_10_20-17_45.json",
        "results/stock-load/MULTIPLE_UDP/lat_2021_10_20-17_45.json",
        "results/stock-load/UDP_BURST/lat_2021_10_20-17_47.json",
        "results/stock-load/UDP_SMALL/lat_2021_10_20-17_49.json",
    ]

    files += [
        "results/dpdk-load/UDP_LOW/lat_2021_10_29-11_55.json",
        "results/dpdk-load/UDP_HIGH/lat_2021_10_29-11_57.json",
        "results/dpdk-load/TCP_HIGH/lat_2021_10_29-11_59.json",
        "results/dpdk-load/MULTIPLE_TCP/lat_2021_10_29-12_01.json",
        "results/dpdk-load/MULTIPLE_UDP/lat_2021_10_29-12_01.json",
        "results/dpdk-load/UDP_BURST/lat_2021_10_29-12_03.json",
        "results/dpdk-load/UDP_SMALL/lat_2021_10_29-12_06.json",
    ]

    files += [
        "results/rt-kernel-dpdk/UDP_LOW/lat_2021_10_15-16_26.json",
        "results/rt-kernel-dpdk/UDP_HIGH/lat_2021_10_15-16_28.json",
        "results/rt-kernel-dpdk/TCP_HIGH/lat_2021_10_15-16_30.json",
        "results/rt-kernel-dpdk/MULTIPLE_TCP/lat_2021_10_15-16_32.json",
        "results/rt-kernel-dpdk/MULTIPLE_UDP/lat_2021_10_15-16_32.json",
        "results/rt-kernel-dpdk/UDP_BURST/lat_2021_10_15-16_34.json",
        "results/rt-kernel-dpdk/UDP_SMALL/lat_2021_10_15-16_36.json",
    ]

    CONST_TRAFFIC = [
        "UDP_LOW",
        "UDP_HIGH",
        "TCP_HIGH",
        "MULTIPLE_TCP",
        "MULTIPLE_UDP",
        "UDP_BURST",
        "UDP_SMALL",
    ]
    # CONST_DUT = ["switch", "stock", "dpdk", "stock-load", "dpdk-load"]
    CONST_DUT = ["switch", "stock", "rt-kernel", "dpdk", "rt-kernel-dpdk"]
    CMP_NAME = "OVERLOAD"

    p = Plotter(files, CONST_TRAFFIC, CONST_DUT, CMP=True, CMP_NAME=CMP_NAME)
    p.do_plot()


if __name__ == "__main__":
    main()
