# -*- coding: utf-8 -*-
'''
Created on Apr 9, 2015

@author: 0_o -- null_null (nu11.nu11 [at] yahoo.com)
         Oh, and it is n-u-one-one.n-u-one-one, no l's...
         Wonder how the guys at packet storm could get this wrong :(

# vim: set tabstop=2 shiftwidth=2 smarttab expandtab
# vim: retab

'''
__updated__ = "2015-04-09"


from Common.singleton import Singleton

import threading



class ThreadList(object):
  '''
  Implements and maintains a list of threads.
  Singleton Object.
  '''
  __metaclass__ = Singleton
  
  
  def __init__(self):
    self.__threadList = []
    self.__threadListLock = threading.Lock()
    self.__resultDict = {}
    self.__resultCond = {}
    return
  
  
  def getThreadList(self):
    '''
    Return a copy of the list of threads
    '''
    tl = []
    with self.__threadListLock:
      tl.extend(self.__threadList)
    return tl
  
  
  def createThread(self, myThreadClass):
    '''
    Create a thread from class myThreadClass
    '''
    myThread = None
    # moar code here
    return myThread
  
  
  def startThread(self, myThreadInstance):
    '''
    Start a myThreadInstance, created by createThread()
    '''
    retval = False
    # moar code here
    return retval
  
  
  def stopThread(self, myThreadInstance):
    '''
    Stop a myThreadInstance, created by createThread()
    '''
    retval = False
    # moar code here!
    return retval



# make an instance of ThreadList
threadList = ThreadList()

