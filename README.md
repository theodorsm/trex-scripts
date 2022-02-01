# Setup guide

For various applications like tactile internet, gaming, RTC and critical infrastructure, low and consistent latency and jitter is required in the network. To be able to ensure equipment can deliver the performance required, benchmarks has to be done. Usually expensive hardware traffic generators are used to take these measurements. On the software side, there exist programs like iperf that is commonly used to get some idea of the network performance. The problem with this way of benchmarking is that is way too expensive to afford good and reliable hardware equipment, and the software solution is not accurate enough for the precise task at hand. In this guide a software setup (using hardware acceleration) is presented that tries to bridge the gap between a cheap (and open source) software benchmarking setup on general hardware and a dedicated hardware packet generator (PGEN).

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

The benchmark-setup in this guide is beneficial for network engineers or researchers that want to compare latency and jitter for different device configurations with good accuracy and reliability. The use of this setup was originally to look into the following hypothesis: *how a Linux system is setup greatly affects performance of packets transferred through the OS, especially with a lot of other processes competing for system resources (e.g. CPU, memory, network card).*

## 0. Supported hardware

Check that your hardware is supported on the [official support page](https://core.dpdk.org/supported/cpus/).

**NOTE:** A CPU of at least 4 threads is required, and for best performance ensure each memory channel has at least one memory DIMM inserted (more performance configurations can be found [here](https://doc.dpdk.org/guides/linux_gsg/nic_perf_intel_platform.html)).

*This setup can be done on virtual machines but some extra configuration may have to be done, check the documentation for your virtual host and the other links provided in this guide. ([VM drivers](https://doc.dpdk.org/guides/nics/e1000em.html))*.

## 1. OS

Any Linux distribution could be used, but Arch was used when creating this guide (RHEL/Fedora is also widely supported).
Ideally you should have a completely clean system, but it is not required.

For installing Arch follow the [wiki guide](https://wiki.archlinux.org/index.php/installation_guide).

*linux-5.11.6.arch1-1 is used in this guide*

### Useful tools and packages

Install:

```bash
sudo pacman -S python-pip base-devel git

```

## 2. PGEN:

### 2.1 Cisco TRex

For the PGEN side, [Cisco TRex](https://trex-tgn.cisco.com/) is used to generate traffic and taking measurements of latency and jitter. TRex uses the [Data Plane Development Kit](https://www.dpdk.org/) (DPDK) as hardware acceleration to get the most accurate timings and performance out of the device's Network Interface Controller (NIC).

For more in-depth documentation checkout the [official TRex documentation](https://trex-tgn.cisco.com/trex/doc/trex_manual.html).

*This guide is based on TRex v2.88 (with DPDK v21.02)*

TRex install:

```bash
mkdir -p /opt/trex
cd /opt/trex
# Known issue with certificate: https://github.com/cisco-system-traffic-generator/trex-core/issues/465
wget --no-cache --no-check-certificate https://trex-tgn.cisco.com/trex/release/latest
tar -xzvf latest
```


#### 2.1.1 Hot-fix

With Python 3.9.1 a problem with scapy occurred, the following hot-fix worked (ideally the correct library should be installed, and not just symlinking):

```bash
sudo ln -s -f /usr/lib/libc.a /usr/lib/liblibc.a
```

### 2.2 Setup NIC with DPDK supported drivers

Identify the ports:

```bash
cd /opt/trex/v2.XX/ # replace with your version
sudo ./dpdk_setup_ports.py -s
```

Note the MAC addresses of your NICs before continuing (to be used later when creating the configuration file for TRex).

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

TRex also provides a `trex-cfg` script that loads the correct drivers and tries to bind the NICs to a DPDK supported driver. The script could replace step **2.2**, but is somewhat unreliable.


## 3. DUT

To be able to use the benchmarking tool, you will have a system that is configured with a bridge to forward packets between port0 and port1 (see figure 1).

In this guide two ways of configuring the DUT is presented; stock and with DPDK.

The "stock" DUT is a device running a stable vanilla [Linux kernel](https://www.kernel.org/) and with no form of hardware acceleration. A regular Linux bridge is used to forward traffic "through" the device.

The DPDK DUT is also running a stable vanilla Linux kernel but with hardware acceleration enabled with DPDK. Forwarding is handled by `dpdk-testpmd` included in DPDPK, running as a user space application.


Any configuration that manages to forward traffic from portA to portB on the PGEN will work, so the DUT could also be considered as a **black-box** with a measurable latency and PDV.

**Follow ONE of the configurations below (config 1 or 2)**


### 3.1 config 1: stock DUT

#### 3.2 Bridging with netplan

Install:

```bash
sudo pacman -S netplan
```

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


#### 3.4 Enable forwarding in sysctl

```bash
echo net.ipv4.ip_forward=1 > /etc/sysctl.conf
sysctl -p /etc/sysctl.conf
```

#### 3.5: Arp table
We have to manually create the arp table:

*If using arp (outdated, but works):*

```bash
sudo pacman -S net-tools
```

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
# Not using net-tools: (have not been tested)
# sudo ip neigh 10.0.0.2 lladdr <PORTA_MAC> dev <YOUR_INTERFACE0>
# sudo ip neigh 10.0.0.3 lladdr <PORTB_MAC> dev <YOUR_INTERFACE1>
# sudo ip neigh 10.0.0.2 lladdr <PORTA_MAC> dev br0
# sudo ip neigh 10.0.0.3 lladdr <PORTB_MAC> dev br0
sudo iptables -A FORWARD -i br0 -o br0 -j ACCEPT
```

### 3.1 config 2: DPDK DUT

Install DPDK by following the [official documentation](https://doc.dpdk.org/guides/linux_gsg/sys_reqs.html).
*v21.08 was used to create this guide*

#### 3.2 Hugepages

Not setting up the hugepages correctly will result in bad performance, so set the hugepage to an appropriate size like this:

```bash
cd <DPDK-LOCATION>/dpdk-XX.XX/
sudo ./usertools/dpdk-hugepages.py -p 1G --setup 2G
```

#### 3.3 Isolate CPU cores

Isolate CPU cores to be used by DPDK in the grub configurations:

```
# add this line to config file (/etc/default/grub) and the cpus to isolate
GRUB_CMDLINE_LINUX="isolcpus=0,1,2,3"
```

#### 3.4 Bind NICs

Next, supported DPDK drivers must be bound to the NICs:
```bash
sudo modprobe uio_pci_generic
sudo ./usertools/dpdk-devbind.py -b uio_pci_generic 0000:01:00.0 # Replace with your ID
sudo ./usertools/dpdk-devbind.py -b uio_pci_generic 0000:01:00.1 # Replace with your ID
```

#### 3.5 Start forwarding

Run DPDK forwarding with 2 cores isolated:
```bash
sudo dpdk-testpmd -l 0-3 -n 4 -- -i --nb-cores=2

testpmd> start
```

## 4. Running

After completing the steps above to setup the packet generator and one of the DUTs (either stock or DPDK) you can clone this repo and follow the guide in [README_SCRIPTS.md](https://github.com/theodorsm/trex-scripts/blob/main/README_SCRIPTS.md).

Clone this repo on the packet generator:

```bash
git clone https://github.com/theodorsm/trex-scripts.git
cd trex-scripts
```

## 5. Troubleshooting

To verify the PGEN setup, try to run TRex in loopback mode as described in the [documentaion](https://trex-tgn.cisco.com/trex/doc/trex_manual.html#_configuring_for_loopback):


## External guides and documentation

All external guides was checked last *Dec. 9 2021* and found to be consistent with this guide. If any of the guides are moved, down or outdated, feel free to create an issue.
