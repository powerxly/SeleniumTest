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
    def setUp(self):
        pass
    def test_flow_01(self):
        '''集团公文-部门通知 20171226
        '''
        uihandle = oa_init()
        docTitle = ""
        docTitle = "集团公文-部门通知（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]部门通知（自动测试）20171024175713'
        oa_try(self,uihandle,docTitle,resume=0,flow='集团公文-部门通知',retry=5)
    def ttttttest_flow_0001(self):
        '''集团公文-部门通知 20171226
        '''
        uihandle = oa_init()
        #uihandle = ''
        '''
        docTitle = "公文（自动测试）-发文流程%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle = "[党委办公室(党群工作部、工会、人力)]公文（自动测试）-发文流程20170920175051"
        #oa_try(self,uihandle,docTitle,resume=12,flow='移动学院团委发文')
        '''
        
        docTitle = "部门通知（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]部门通知（自动测试）20171024175713'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企客户分公司部门通知',retry=3)
        
        '''
        #docTitle = "纪委通知（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        docTitle='[政企分公司]纪委通知（自动测试）20171031152337 '
        oa_try(self,uihandle,docTitle,resume=10,flow='政企分公司纪委通知')
        '''
        '''
        docTitle = "部门培训（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]部门培训（自动测试）20171024115732'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司部门培训通知')
        '''
        '''
        docTitle = "部门审批单（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]部门审批单（自动测试）20171025131132'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司部门审批单')
        '''
        '''
        docTitle = "调度令（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]调度令（自动测试）20171027112030'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司调度令（与集团相关）')
        '''
        '''
        docTitle = "电子督办单（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]电子督办单（自动测试）20171031152337'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企客户分公司电子督办单')
        '''
        '''
        docTitle = "[政企分公司]督办事项管理"
        #docTitle='[政企分公司]督办事项（自动测试）20171031152337'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司督办事项管理审批')
        '''
        '''
        docTitle = "政企分公司党办文件（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]政企分公司党办文件（自动测试）20171107160728'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司党办文件')
        '''
        '''
        docTitle = "政企分公司（通知）（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]政企分公司（通知）（自动测试）20171108152628'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司（通知）')
        '''
        '''
        docTitle = "工会委员会文件（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]工会委员会文件（自动测试）20171108105535'
        oa_try(self,uihandle,docTitle,resume=0,flow='政企分公司工会委员会文件')
        '''
        '''
        #docTitle = "党委会会议纪要（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        docTitle='[政企分公司]党委会会议纪要（自动测试）20171117095052'
        oa_try(self,uihandle,docTitle,resume=6,flow='政企客户分公司党委会议纪要')
        '''
        '''
        docTitle = "信息港中心会议纪要（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[信息港中心]信息港中心会议纪要（自动测试）20171123155935'
        oa_try(self,uihandle,docTitle,resume=7,flow='信息港中心专题办公会会议纪要')
        '''
        '''
        #docTitle = "发文（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
        #docTitle='[政企分公司]呈批件（自动测试）20171122103252'
        docTitle='[人力资源部]发文（自动测试）20171122153448'
        oa_try(self,uihandle,docTitle,resume=4,flow='研究院发文（送集团）')
        '''
        
    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()