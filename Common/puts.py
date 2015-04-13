# -*- coding: utf-8 -*-
'''
Created on Apr 13, 2015

@author: 0_o -- null_null (nu11.nu11 [at] yahoo.com)
         Oh, and it is n-u-one-one.n-u-one-one, no l's...
         Wonder how the guys at packet storm could get this wrong :(

# vim: set tabstop=2 shiftwidth=2 smarttab expandtab
# vim: retab

Acknowledgement:
This code is a stripped down version of what I found here: sf.net/p/hl7socketreader

'''
__updated__ = "2015-04-13"


from collections import deque
import threading
import time
import sys


class Puts(threading.Thread):
  
  def __init__(self):
    self.__queue = deque()
    self.__condition = threading.Condition()
    self.__running = 1
    self.__acceptInput = 1
    threading.Thread.__init__(self)
    self.start()
    
    
  def getState(self):
    return self.__running
    
  
  def run(self):
    while self.__running > 0:
      s = None
      with self.__condition:
        if len(self.__queue) <= 0 and self.__running > 0:
          self.__condition.wait()
        while len(self.__queue) > 0 and self.__running > 0:
          (s, w) = self.__queue.popleft()
          if s:
            if w: print s
            else: print s,
            sys.stdout.flush()
    return


  def puts(self, s, wrap = True):
    if self.__acceptInput > 0:
      with self.__condition:
        self.__queue.append((str(s), wrap))
        self.__condition.notifyAll()
    
    
  def stopThread(self):
    if self.__running:
      self.__acceptInput = 0
      while len(self.__queue) > 0:
        with self.__condition:
          self.__condition.notifyAll()
        time.sleep(0.1)
      self.__running = 0
      with self.__condition:
        self.__condition.notifyAll()
      sys.stdout.flush()
    return
    
        
  def __del__(self):
    if self.__running:
      self.stopThread()
    return


c = Puts()
