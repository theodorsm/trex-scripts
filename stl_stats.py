import datetime
import json
import pprint
import time

import stl_path
from trex.stl.api import *
from Plotter import Plotter

PGID_TO_NAME = {
    1: "UDP_LOW",
    2: "UDP_HIGH",
    3: "TCP_HIGH",
    4: "MULTIPLE_TCP",
    5: "MULTIPLE_UDP",
    6: "UDP_BURST",
    7: "UDP_SMALL",
}

# 1Kpps -> 500 * 8 * 1000pps = 4Mbit/s
PPS_LOW = 1000
# 100Kpps -> 500 * 8 * 100Kpps = 400Mbit/s
PPS_HIGH = 100000

DURATION = 120

RUNS = 4

DUT = "dpdk"


def save_to_file(name, data, date):
    try:
        print("Trying to save to file...")
        filename = f"results/{DUT}/{name}_{date}.json"
        with open(filename, "w") as out:
            json.dump(data, out)
    except Exception as e:
        print("Save to file failed: " + str(e))
        return False
    print("Save success!")
    return True


def rx_stats(tx_port, rx_port, duration, streams: list):
    # create client
    c = STLClient()
    passed = True
    try:

        # connect to server
        c.connect()

        # prepare our ports
        c.reset(ports=[tx_port, rx_port])

        # add streams to ports
        c.add_streams(streams, ports=[tx_port])

        print(
            "\ninjecting packets on port {0}, for {1}s. streams = {2}\n".format(
                tx_port, duration, list(map(lambda stream: stream.name, streams))
            )
        )

        passed = rx_iteration(c, tx_port, rx_port, duration)

    except STLError as e:
        passed = False
        print(e)

    finally:
        c.disconnect()

    if passed:
        print("\ntest passed :-)\n")
    else:
        print("\ntest failed :-(\n")


# RX one iteration
def rx_iteration(c, tx_port, rx_port, duration):

    c.clear_stats()

    c.start(ports=[tx_port], duration=duration)
    pgids = c.get_active_pgids()
    print("Currently used pgids: {0}".format(pgids))
    print("Waiting for traffic to end...")

    c.wait_on_traffic(ports=[tx_port])

    stats = c.get_pgid_stats(pgids["latency"])
    for pgid in pgids["latency"]:
        passed = stream_iteration(c, stats, pgid, tx_port, rx_port)
        if not passed:
            return False
    return True


def stream_iteration(c, stats, pgid, tx_port, rx_port):
    flow_stats = stats["flow_stats"].get(pgid)
    global_lat_stats = stats["latency"]
    lat_stats = global_lat_stats.get(pgid)
    if not flow_stats:
        print("no flow stats available")
        return False
    if not lat_stats:
        print("no latency stats available")
        return False

    tx_pkts = flow_stats["tx_pkts"].get(tx_port, 0)
    tx_bytes = flow_stats["tx_bytes"].get(tx_port, 0)
    rx_pkts = flow_stats["rx_pkts"].get(rx_port, 0)
    drops = lat_stats["err_cntrs"]["dropped"]
    ooo = lat_stats["err_cntrs"]["out_of_order"]
    dup = lat_stats["err_cntrs"]["dup"]
    sth = lat_stats["err_cntrs"]["seq_too_high"]
    stl = lat_stats["err_cntrs"]["seq_too_low"]
    old_flow = global_lat_stats["global"]["old_flow"]
    bad_hdr = global_lat_stats["global"]["bad_hdr"]
    lat = lat_stats["latency"]
    jitter = lat["jitter"]
    avg = lat["average"]
    tot_max = lat["total_max"]
    tot_min = lat["total_min"]
    last_max = lat["last_max"]
    hist = lat["histogram"]

    date = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")
    s1 = save_to_file(PGID_TO_NAME[pgid] + "/flow", flow_stats, date)
    s2 = save_to_file(PGID_TO_NAME[pgid] + "/lat", lat_stats, date)
    if (s1 or s2) is False:
        return False

    if c.get_warnings():
        print("\n\n*** test had warnings ****\n\n")
        for w in c.get_warnings():
            print(w)
        return False

    print(
        "Error counters: dropped:{0}, ooo:{1} dup:{2} seq too high:{3} seq too low:{4}".format(
            drops, ooo, dup, sth, stl
        )
    )
    if old_flow:
        print("Packets arriving too late after flow stopped: {0}".format(old_flow))
    if bad_hdr:
        print("Latency packets with corrupted info: {0}".format(bad_hdr))
    print("Latency info for {0}:".format(PGID_TO_NAME[pgid]))
    print("  Maximum latency(usec): {0}".format(tot_max))
    print("  Minimum latency(usec): {0}".format(tot_min))
    print("  Maximum latency in last sampling period (usec): {0}".format(last_max))
    print("  Average latency(usec): {0}".format(avg))
    print("  Jitter(usec): {0}".format(jitter))
    print("  Latency distribution histogram:")
    l = list(hist.keys())  # need to listify in order to be able to sort them.
    l.sort()
    for sample in l:
        range_start = sample
        if range_start == 0:
            range_end = 10
        else:
            range_end = range_start + pow(10, (len(str(range_start)) - 1))
        val = hist[sample]
        print(
            "    Packets with latency between {0} and {1}:{2} ".format(
                range_start, range_end, val
            )
        )
    return True


if __name__ == "__main__":

    pkt = Ether() / IP(src="10.0.0.2", dst="10.0.0.3") / UDP(dport=12, sport=1025)

    udp_pkt = STLPktBuilder(pkt=pkt / Raw(RandString(size=500 - len(pkt))))

    pkt = Ether() / IP(src="10.0.0.2", dst="10.0.0.3") / TCP(dport=80)

    tcp_pkt = STLPktBuilder(pkt=pkt / Raw(RandString(size=500 - len(pkt))))

    UDP_LOW = STLStream(
        name=PGID_TO_NAME[1],
        packet=udp_pkt,
        flow_stats=STLFlowLatencyStats(pg_id=1),
        mode=STLTXCont(pps=PPS_LOW),
    )

    UDP_HIGH = STLStream(
        name=PGID_TO_NAME[2],
        packet=udp_pkt,
        flow_stats=STLFlowLatencyStats(pg_id=2),
        mode=STLTXCont(pps=PPS_HIGH),
    )

    TCP_HIGH = STLStream(
        name=PGID_TO_NAME[3],
        packet=tcp_pkt,
        flow_stats=STLFlowLatencyStats(pg_id=3),
        mode=STLTXCont(pps=PPS_HIGH),
    )

    MULTIPLE_TCP = STLStream(
        name=PGID_TO_NAME[4],
        packet=tcp_pkt,
        flow_stats=STLFlowLatencyStats(pg_id=4),
        mode=STLTXCont(pps=PPS_HIGH),
    )

    MULTIPLE_UDP = STLStream(
        name=PGID_TO_NAME[5],
        packet=udp_pkt,
        flow_stats=STLFlowLatencyStats(pg_id=5),
        mode=STLTXCont(pps=PPS_HIGH),
    )

    BURST_UDP = STLStream(
        name=PGID_TO_NAME[6],
        packet=udp_pkt,
        flow_stats=STLFlowLatencyStats(pg_id=6),
        # Burst of 1 sec interval @ pps_high, number of burst = duration.
        mode=STLTXMultiBurst(
            pps=PPS_HIGH, pkts_per_burst=PPS_HIGH, count=DURATION, ibg=1000000.0
        ),
    )

    udp_pkt = STLPktBuilder(pkt=pkt / Raw(RandString(size=100 - len(pkt))))

    UDP_SMALL = STLStream(
        name=PGID_TO_NAME[7],
        packet=udp_pkt,
        flow_stats=STLFlowLatencyStats(pg_id=7),
        # 500Kpps -> 400Mbit/s
        mode=STLTXCont(pps=PPS_HIGH * 5),
    )

    for i in range(RUNS):
        rx_stats(tx_port=0, rx_port=1, duration=DURATION, streams=[UDP_LOW])
        rx_stats(tx_port=0, rx_port=1, duration=DURATION, streams=[UDP_HIGH])
        rx_stats(tx_port=0, rx_port=1, duration=DURATION, streams=[TCP_HIGH])
        rx_stats(
            tx_port=0,
            rx_port=1,
            duration=DURATION,
            streams=[MULTIPLE_UDP, MULTIPLE_TCP],
        )
        rx_stats(tx_port=0, rx_port=1, duration=DURATION, streams=[BURST_UDP])
        rx_stats(tx_port=0, rx_port=1, duration=DURATION, streams=[UDP_SMALL])
