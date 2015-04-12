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



#===============================================================================
# # Create a Singleton Object.
# # Usage:
# #Python2
# class MyClass(BaseClass):
#     __metaclass__ = Singleton
# 
# #Python3
# class MyClass(BaseClass, metaclass=Singleton):
#     pass
#===============================================================================
class Singleton(type):
  _instances = {}
  def __call__(cls, *args, **kwargs):  # @NoSelf
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]


