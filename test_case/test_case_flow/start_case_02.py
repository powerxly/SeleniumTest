#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 15:30
# test_case/test_case_flow/start_case_01.py

import unittest
from function.function_mobile_uat import *

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
# 用例
class Case_02(unittest.TestCase):
    '''政企分公司公文
	'''
    def setUp(self):
        pass
    def test_flow_01(self):
        '''政企分公司-党办文件 20171226
        '''
        uihandle = oa_init()
        
        docTitle = "党办文件（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]党办文件（自动测试）20180109100649'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司党办文件',retry=5)
        
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()