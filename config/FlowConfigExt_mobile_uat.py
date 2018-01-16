#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-07-26 13:20
# config/FlowConfig.py

# 封装对流程及其部件的访问参数,及其获取方式（目前支持采用ini和excel文件的读取）
# 
__default_encoding__="gbk"
#from FlowConfig import SiteConfig
from config.FlowConfig import *

import xlrd,xlwt
import sys,os
import json

#__defaultFlowPath__:缺省的流程配置目录
__defaultFlowPath__='./config/flows'

        
class SmartFlow(FlowConfig):
    # 构造方法，用来接收selenium的driver对象
    def __init__(self,flowName,source='excel',path=__defaultFlowPath__):
        self.flowName = flowName
        self.source= source
        self.__flowConfigPath__=path
        self.__flowConfig__ = self.getFlowsConfig()
    def readConfigFromExcel(self,fileNames):
        #与标准相比，excel文件输入为中移动增加了opiniontype列的处理
        #flows是返回的参数
        flows = {}
        flowConfigPath = self.__flowConfigPath__
        for l in fileNames:
            xlsFile = xlrd.open_workbook(os.path.join(flowConfigPath,l))
            flowName = l[:l.rindex('.')]

            flow = {}
            
            #流程基本信息
            values = {}     
            sheet = xlsFile.sheet_by_name('基本信息'.decode(__default_encoding__))
            section = 'flow'
            #--流程标题
            values['title'] = toEncode(sheet.cell(2,2).value)
            #--测试运行路径名
            runpath = toEncode(sheet.cell(3,2).value).split(',')
            values['runpath'] = "%s" % runpath
            #填写流程基本信息区段
            flow['flow'] = values
            
            #获取该流程的测试运行路径的详细信息
            types={'开始'.decode(__default_encoding__):'start','结束'.decode(__default_encoding__):'end','流程跟踪截图'.decode(__default_encoding__):'screenshot'}
            paths = {}
            nodes = {}
            others = ['','节点名'.decode(__default_encoding__)]
            leading = True
            for r in runpath:
                rSheet = xlsFile.sheet_by_name(r.decode(__default_encoding__))
                path = []
                for i in range(0,rSheet.nrows):
                    node = {}
                    nodeName = rSheet.cell(i,1).value
                    if nodeName=='' and leading:
                        #前导空值,应该跳过
                        continue
                    if nodeName=='节点名'.decode(__default_encoding__):
                        #前导空值结束
                        leading = False
                        continue
                    #非前导环节，遇到空值则结束
                    if nodeName=='' and not leading:
                        break
                    #是节点，添加到path和节点信息中
                    path.append(toEncode(nodeName))
                    #print('nodename:%s' % nodeName)
                    
                    #节点信息
                    #-节点类型
                    nodeType = rSheet.cell(i,2).value
                    if types.has_key(nodeType):
                        node['type'] = types[nodeType]
                    #-user  
                    user = rSheet.cell(i,3).value
                    if user!='':
                        node['user'] = toEncode(user)
                    #-transition
                    transition = rSheet.cell(i,4).value
                    if transition!='':
                        node['transition'] = toEncode(transition)
                    #-assignee
                    assignee = rSheet.cell(i,5).value
                    if assignee!='':
                        node['assignee'] = toEncode(assignee)
                    #-opinion
                    #移动的特殊处理，添加了意见类型选择
                    opinion = rSheet.cell(i,6).value +'|' + rSheet.cell(i,7).value
                    #print("---------opinion:%s " % opinion)
                    if opinion!='|':
                        node['opinion'] = toEncode(opinion)
                    #-forms
                    forms = toEncode(rSheet.cell(i,8).value)
                    if forms!='':
                        node['forms'] = forms
                    #-startMenu
                    startMenu = rSheet.cell(i,9).value
                    if startMenu!='':
                        #与ini版本兼容,因为当初ini版时字符串（json格式）转换有问题，所以json内部均为gbk，历史遗留问题
                        node['startMenu'] = toEncode(startMenu)
                    #-actions
                    actions = rSheet.cell(i,10).value 
                    if actions!='':
                        node['actions'] = toEncode(actions)
                    #-screenshot
                    screenshot = rSheet.cell(i,11).value 
                    if screenshot!='':
                        node['filename'] = toEncode(screenshot)
                    
                    #将填写好的节点，填入节点区段
                    nodes[toEncode(nodeName)] = "%s" % node
                #转成与ini类似的格式
                paths[toEncode(r)] = "%s" % path
            flow['paths'] = paths
            flow['nodes'] = nodes
            flow['forms'] = self.readFormsFromSheet(xlsFile)
            flows[flowName]=flow
        return flows
    #与ini版本兼容,因为当初ini版时字符串（json格式）转换有问题，所以json内部均为gbk，历史遗留问题
    def readFormsFromSheet(self,xlsFile):
        sheet = xlsFile.sheet_by_name('输入表单'.decode(__default_encoding__))
        startRow =3
        startCol = 1
        forms={}
        for i in range(startRow,sheet.nrows):
            fields = []
            
            formName = toEncode( sheet.cell(i,startCol).value)
            if forms.has_key(formName):
                #之前遇到过的表单
                fields = forms[formName]
            else:
                #遇到新表单,初始化字段列表
                fields = []
                forms[formName]=fields
            fieldName = toEncode(sheet.cell(i,startCol+1).value)
            #excel可以获取到其他类型的域值，例如整型，对我们统一变成字符串即可
            fieldValue = toEncode(sheet.cell(i,startCol+2).value)
            fieldType = toEncode(sheet.cell(i,startCol+3).value)
            #兼容历史设置文件，防止老的测试文件因为没有第5列数据（其他参数列）而报错
            try:
                r = {}
                v = toEncode(sheet.cell(i,startCol+4).value)
                fieldParams = v
            except:
                fieldParams = ''
            #增加新的字段设置
            fields.append([fieldName,fieldValue,fieldType,fieldParams])

        #改成文本值，兼容ini处理模式
        for i in forms.keys():
            v = forms[i]
            forms[i] = "%s" % v
        
        return forms    
        
