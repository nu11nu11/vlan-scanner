# -*- coding: utf-8 -*-
'''
Created on Apr 14, 2015

@author: 0_o -- null_null (nu11.nu11 [at] yahoo.com)
         Oh, and it is n-u-one-one.n-u-one-one, no l's...
         Wonder how the guys at packet storm could get this wrong :(

# vim: set tabstop=2 shiftwidth=2 smarttab expandtab
# vim: retab
'''
__updated__ = "2015-05-12"


from Common.puts import c

from scapy.all import *
from threading import Thread
# from VSCAN.Scanner.sniffer import sniffAnswer

import binascii


#===============================================================================
# def worker(num):
#     """thread worker function"""
#     print 'Worker: %s' % num
#     return
# 
# threads = []
# for i in range(5):
#     t = threading.Thread(target=worker, args=(i,))
#     threads.append(t)
#     t.start()
#===============================================================================


class DhcpDiscover(Thread):
  '''
  Emit DHCP discover probes and sniff for DHCP offers
  '''
  
  def __init__(self, iface, mac = None, results = None, resultlock = None):
    self.__iface = iface
    if mac: self.__mac = mac 
    else: self.__mac = get_if_hwaddr(self.__iface)
    self.__resultDict = results
    self.__resultDictLock = resultlock
    self.__dhcpOfferTimeout = 5
    self.__snifferFilter = 'udp and (port 67 or 68)'
    self.__dhcpXid = None
    Thread.__init__(self)
    return
  
  
  def dhcpClient(self, response):
    global c
    # Implements a rudimentary DHCP client to spoof DHCP DISCOVER messages.
    # if response is None, then send a DHCP DISCOVER.
    if response is None:
      packet = self.__buildDhcpDiscover()
      c.puts("[*] Sending a DHCP DISCOVER with xid = " + hex(packet[BOOTP].xid) + " on " + self.__iface)
      # sendp(packet, iface = self.__iface, inter = 1, count = 3, verbose = 0)
      sendp(packet, iface = self.__iface, verbose = 0)
      return
    # a packet has been received. check if it is a DHCP packet.
    if response.haslayer(DHCP):
      # dissect and analyze...
      if response[DHCP].options[0][1] == 2:
        dhcpServerIpAddress = response[BOOTP].siaddr
        dhcpServerMacAddress = response[Ether].src
        dhcpOfferedAddress = response[BOOTP].yiaddr
        dhcpOpts = response[DHCP].options[1:response[DHCP].options.index('end')]
        with self.__resultDictLock:
          self.__resultDict[(self.__iface, 'DHCP')] = {'dhcpServerIpAddress': dhcpServerIpAddress,
                                                       'dhcpServerMacAddress': dhcpServerMacAddress,
                                                       'dhcpOfferedAddress': dhcpOfferedAddress,
                                                       'dhcpOpts': dhcpOpts}
        c.puts("[*] Got DHCP OFFER from: " + dhcpServerMacAddress + ", DHCP server: " + response[BOOTP].siaddr + ", offered IP: " + response[BOOTP].yiaddr + ", xid: " + hex(response[BOOTP].xid))
        msg = "   [+] DHCP options:"
        for dhcpOpts in response[DHCP].options:
          msg += "\n"
          if dhcpOpts == 'end' or dhcpOpts == 'pad': break
          key = dhcpOpts[0]
          val = dhcpOpts[1:]
          msg += "   [+] " + key + ": " + str(val)
        c.puts(msg)
        return 
    return
  
  
  def __buildDhcpDiscover(self):
    # construct a DHCP DISCOVER packet
    # BOOTP protocol
    # siaddr = DHCP server ip
    # yiaddr = ip offered to client
    # xid = transaction id 
    # chaddr = clients mac address in binary format
    # self.__mac = clients mac address as string
    self.__dhcpXid = random.randint(0, 0xFFFFFFFF)
    chaddr = binascii.unhexlify(self.__mac.replace(":", ""))
    pEther = Ether(dst = 'ff:ff:ff:ff:ff:ff', src = self.__mac, type = 0x0800)
    pIP = IP(src = '0.0.0.0', dst = '255.255.255.255')
    pUDP = UDP(dport = 67, sport = 68)
    pBOOTP = BOOTP(op = 1, chaddr = chaddr, xid = self.__dhcpXid)
    pDHCP = DHCP(options = [('message-type', 'discover'), ('end')])
    packet = pEther / pIP / pUDP / pBOOTP / pDHCP
    return packet
  
  
  def sniffAnswer(self):
    '''
    sniffAnswerDhcp('eth0', 'udp and (port 67 or 68)', 'dhcp_client', 5)
    # "[*] Waiting for a DHCP OFFER..." 
    '''
    retval = sniff(filter = self.__snifferFilter, lfilter = self.dhcpClient, iface = self.__iface, timeout = self.__dhcpOfferTimeout)
    return retval
  
  
  def run(self):
    '''
    Initiate the scan
    '''
    # sniff for a DHCP OFFER...
    sniffer = Thread(target = self.sniffAnswer)
    sniffer.start()
    # send a DHCP DISCOVER probe...
    self.dhcpClient(None)
    sniffer.join()
    return
  
  
