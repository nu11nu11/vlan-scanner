# -*- coding: utf-8 -*-
'''
Created on Apr 9, 2015

@author: 0_o -- null_null (nu11.nu11 [at] yahoo.com)
         Oh, and it is n-u-one-one.n-u-one-one, no l's...
         Wonder how the guys at packet storm could get this wrong :(

# vim: set tabstop=2 shiftwidth=2 smarttab expandtab
# vim: retab

'''
__updated__ = "2015-05-12"


from Common.puts import c
from VSCAN.Scanner.broadcastDhcpDiscover import DhcpDiscover

import threading
import time
import os
import random


# To get rid of the PyDev warning:
c.getState()



class VlanScanActive(threading.Thread):
  '''
  Do an active scan on one vlan
  '''
  
  def __init__(self, vlan, nic, mac, results, resultlock):
    global c
    self.__vlan = str(vlan)
    self.__nic = nic
    self.__mac = mac
    self.__resultDict = results
    self.__resultDictLock = resultlock
    self.__vlanIface = self.__nic + '.' + self.__vlan
    self.__running = 1
    threading.Thread.__init__(self)
    return None
    
    
  def getState(self):
    return self.__running
    
    
  def run(self):
    global c
    if self.__running:
      if os.system('ip link add link ' + self.__nic + ' name ' + self.__vlanIface + ' type vlan id ' + self.__vlan) > 0:
        c.puts('[-] Unable to create vlan interface ' + self.__vlanIface)
        self.stopThread()
        return False
      else:
        os.system('ip link set ' + self.__vlanIface + ' up')
        c.puts('[+] Created interface ' + self.__vlanIface)
      c.puts("[*] Scanning VLAN: " + str(self.__vlan))
      
      
      
      # TODO: MOAR SOURCE CODE - DO A SCAN
      # time.sleep(random.randint(1, 5))
      dhcpThread = DhcpDiscover(self.__vlanIface, self.__mac, self.__resultDict, self.__resultDictLock)
      dhcpThread.start()
      
      # start more scans
      
      dhcpThread.join()
      self.stopThread()
    return True
  
  
  def stopThread(self):
    global c
    if self.__running: 
      self.__running = 0
      os.system('ip link set ' + self.__vlanIface + ' down')
      if os.system('ip link delete ' + self.__vlanIface) > 0:
        c.puts('[-] Unable to remove vlan interface ' + self.__vlanIface)
      else:
        c.puts('[+] Removed interface ' + self.__vlanIface)
      return True
    return False
    
    
  def __del__(self):
    self.stopThread()



class VlanScanPassive(threading.Thread):
  '''
  NOT IMPLEMENTED YET
  '''
  
  def __init__(self, vlanId):
    import sys
    sys.exit("[-] Passive scanning is not implemented yet!")
    self.__vlanId = vlanId
    self.__running = 1
    threading.Thread.__init__(self)
    
    
  def run(self):
    pass
  
  
  def stop(self):
    self.__running = 0
    
    
  def __del__(self):
    # yet no idea what to do here...
    pass
  
  pass 


scanModes = ['active', 'passive']
validVlanIds = range(0, 4095 + 1)




