#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 15:30
# test_case/test_case_1/start_case_01.py
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import unittest
from function.function_01 import *
# 用例
class Case_01(unittest.TestCase):
    ''' mytest 001
        hello
    '''
    def setUp(self):
        pass

    def test_zzk(self):
        ''' try ok
            next
        '''
        #search("哇塞好玩")
        print('打印方法名：test_zzk')

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()