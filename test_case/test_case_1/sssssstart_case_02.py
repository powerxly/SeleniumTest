#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 15:30
# test_case/test_case_1/start_case_01.py

import unittest
from function.function_02 import *
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
# 用例
class Case_02(unittest.TestCase):
    def setUp(self):
        pass


    def test_aqkkoa_simple_gowen(self):
        #初始化句柄
        uihandle = aqkkoa_init()
        #登录
        aqkkoa_login(uihandle,"宋金超")
        
        docTitle = "公文（自动测试）-发文流程%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        aqkkoa_gongwen_fawen_new_save(self,uihandle,docTitle)
        #aqkkoa_gongwen_fawen_new_cancel(self,uihandle)
        check_gongwen_view_Doc(self,uihandle,docTitle)

        aqkkoa_gongwen_fawen_next(self,uihandle,docTitle,'宋金超','宋金超（局室领导）同意')
        
        #uihandle.Click('系统登出按钮')

        print('打印方法名：test_aqkkptsj')
        #uihandle.quit()

	def ttest_aqkkoa(self):
        #初始化句柄
        uihandle = aqkkoa_init()
        #登录
        aqkkoa_login(uihandle,"宋金超")
        
        docTitle = "公文（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        aqkkoa_gongwen_fawen_new_save(self,uihandle,docTitle)
        #aqkkoa_gongwen_fawen_new_cancel(self,uihandle)
        check_gongwen_view_Doc(self,uihandle,docTitle)

        uihandle.Click('系统登出按钮')

        print('打印方法名：test_aqkkptsj')
        uihandle.quit()
    def ttest_aqkkoaview(self):
        #初始化句柄
        uihandle = aqkkoa_init()
        #登录
        aqkkoa_login(uihandle,"宋金超")
        
        docTitle = '公文（自动测试）'
        check_gongwen_view_Doc(self,uihandle,docTitle)

        uihandle.Click('系统登出按钮')

        print('打印方法名：test_aqkkptsj')
        uihandle.quit()
    def ttest_aqkkoa_gongwen_next_step(self):
        #初始化句柄
        uihandle = aqkkoa_init()
        #登录
        aqkkoa_login(uihandle,"宋金超")
        
        docTitle = '公文（自动测试）'
        aqkkoa_gongwen_fawen_next(self,uihandle,docTitle,'宋金超','宋金超（局室领导）同意')
        
        uihandle.Click('系统登出按钮')

        print('打印方法名：test_aqkkptsj')
        uihandle.quit()
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()