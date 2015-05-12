# -*- coding: utf-8 -*-
'''
Created on Apr 9, 2015

@author: 0_o -- null_null (nu11.nu11 [at] yahoo.com)
         Oh, and it is n-u-one-one.n-u-one-one, no l's...
         Wonder how the guys at packet storm could get this wrong :(

# vim: set tabstop=2 shiftwidth=2 smarttab expandtab
# vim: retab

'''
__updated__ = "2015-05-11"


from Common.singleton import Singleton

import vlanScanner
import threading



class ThreadList(object):
  '''
  Implements and maintains a list of threads.
  Singleton Object.
  '''
  __metaclass__ = Singleton
  
  
  def __init__(self):
    self.__threadList = []  # {'instance': object, 'vlan': str, 'nic': str}
    self.__threadListLock = threading.Lock()
    self.__resultDict = {}
    self.__resultDictLock = threading.Lock()
    self.__resultCond = threading.Condition()
    return
  
  
  def getThreadList(self):
    '''
    Return a copy of the list of threads
    '''
    tl = []
    with self.__threadListLock:
      tl.extend(self.__threadList)
    return tl
  
  
  def getAnyAliveState(self):
    '''
    Returns:
        True:  if any thread is still alive
        False: otherwise
    '''
    with self.__threadListLock:
      for t in self.__threadList:
        if t.get('instance').getState() > 0:
          return True
    return False
  
  
  def getAliveCount(self):
    '''
    Returns an integer of threads considered alive.
    '''
    count = 0
    with self.__threadListLock:
      for t in self.__threadList:
        if t.get('instance').getState() > 0:
          count += 1
    return count
  
  
  def createThread(self, scanMode = None, vlanId = None, nic = None, mac = None):
    '''
    Create a thread with the params scanMode, vlanId, nic, mac
    '''
    if not (scanMode or vlanId or nic): return None
    if not scanMode in vlanScanner.scanModes: return None
    if not vlanId in vlanScanner.validVlanIds: return None
    if not type(nic) == str: return None
    if not mac: return None
    myThread = {} 
    t = None
    with self.__threadListLock:
      if scanMode == 'active':
        t = vlanScanner.VlanScanActive(vlanId, nic, mac, self.__resultDict, self.__resultDictLock)
      if scanMode == 'passive':
        t = vlanScanner.VlanScanPassive(vlanId, nic, mac, self.__resultDict, self.__resultDictLock)
      myThread.update({'instance': t, 'vlan': vlanId, 'nic': nic, 'mac': mac})
      self.__threadList.append(myThread)
    return myThread
  
  
  def startThread(self, myThread):
    '''
    Start a myThread.get('instance'), created by createThread()
    Return values:
        True - thread started successfully
        False - any error occurred
    '''
    myThreadInstance = myThread.get('instance')
    try:
      myThreadInstance.start()
    except RuntimeError:
      return False  
    return True
  
  
  def stopThread(self, myThread):
    '''
    Stop a myThread.get('instance'), created by createThread()
    '''
    retval = False
    myThreadInstance = myThread.get('instance')
    if myThreadInstance.getState() > 0:
      with self.__threadListLock:
        myThreadInstance.stopThread()
        self.__threadList.remove(myThread)
        retval = True
    return retval
  
  
  def stopAll(self):
    '''
    Stop all running instances
    '''
    retval = True
    with self.__threadListLock:
      for t in self.__threadList:
        if self.stopThread(t) == False:
          retval = False
    return retval



# make an instance of ThreadList
threadList = ThreadList()

