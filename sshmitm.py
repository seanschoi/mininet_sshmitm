"""
Custom topology that creates 3 hosts under a single switch.
Use for examples such as SSH MITM attack and TCP Hijacking

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.

author: Sean Choi
email: yo2seol@stanford.edu
"""

from mininet.net import Mininet
from mininet.node import Node, Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.moduledeps import pathCheck

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd("sysctl -p /etc/sysctl.conf")

    def terminate( self ):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        self.cmd("sysctl -p /etc/sysctl.conf")
        super( LinuxRouter, self ).terminate()

class AttackTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        left_host = self.addHost( 'h1', ip='192.168.0.3/24',
            mac='00:00:00:00:00:01')
        right_host = self.addHost( 'h2', ip='192.168.0.4/24',
            mac='00:00:00:00:00:02')
        #attacker_host = self.addHost( 'h3', ip='192.168.0.5/24',
        #    mac='00:00:00:00:00:03')
        attacker_host = self.addNode( 'h3', cls=LinuxRouter, ip='192.168.0.5/24',
            mac='00:00:00:00:00:03')
        main_switch = self.addSwitch( 's1' )
        
        # Add links from the hosts to this single switch
        self.addLink( left_host, main_switch )
        self.addLink( right_host, main_switch )
        self.addLink( attacker_host, main_switch )

def start_sshd( host ):
    "Start sshd on host"
    stop_sshd()
    info( '*** Starting sshd in %s\n' % host.name )
    name, intf, ip = host.name, host.defaultIntf(), host.IP()
    banner = '/tmp/%s.banner' % name
    host.cmd( 'echo "Welcome to %s at %s" >  %s' % ( name, ip, banner ) )
    host.cmd( '/usr/sbin/sshd -o Banner=%s -o UseDNS=no' % banner)
    info( '***', host.name, 'is running sshd on', intf, 'at', ip, '\n' )

def stop_sshd():
    "Stop *all* sshd processes with a custom banner"
    info( '*** Shutting down stale sshd/Banner processes ',
          quietRun( "pkill -9 -f Banner" ), '\n' )

def create_attack_log(host):
    host.cmd("chmod 666 /home/mininet/sshmitm/decoded.log>>!#:2")
    host.cmd("chmod 666 /home/mininet/sshmitm/logfile.log>>!#:2")

def delete_attack_log(host):
    host.cmd("rm /home/mininet/sshmitm/decoded.log")
    host.cmd("rm /home/mininet/sshmitm/logfile.log")

def main():
    topo = AttackTopo()
    info( '*** Creating network\n' )
    net = Mininet(topo=topo)
    net.start()
    print net.items()
    h1, h2, attacker, s1 = net.get('h1', 'h2', 'h3', 's1')
    # Start a ssh server on host 2
    start_sshd(h2)
    create_attack_log(attacker)
    CLI(net)
    stop_sshd()
    delete_attack_log(attacker)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()


#topos = { 'attacktopo': ( lambda: AttackTopo() ) }
