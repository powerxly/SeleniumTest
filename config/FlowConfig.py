#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-07-26 13:20
# config/FlowConfig.py

# 封装对流程及其部件的访问参数,及其获取方式（目前支持采用ini和excel文件的读取）
# 
__default_encoding__="gbk"
#from config.SiteConfig import SiteConfig

import ConfigParser
import xlrd,xlwt
import sys,os
import json

#__defaultFlowPath__:缺省的流程配置目录
__defaultFlowPath__='./config/flows'


def getFilesInDir(dir):
    path = os.listdir(dir)
    return path
def getSourceFiles(flowName,flowConfigPath=__defaultFlowPath__,sourceType='ini'):
    #获取流程设置目录下所有的配置文件，文件名就是流程配置的关键字
    if(sourceType=='excel'):
        filter = ['xls','xlsx']
    else:
        filter = ['ini']
    lists=[]
    listdir=getFilesInDir(flowConfigPath)
    for l in listdir:
        if l.find('.')>=0:
            suffix = l[l.rindex('.')+1:].lower()
            name = l[:l.rindex('.')].lower()
            if suffix in filter and name.lower() == flowName.lower():
                lists.append(l)
    return lists
'''
def getFlows(flowConfigPath=__defaultFlowPath__,sourceType='ini'):
    #流程设置文件的文件名，就是流程设置的关键字
    lists=[]
    listdir=getSourceFiles(flowConfigPath,sourceType)
    for l in listdir:
        lists.append(l[:l.rindex('.')])
    return lists

def getFlowFiles(flowName,flowConfigPath=__defaultFlowPath__,sourceType='ini'):
    #流程设置文件的文件名，就是流程设置的关键字
    lists=[]
    listdir=getSourceFiles(flowConfigPath,sourceType)
    for l in listdir:
        lists.append(l)
    return lists
'''
        


def findHZ(dict,toSearch,code="default"):
    #如果汉字编码没有显示说明，那么缺省会依序尝试__default_encoding__和unicode这两种汉字编码，增强系统容错性。
    r="";
    #print(toSearch)
    #print(dict)
    #toSearch=toSearch.lower()
    if(code.lower()=="default"):
        try:
            r=dict[toSearch]
        except Exception,e:
            try:
                r=findHZ(dict,toSearch,code=__default_encoding__)
            except Exception,e:
                r=""
    else:
        try:
            r=dict[toSearch.decode(__default_encoding__)]
        except:
            r=''
    return r
    
class FlowConfig():
    __flowConfigPath__=''
    __flowConfig__={}
    def __init__(self,flowName,source='ini',path=__defaultFlowPath__):
        self.flowName = flowName
        self.source= source
        self.__flowConfigPath__=path
        self.__flowConfig__ = self.getFlowsConfig()
        pass
    def __str__(self):
        return json.dumps(self.__flowConfig__)
    def toJson(self):
        return(self.__flowConfig__)
    def getFlow(self,flow,code="default"):
        return(findHZ(self.__flowConfig__,flow,code))
    def getNodes(self,flow,code="default"):
        return(findHZ(self.getFlow(flow,code),"nodes",code))
    def getNode(self,flow,nodename,code="default"):
        #获取流程的节点信息
        return getDict(self.getNodes(flow,code),nodename,code)

    #获取流程节点详细信息[name]
    def getFlowInfos(self,flow,code="default"):
        return(findHZ(self.getFlow(flow,code),"flow",code))
    def getFlowTitle(self,flow,code="default"):
        return(findHZ(self.getFlowInfos(flow,code),'title',code))
    def getRunPaths(self,flow,code="default"):
        #获取需要测试的流程路径，这里只返回path名称，具体定义保存在paths区段中
        return getArray(self.getFlowInfos(flow,code),'runpath',code)
        
    def getPaths(self,flow,code="default"):
        return(findHZ(self.getFlow(flow,code),"paths",code))
    def getPath(self,flow,name,code="default"):
        return getArray(self.getPaths(flow,code),name,code)

    def getForms(self,flow,code="default"):
        return(findHZ(self.getFlow(flow,code),"forms",code))
    def getForm(self,flow,name,code="default"):
        return getArray(self.getForms(flow,code),name,code)
    def getFlowsConfig(self):
        #获取流程设置目录下的所有相关配置文件，将其内容读取为json配置数据，以流程关键字（文件名）为查询关键字
        #数组decodings里存放的是需要被解码成unicode的参数，例如xpath中的value，中文应该解码成unicode，否则查不到
        decodings=[]
        flowName = self.flowName
        flowConfigPath = self.__flowConfigPath__
        sourceType = self.source
        names = getSourceFiles(flowName,flowConfigPath,sourceType)
        if(sourceType=='excel'):
            flows = self.readConfigFromExcel(names)
        else:
            flows = self.readConfigFromIni(names)
        return flows
    def readConfigFromIni(self,fileNames):
        #flows是返回的参数
        flows = {}
        flowConfigPath = self.__flowConfigPath__
        cf = ConfigParser.ConfigParser()
        for l in fileNames:
            flowName = l[:l.rindex('.')]
            sections={}
            cf.read(os.path.join(flowConfigPath,l))
            secs=cf.sections()
            #print(secs)
            for s in secs:
                keyValues={}
                keys = cf.options(s)
                for k in keys:
                    #print('keys:%s' % k)
                    v = cf.get(s,k)
                    #print('v:%s' % repr(v))
                    '''
                    #v = cf.get(s,k).decode(__default_encoding__)
                    #print('v:%s' % repr(v))
                    if(v[0]=='[' and v[-1:]==']'):
                        #具体的元素的查找参数以二维数组的方式存放，例如['id', 'zzk_q']，这里需要处理一下，使得后面元素查找时可以直接使用
                        v = eval(v)
                        #eval 解析数组，不知为何总是把内容转成utf-8，即使源字符串中已经是unicode
                        #for i in range(0,len(v)):
                        #    v[i]=v[i].decode(__default_encoding__)
                         
                        if(len(v)==2):
                            if(v[0].lower() in decodings):
                                #参数名称包含在需要解码的参数名数组中，值需要解码成unicode
                                v[1]=v[1].decode(__default_encoding__)
                        
                    keyValues[k.decode(__default_encoding__)] = v
                    '''
                    keyValues[k] = v
                #sections[s.decode(__default_encoding__)]=keyValues
                sections[s]=keyValues
            #flows[l.decode(__default_encoding__)]=sections
            flows[flowName]=sections
        return flows

    def readConfigFromExcel(self,fileNames):
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
                    opinion = rSheet.cell(i,6).value 
                    if opinion!='|':
                        node['opinion'] = toEncode(opinion)
                    #-forms
                    forms = toEncode(rSheet.cell(i,7).value)
                    if forms!='':
                        node['forms'] = forms
                    #-startMenu
                    startMenu = rSheet.cell(i,8).value
                    if startMenu!='':
                        #与ini版本兼容,因为当初ini版时字符串（json格式）转换有问题，所以json内部均为gbk，历史遗留问题
                        node['startMenu'] = toEncode(startMenu)
                    #-actions
                    actions = rSheet.cell(i,9).value 
                    if actions!='':
                        node['actions'] = toEncode(actions)
                    #-screenshot
                    screenshot = rSheet.cell(i,10).value 
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
            fieldParams = toEncode(sheet.cell(i,startCol+4).value)
            #增加新的字段设置
            fields.append([fieldName,fieldValue,fieldType,fieldParams])

        #改成文本值，兼容ini处理模式
        for i in forms.keys():
            v = forms[i]
            forms[i] = "%s" % v
        
        return forms    

def toEncode(v):
    t=type(v)
    if t == unicode:
        r = v.encode(__default_encoding__)
    elif t== float:
        #特殊处理，因为excel数字域默认是float类型，转换后4会变成4.0,应急处理，以后再想好的办法。
        if(v==int(v)):
            r = "%i" % v
        else:
            r = "%s" % v
    elif t==str:
        r = v
    else:
        print('!!!!!!there is still other type to deal:%s' % type(v))
        r = v
    return r
    
#计算设置中传入的伪变量,例如替换$idx$, context={'idx':1}
def compute(self,value,context={}):
    #目前只有字符串才进行替换，其他类型以后再说
    if type(value)==str:
        for k in context.keys():
            findStr ='$'+k+'$'
            newStr = '%s' % context[k]
            value = value.replace(findStr,newStr)
    return value
    
    
def MyEqual(obj1,obj2):
    try:
        equal = (obj1==obj2)
    except:
        equal = False
    return equal
class Compare():
    history=[]
    complete = False
    equal = False
    stack=[]
    level=0
    def __init__(self,obj1,obj2):
        self.compare(obj1,obj2)
    def compare(self,obj1,obj2):
        self.level = self.level+1
        if type(obj1)!= type(obj2):
            self.equal = False
            self.history.append(self.outputStack() +'type mismatched')
            self.complete = True
        elif(MyEqual(obj1,obj2)):
            self.equal = True
            self.complete = True
        else:
            self.equal = False
            self.complete = True
            if type(obj1)==dict:
                if(not MyEqual(obj1.keys(),obj2.keys())):
                    self.history.append( self.outputStack()+ 'keys mismatched')
                else:
                    for i in obj1.keys():
                        self.stack.append("--level%i:dict:idx(%s)" % (self.level,i))
                        result = self.compare(obj1[i],obj2[i])
                        self.stack.pop()
            elif type(obj1) == list:
                if(len(obj1)!=len(obj2)):
                    self.history.append( self.outputStack()+ 'array length mismatched')
                else:
                    for i in range(0,len(obj1)):
                        self.stack.append("--level%i:List:idx(%i)" % (self.level,i))
                        result = self.compare(obj1[i],obj2[i])
                        self.stack.pop()
            else:
                #self.history.append( self.outputStack()+ 'value is mismatched(%s vs %s)' % (obj1,obj2))
                pass
        self.level = self.level-1
    def outputStack(self):
        return 'stacktrace(%s):' % '.'.join(self.stack)

def getArray(contr,nodeName,code):
    #获取指定信息
    try:
        str = findHZ(contr,nodeName,code)
        r = eval(str)
    except:
        print('getArray:error in finding node(%s) code(%s)' % (nodeName,code))
        return []
    return r
def getDict(contr,nodeName,code):
    #获取指定信息
    try:
        str = findHZ(contr,nodeName,code)
        #print(str)
        r = eval(str)
    except:
        print('getDict:error in finding node(%s) code(%s)' % (nodeName,code))
        return {}
    return r
def getStr(contr,nodeName,code):
    #获取指定信息
    try:
        str = findHZ(contr,nodeName,code)
    except:
        print('getStr:error in finding node(%s) code(%s)' % (nodeName,code))
        return ""
    return r
def getInt(contr,nodeName,code):
    #获取指定信息
    try:
        str = int(findHZ(contr,nodeName,code))
    except:
        print('getInt:error in finding node(%s) code(%s)' % (nodeName,code))
        return ""
    return r
