import datetime
import json
import pprint
import time

import stl_path
from trex.stl.api import *
from goose.goose import GOOSE
from goose.goose_pdu import AllData, Data, IECGoosePDU
from pyasn1.codec.ber import encoder
from pyasn1.type import tag

PGID_TO_NAME = {5: "RX_UDP", 6: "RX_TCP", 7: "RX_GOOSE"}

def create_goose_message():
    g = IECGoosePDU().subtype(
        implicitTag=tag.Tag(
            tag.tagClassApplication,
            tag.tagFormatConstructed,
            1
        )
    )
    g.setComponentByName('gocbRef', 'PDC02_11_700G_G1CFG/LLN0$GO$GooseDset_BF')
    g.setComponentByName('timeAllowedtoLive', 2000)
    g.setComponentByName('datSet', 'PDC02_11_700G_G1CFG/LLN0$Dset_BF')
    g.setComponentByName('goID', '11_700G_G1_Dset_BF')
    g.setComponentByName('t', b'\x55\x15\x1b\x9b\x69\x37\x40\x92')
    g.setComponentByName('stNum', 5)
    g.setComponentByName('sqNum', 1757)
    g.setComponentByName('test', False)
    g.setComponentByName('confRev', 3)
    g.setComponentByName('ndsCom', False)
    g.setComponentByName('numDatSetEntries', 6)
    d = AllData().subtype(
        implicitTag=tag.Tag(
            tag.tagClassContext,
            tag.tagFormatConstructed,
            11
        )
    )
    d1 = Data()
    d1.setComponentByName('boolean', False)
    d2 = Data()
    d2.setComponentByName('bit-string', "'0000000000000'B")
    d3 = Data()
    d3.setComponentByName('utc-time', b'\x55\x15\x14\xc0\xc8\xf5\xc0\x92')
    d4 = Data()
    d4.setComponentByName('boolean', False)
    d5 = Data()
    d5.setComponentByName('bit-string', "'0000000000000'B")
    d6 = Data()
    d6.setComponentByName('utc-time', b'\x55\x15\x14\xaa\x3a\x9f\x80\x92')
    d.setComponentByPosition(0, d1)
    d.setComponentByPosition(1, d2)
    d.setComponentByPosition(2, d3)
    d.setComponentByPosition(3, d4)
    d.setComponentByPosition(4, d5)
    d.setComponentByPosition(5, d6)
    g.setComponentByName('allData', d)
    return encoder.encode(g)


def save_to_file(name, data):
    try:
        print("Trying to save to file...")
        date = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M")
        filename = f"results/{name}_{date}.json"
        with open(filename, "w") as out:
            json.dump(data, out)
    except Exception as e:
        print("Save to file failed: " + str(e))
        return False
    print("Save success!")
    return True


def rx_stats(tx_port, rx_port, pps, duration):

    # create client
    c = STLClient()
    passed = True

    try:
        pkt = STLPktBuilder(
            pkt=Ether()
            / IP(src="10.0.0.2", dst="10.0.0.3")
            / UDP(dport=12, sport=1025)
            / "at_least_16_bytes_payload_needed"
        )
        s1 = STLStream(
            name=PGID_TO_NAME[5],
            packet=pkt,
            flow_stats=STLFlowLatencyStats(pg_id=5),
            mode=STLTXCont(pps=pps),
        )

        tcp_pkt = STLPktBuilder(
            pkt=Ether()
            / IP(src="10.0.0.2", dst="10.0.0.3")
            / TCP(dport=80)
            / "at_least_16_bytes_payload_needed"
        )

        s2 = STLStream(
            name=PGID_TO_NAME[6],
            packet=tcp_pkt,
            flow_stats=STLFlowLatencyStats(pg_id=6),
            mode=STLTXCont(pps=pps),
        )

        # Should be DotQ1
        goose_pkt = STLPktBuilder(
            pkt=Ether()
            / IP(src="10.0.0.2", dst="10.0.0.3")
            / GOOSE(appid=int(0x00b1))
            / create_goose_message()
        )

        s3 = STLStream(
            name=PGID_TO_NAME[7],
            packet=goose_pkt,
            flow_stats=STLFlowLatencyStats(pg_id=7),
            mode=STLTXCont(pps=pps),
        )

        # connect to server
        c.connect()

        # prepare our ports
        c.reset(ports=[tx_port, rx_port])

        # add both streams to ports
        c.add_streams([s1, s2, s3], ports=[tx_port])

        print(
            "\nInjecting packets on port {0}, for {1}s. pps = {2}\n".format(
                tx_port, duration, pps
            )
        )

        passed = rx_iteration(c, tx_port, rx_port, duration)

    except STLError as e:
        passed = False
        print(e)

    finally:
        c.disconnect()

    if passed:
        print("\nTest passed :-)\n")
    else:
        print("\nTest failed :-(\n")


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

    s1 = save_to_file(PGID_TO_NAME[pgid] + "/flow", flow_stats)
    s2 = save_to_file(PGID_TO_NAME[pgid] + "/lat", lat_stats)
    if (s1 or s2) is False:
        print("hit")
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


rx_stats(tx_port=0, rx_port=1, pps=100000, duration=10)
