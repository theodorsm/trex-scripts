# trex-scripts
Scripts for TRex Python API.

The `stl_stats.py` script is used to take latency and jitter measurements.

## Traffic

The following 6 traffic-streams is included:

- UDP_LOW: UDP size = 500, @ 1Kpps, 4Mbps
- UDP_HIGH: UDP size = 500, @ 100Kpps, 400Mbps
- TCP_HIGH: TCP size = 500, @ 100Kpps, 400Mbps
- Running MULTIPLE_UDP and MULTIPLE_TCP simultaneously, total of 800Mbps:
    - MULTIPLE_UDP: UDP size = 500, @ 100Kpps
    - MULTIPLE_TCP: TCP size = 500, @ 100Kpps
- BURST_UDP: UDP size = 500 @ 100Kpps with 1 second intervals.
- UDP_SMALL: UDP size = 100 @ 500Kpps, 400Mbps


## Running

### Getting started

Firstly you need to update the `.env` file to correspond to your system.

Then you can install the requirements and activate the virtual environment:
```bash
# Initial setup (once)
python -m venv venv
pip install -r requirements.txt

# Activate (everytime)
source venv/bin/activate
```

### Parameters and run

In `stl_stats.py` you can adjust the following parameters to your needs:

- PPS_LOW (default=1000): Packets per second for UDP_LOW
- PPS_HIGH (default=100000): Packets per second for UDP_HIGH, TCP_HIGH, MULTIPLE and BURST_UDP
- DURATION (default=120): How long each latency measurement should last.
- RUNS (default=4): How many runs of each measurements.

To run the script:

```bash
# in one terminal, leave running:
sudo ./t-rex-64 -i --hdrh
# seperate terminal (trex-scripts)
python stl_stats.py
```

To verify and troubleshoot the port setup:

```bash
# with server running
./trex-console

trex> portattr -a
```
