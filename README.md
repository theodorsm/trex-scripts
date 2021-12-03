# Setup guide

For various applications like tactile internet, gaming, RTC and critical infrastructure, low and consistent latency and jitter is required in the network. To be able to ensure equipment can deliver the performance required, benchmarks has to be done. Usually expensive hardware traffic generators are used to take these measurements. On the software side, we have programs like iperf that is commonly used to get some idea of the network performance. The problem with this way of benchmarking is that is way too expensive to afford good and reliable hardware equipment, and the software solution is not accurate enough for the precise task at hand. In this guide we present a software setup that bridges the gap between a cheap (and open source) software benchmarking setup on general hardware and a dedicated hardware packet generator.

This guide is for setting up the following topology with two separate computers:
```
FIGURE 1.

PGEN (packet generator)         DUT (Device Under Test)
 .-----------.                      .-----------.
 | .-------. |                      | .-------. |
 | | portA | | -------------------> | | port0 | |
 | | portB | | <------------------- | | port1 | |
 | '-------' |                      | '-------' |
 |           |                      |    nic    |
 '-----------'                      '-----------'
```

The benchmark-setup in this guide is beneficial for network engineers or researchers that want to compare latency and jitter for different device configurations with good accuracy and reliability. DPDK and Cisco TRex (runs on DPDK) are the technologies that makes this setup more reliable by bypassing the Linux kernel when taking measurements.

## OS

Any Linux distribution could be used, but in this guide is written with Arch users in mind.
Ideally you should have a completely clean system, but it is not required.

For installing Arch follow the [wiki guide](https://wiki.archlinux.org/index.php/installation_guide).

*linux-5.11.6.arch1-1 is used in this guide*

## Packet generator:

### Tools and packages

Install:

```bash
sudo pacman -S  python-pip base-devel git

```

## PGEN:

### TRex

Follow this [download guide](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_obtaining_the_trex_package) from TRex.

*This guide is based on TRex v2.88 (with version DPDK v21.02)*

### Hot-fix

With Python 3.9.1 a problem with scapy occurred, the following hot-fix worked (ideally the correct library should be installed, and not just symlinking):

```bash
sudo ln -s -f /usr/lib/libc.a /usr/lib/liblibc.a
```

### Setup NIC with DPDK supported drivers

Identify the ports:

```bash
cd /opt/trex/v2.XX/
sudo ./dpdk_setup_ports.py -s

```

```bash
sudo modprobe uio
sudo insmod ko/src/igb_uio.ko
sudo ./dpdk_nic_bind.py -b igb_uio 01:00.0 01:00.1 # replace these two port-IDs to yours
```

or

```bash
sudo modprobe uio_pci_generic
sudo ./dpdk_nic_bind.py -b uio_pci_generic 01:00.0 01:00.1 # replace these two port-IDs to yours
```

### Running

After completing the steps above to setup the packet generator and one of the DUTs below (either stock or DPDK) you can clone this repo and follow the guide in [README_SCRIPTS.md](https://github.com/theodorsm/trex-scripts/blob/main/README_SCRIPTS.md).

Clone this repo on the packet generator:

```bash
git clone https://github.com/theodorsm/trex-scripts.git
cd trex-scripts
```

## DUT

To be able to use the benchmarking tool, you will have a system that is configured with a bridge to forward packets between port0 and port1 (see figure 1).

In this guide two ways of configuring the DUT is presented; stock and with DPDK.

**Follow ONE of configurations below (1. or 2.)**

### Tools and packages

Install:

```bash
sudo pacman -S netplan
```

### 1. stock DUT

Setup bridging with netplan:

```yaml
#/etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp1s0f0:
      dhcp4: no
    enp1s0f1:
      dhcp4: no
    eno1:
      dhcp4: yes
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]

  bridges:
    br0:
      interfaces: [enp1s0f0, enp1s0f1] # Replace with your interfaces
      addresses: [10.0.0.1/24]
```


Enable forwarding in sysctl:

```bash
echo net.ipv4.ip_forward=1 > /etc/sysctl.conf
sysctl -p /etc/sysctl.conf
```

We have to manually create the arp table:

*Modify this script, and run it after each reboot of the system*
```bash
#!/bin/bash

sudo netplan apply
sleep 5
# The IP has to be consistent with the TRex API script
sudo arp -s 10.0.0.2 <PORTA_MAC> -i <YOUR_INTERFACE0>
sudo arp -s 10.0.0.3 <PORTB_MAC> -i <YOUR_INTERFACE1>
sudo arp -s 10.0.0.2 <PORTA_MAC> -i br0
sudo arp -s 10.0.0.3 <PORTB_MAC> -i br0
sudo iptables -A FORWARD -i br0 -o br0 -j ACCEPT
```

### 2. DPDK DUT

Install DPDK by following the [official documentation](https://doc.dpdk.org/guides/linux_gsg/sys_reqs.html).
*v21.08 was used to create this guide*

Not setting up the hugepages correctly will result in bad performance, so set the hugepage to an appropriate size like this:

```bash
cd <DPDK-LOCATION>/dpdk-XX.XX/
sudo ./usertools/dpdk-hugepages.py -p 1G --setup 2G
```

Next, supported DPDK drivers must be bound to the NICs:
```bash
sudo ./usertools/dpdk-devbind.py -b uio_pci_generic 0000:01:00.0 # Replace with your ID
sudo ./usertools/dpdk-devbind.py -b uio_pci_generic 0000:01:00.1 # Replace with your ID
```

Run DPDK forwarding with 2 cores isolated:
```bash
sudo dpdk-testpmd -l 0-3 -n 4 -- -i --nb-cores=2

testpmd> start
```
