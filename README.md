# SSH MITM Attack Demo using Mininet

## Introduction
In this demo, we are going to demonstrate how a malicious attacker can eavesdrop on the traffic between a SSH client and a SSH server via a method called ARP Spoofing to become the Man In The Middle host.

## Getting Started

This example requires two critical pieces of software called Mininet and Ettercap. We will describe how you can install these softwares below.

### Mininet Installation

First of all, we will need to install Mininet. Mininet is a software based network emulator. It allows the users to run a collection of end-hosts, switches, routers, and links on a single Linux kernel. You can either install Mininet on your computer or run this example through a VM image which is provided in the Mininet website. More detailed installation instructions and more information about Mininet can be found in http://mininet.org/download/

### Ettercap Installation

Secondly, we will need to install Ettercap. Ettercap is a comprehensive suite to easily perform various network based attacks such as ARP spoofing. It features sniffing of live connections, content filtering on the fly and many other interesting tricks. It supports active and passive dissection of many protocols and includes many features for network and host analysis. We recommend using the Mininet VM image, as it is based on Ubuntu 14.04, making ettercap installations easier as well.

#### Ubuntu 14.04 Installation (Mininet VM Image)
Simply run `sudo apt-get install ettercap-graphical`

#### Others
Refer to https://github.com/Ettercap/ettercap for detailed instructions on building and installing ettercap

## Running the example

### Clone the repository

You would first need to clone this repository and go into the folder by running
```
git clone https://github.com/yo2seol/mininet_sshmitm.git
cd mininet_sshmitm
```
The folder contains 6 files, `etter_filter_ssh, etter_filter_ssh_co, README.md, sshmitm.py, run_mininet.sh, run_ettercap.sh`. `etter_filter_ssh` is a etterfilter file defining the custom operations for packets received in the attacking host. `sshmitm.py` is the main mininet topology and configuration file. Others are scripts to run the respective services.

### Run the mininet CLI 

Start the mininet topology as defined in `sshmitm.py` by running `./run_mininet.sh` script or running `sudo python sshmitm.py`. The topology contains 3 hosts attached to a single switch with the following definitions.
```
host_name ip  mac_address
h1  192.168.0.3 00:00:00:00:01
h2  192.168.0.4 00:00:00:00:02
h3  192.168.0.5 00:00:00:00:03
```
`h1` will act as a ssh client, and `h2` will act as a ssh server. `h3` will be the man in the middle spoofing on the traffic between `h1` and `h2`.

Running this command will complete the following actions.

* Setup the topology as described above
* Start the ssh server on host 2
* Create logfile on host 3 to capture the ssh output

### Open the terminals for each hosts
Open the terminal for each host by running `xterm h1 h2 h3`

If using ssh terminal to access your VM, you may need to add `-Y` parameter for your `ssh` function. Also, Mac OSX users may need to install xQuartz in http://xquartz.macosforge.org/landing/, as X11 is no longer a default software installed in Mac OSX.

### Set up IP forwarding and start ettercap on the Attacker

In host 3's terminal, run the following command to set up ip forwarding.
```
echo 1 > /proc/sys/net/ipv4/ip_forward, cat /proc/sys/net/ipv4/ip_forward
```
This enables linux kernel IP forwarding, so that it can forward packets received from a host to another host.

Run ettercap using the following command
```
./run_ettercap.sh
```
or which basically runs
```
ettercap -G --filter etter_filter_ssh_co
```
This starts ettercap in a graphical interface and loads the compiled version of `etter_filter_ssh` filter file. If interested, you can also manipulate this file to test out various attacks. Some examples are in https://github.com/Ettercap/ettercap/blob/master/share/etter.filter.examples. Make sure to run `etterfilter etter_filter_ssh -o etter_filter_ssh_co` after modfying the file to compile it again.

### Ettercap Directions

This part will initialize the sniffing as well as arp spoofing. More about ARP spoofing can be found in https://en.wikipedia.org/wiki/ARP_spoofing

1. `Options`-> Check to see that only `Promisc Mode` is checked
2. `Sniffing` -> `Unified Sniffing` -> `h3-eth0` as the network interface -> Click `Ok`
3. `Hosts`-> `Scan for Hosts`. This will scan all hosts connected to your network.
4. `Hosts` -> `Host List` to view the hosts. You will see `h1, h2` as defined by their IP addresses.
5. Add `192.168.0.3` to target 1 and `192.168.0.4` to target 2.
6. Check that the targets are assigned correctly by going to  `Targets` -> `Current Targets`
7. Enable ARP Spoofing as follows. `Mitm` -> `ARP Spoofing` -> Check `Sniff Remote Connections` -> Click `Ok`.
  Check the log to see that GROUP assignments are similar to your targets.
8. `Start` -> `Start Sniffing`

This will cause `h3` to send malicious ARP information to `h1` and `h2` and cause the traffic between two hosts to flow through `h3`. It will also do couple more things. It will attempt to make the clients use SSH Version 1, which is a less secure version. Also, it will log all SSH activities in the files `decoded.log` and `logfile.log`.

### Start the SSH host from h1

1. Run `ssh -1 mininet@192.168.0.4` to connect to `h2`. You can use tools are wireshark (https://www.wireshark.org/) in `h3` to see that the ssh requests are going through `h3` instead of going straight to `h2`.
2. If `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` error shows, run `ssh-keygen -f "/root/.ssh/known_hosts" -R 192.168.0.4` to refresh the keys and retry the `ssh` command.
3. In ettercap, check that both '[SSH Filter] SSH downgraded from version 2 to 1' and 'SSH : 192.168.0.4:22 -> USER: [username]  PASS: [password]' are present in the ettercap console. You are now snooping the SSH connection!

In order to view the entire SSH interactive inputs and output, you can open another terminal for `h3` and run `tail -f decoded.log`. You will see that any inputs and output for `h1`'s ssh connection to `h2` will be shown here.
