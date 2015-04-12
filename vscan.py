# -*- coding: utf-8 -*-
'''
Created on Apr 8, 2015

@author: 0_o -- null_null (nu11.nu11 [at] yahoo.com)
         Oh, and it is n-u-one-one.n-u-one-one, no l's...
         Wonder how the guys at packet storm could get this wrong :(

# vim: set tabstop=2 shiftwidth=2 smarttab expandtab
# vim: retab

'''
__updated__ = "2015-04-09"


from Common.debug import DEBUG_VSCAN as DBG
from VSCAN.threads import threadList as TL

from scapy.all import get_if_list, get_if_hwaddr
from collections import deque

import argparse
import threading
import sys
import os


version = "0.1"
__author__ = "0_o -- null_null"
__email__ = "nu11.nu11 [at] yahoo.com"
__license__ = "GPLv3.0"
__copyright__ = "Copyright 2015 until today: " + __author__ \
                + ' (' + __email__ + ')'
__url__ = ""


  
class Main(object):
  
  def __init__(self):
    self.__progName = "vscan"
    self.__progVersion = self.__progName + " " + version
    self.__iface = None
    self.__ifaceMac = None
    self.__ifaceOldMac = None
    self.__vlanIds = []
    self.__running = 0
    self.__main()
    
  
  def __parseOptions(self, myargs):
    '''
    Parse the command line options
    '''
    argParser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    argParser.add_argument("-i", "--iface", dest = "iface", default = "eth0", help = "The hardware network interface to scan.", metavar = "NIC")
    argParser.add_argument("-m", "--mac", dest = "mac", help = "Use MAC as hardware address on NIC.", metavar = "MAC")
    argParser.add_argument("vlanIds", help = "The vlan ids to scan. Format: 1,70-150,42", metavar = "VLAN-IDs")
    argParser.add_argument("-v", "--version", action = "version", version = self.__progVersion)
    try:
      cfg = argParser.parse_args(myargs)
      if DBG: print str(cfg)
    except SystemExit:
      sys.exit()
    except:
      return None
    return cfg
  
  
  def __main(self):
    '''
    The main() method
    '''
    # parse cmd line args
    cfg = self.__parseOptions(sys.argv[1:])
    if cfg == None: sys.exit("[-] Unable to parse command line args.")
    # validate cmd line args
    if cfg.iface in get_if_list():
      self.__iface = cfg.iface
      self.__ifaceOldMac = get_if_hwaddr(self.__iface)
      if cfg.mac is None: self.__ifaceMac = get_if_hwaddr(self.__iface)
      else: self.__ifaceMac = cfg.mac 
    else: 
      sys.exit("[-] No such interface: " + cfg.iface)
    self.__vlanIds = self.__parseVlanIdString(cfg.vlanIds)
    # check if we run as root
    if os.getuid() != 0:
      sys.exit("[-] " + self.__progName + " must be run as root.")
    try:
      # configure interfaces
      if self.__ifaceMac != self.__ifaceOldMac:
        if os.system("ip link set " + self.__iface + " address " + self.__ifaceMac) > 0:
          sys.exit("[-] Unable to set MAC address " + self.__ifaceMac + " for " + self.__iface + ".")
      # put self.__iface into promiscuous mode
      if os.system("ip link set " + self.__iface + " promisc on") > 0:
        sys.exit("[-] Unable to put " + self.__iface + " into promiscuous mode.")
      # moar source code here...
      
      
      for vlan in self.__vlanIds:
        # moar threaded code here!
        pass
      
      print str(TL.getThreadList())
      
      
      
      pass
    finally:
      # put self.__iface back into non-promiscuous mode
      os.system("ip link set dev " + self.__iface + " promisc off")
      # Set MAC address to the old one
      if self.__ifaceMac != self.__ifaceOldMac:
        if os.system("ip link set " + self.__iface + " address " + self.__ifaceOldMac) > 0:
          sys.exit("[-] Unable to set MAC address " + self.__ifaceOldMac + " for " + self.__iface + ".")
    
    return
    
    
  def __parseVlanIdString(self, s = ""):
    '''
    Convert a string 
        s = "2,6, 1 , 85- 88, 2" 
    into a sorted list of unique integers 
        l = [1, 2, 6, 85, 86, 87, 88]
    '''
    if s == "": return []
    l = []
    mylist = []
    # remove all space characters
    s = s.replace(" ", "")
    # divide and conquer
    l.extend(s.split(','))
    for v in l:
      if "-" in v:
        v1 = v.split("-")
        v1 = map(lambda x: int(x), v1)
        vmin = min(v1)
        vmax = max(v1)
        if vmax == vmin:
          mylist.append(vmax)
        else:
          mylist.extend(range(vmin, vmax + 1))
      else:
        mylist.append(int(v))
    # sort and unify
    mylist.sort()
    for m in mylist:
      if mylist.count(m) > 1:
        mylist.remove(m)
    # finished
    return mylist
    
    
    
if __name__ == '__main__':
  Main()
  
