# -*- coding: utf-8 -*-
'''
Created on Apr 8, 2015

@author: 0_o -- null_null (nu11.nu11 [at] yahoo.com)
         Oh, and it is n-u-one-one.n-u-one-one, no l's...
         Wonder how the guys at packet storm could get this wrong :(

# vim: set tabstop=2 shiftwidth=2 smarttab expandtab
# vim: retab

'''
__updated__ = "2015-04-14"


version = "0.1"
__author__ = "0_o -- null_null"
__email__ = "nu11.nu11 [at] yahoo.com"
__license__ = "GPLv3.0"
__copyright__ = "Copyright 2015 until today: " + __author__ \
                + ' (' + __email__ + ')'
__url__ = ""

  
from Common.puts import c
from Common.debug import DEBUG_VSCAN as DBG
from VSCAN.threads import threadList as TL

from scapy.all import get_if_list, get_if_hwaddr

import argparse
import traceback
import time
import sys
import os


# To get rid of the PyDev warning:
c.getState()



class Main(object):
  
  def __init__(self):
    self.__progName = "vscan"
    self.__progVersion = self.__progName + " " + version
    self.__iface = None
    self.__ifaceMac = None
    self.__ifaceOldMac = None
    self.__threads = 0
    self.__vlanIds = []
    self.__running = 0
    
  
  def main(self):
    '''
    The main() method
    '''
    global c
    # parse cmd line args
    cfg = self.__parseOptions(sys.argv[1:])
    if cfg is False: return False
    (errcode, errmsg) = self.__parseCmdLine(cfg)
    if errcode > 0: 
      c.puts(errmsg)
      return False
    # check if we run as root
    if os.getuid() != 0:
      c.puts("[-] " + self.__progName + " must be run as root.")
      return False
    try:
      # configure interfaces
      if self.__ifaceMac != self.__ifaceOldMac:
        if os.system("ip link set " + self.__iface + " address " + self.__ifaceMac) > 0:
          c.puts("[-] Unable to set MAC address " + self.__ifaceMac + " for " + self.__iface + ".")
          return False
      # put self.__iface into promiscuous mode
      if os.system("ip link set " + self.__iface + " promisc on") > 0:
        c.puts("[-] Unable to put " + self.__iface + " into promiscuous mode.")
        return False
      # reverse vlan id list to enable pop() from the list head
      vlanList = []
      vlanList.extend(self.__vlanIds)
      vlanList.reverse()
      # staggered vlan scan
      while len(vlanList) > 0:
        if TL.getAliveCount() < self.__threads:
          v = vlanList.pop()
          t = TL.createThread('active', v, self.__iface)
          TL.startThread(t)
          
          
      # TODO: MOAR SOURCE CODE - COLLECT AND EVALUATE RESULTS
          
          
      # scans have finished or an error has occurred
    finally:
      # put self.__iface back into non-promiscuous mode
      os.system("ip link set dev " + self.__iface + " promisc off")
      # Set MAC address to the old one
      if self.__ifaceMac != self.__ifaceOldMac:
        if os.system("ip link set " + self.__iface + " address " + self.__ifaceOldMac) > 0:
          c.puts("[-] Unable to set MAC address " + self.__ifaceOldMac + " for " + self.__iface + ".")
          return False
    
    return
    
    
  def __parseOptions(self, myargs):
    '''
    Parse the command line options
    '''
    global c
    argParser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    argParser.add_argument("-i", "--iface", dest = "iface", default = "eth0", help = "The hardware network interface to scan.", metavar = "NIC")
    argParser.add_argument("-m", "--mac", dest = "mac", help = "Use MAC as hardware address on NIC.", metavar = "MAC")
    argParser.add_argument("-t", "--threads", type = int, dest = "threads", default = 10, help = "Scan NUM_THREADS vlan ids concurrently.", metavar = "NUM_THREADS")
    argParser.add_argument("vlanIds", help = "The vlan ids to scan. Format: 1,70-150,42", metavar = "VLAN-IDs")
    argParser.add_argument("-v", "--version", action = "version", version = self.__progVersion)
    try:
      cfg = argParser.parse_args(myargs)
      if DBG: c.puts(str(cfg))
    except SystemExit:
      return False
    except:
      return None
    return cfg
  
  
  def __parseCmdLine(self, cfg = None):
    '''
    Parse whatever argparse has got.
    '''
    errcode = 0
    errmsg = ''
    if cfg == None:
      errcode = 1 
      errmsg = "[-] Unable to parse command line args."
      return (errcode, errmsg)
    # validate cmd line args
    if cfg.iface in get_if_list():
      self.__iface = cfg.iface
      self.__ifaceOldMac = get_if_hwaddr(self.__iface)
      if cfg.mac is None: self.__ifaceMac = get_if_hwaddr(self.__iface)
      else: self.__ifaceMac = cfg.mac 
    else:
      errcode = 2
      errmsg = "[-] No such interface: " + cfg.iface
      return (errcode, errmsg)
    if cfg.threads > 0: self.__threads = cfg.threads
    else:
      errcode = 3
      errmsg = "[-] A positive number of threads must be given."
    self.__vlanIds = self.__parseVlanIdString(cfg.vlanIds)
    if self.__vlanIds == []:
      errcode = 10
      errmsg = "[-] vlan range string is invalid."
      return (errcode, errmsg)
    return (errcode, errmsg)
  
  
  def __parseVlanIdString(self, s = ""):
    '''
    Convert a string 
        s = "2,6, 1 , 85- 88, 2" 
    into a sorted list of unique integers 
        l = [1, 2, 6, 85, 86, 87, 88]
    '''
    if s == "": return []
    try:
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
      # but what if self.__vlanIds is [] -- scan them all!
      if mylist == []: mylist = range(0, 4095 + 1)
    except:
      return []
    # finished
    return mylist
    
    
    
if __name__ == '__main__':
  retval = False
  try:
    m = Main()
    retval = m.main()
  except:
    traceback.print_exc(file = sys.stdout)
    for t in TL.getThreadList():
      TL.stopThread(t)
  finally:
    while TL.getAnyAliveState():
      time.sleep(0.1)
    c.stopThread()
    c.join()
    if retval: sys.exit()
    else: sys.exit(1)

