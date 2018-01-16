#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-10 16:34
# all_flow.py

import unittest
#import HTMLTestRunner
from encapsulation.unittest.SmartHTMLTestRunner import SmartHTMLTestRunner
import time,os,datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

import pdb

# 取test_case文件夹下所有用例文件
def creatsuitel(lists):
    testunit = unittest.TestSuite()
    # discover 方法定义
    discover = unittest.defaultTestLoader.discover(lists, pattern='start_*.py', top_level_dir=None)
    #discover 方法筛选出来的用例，循环添加到测试套件中
    for test_suite in discover:
        for test_case in test_suite:
            testunit.addTests(test_case)
            #print(testunit)
    return testunit
list_1 = 'test_case\\test_case_flow'
#pdb.set_trace()
alltestnames = creatsuitel(list_1)
#pdb.set_trace()

#取前面时间加入到测试报告文件名中
now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(time.time()))
filename = "report\\"+now+'_result.html' #定义个报告存放路径，支持相对路径。
fp = open(filename, 'wb')
runner = SmartHTMLTestRunner(stream=fp, title='自动测试运行结果报告', description='报告描述')

if __name__ == "__main__":
    # 执行测试用例集并生成报告
    #runner = unittest.TextTestRunner()
    runner.run(alltestnames)
fp.close()