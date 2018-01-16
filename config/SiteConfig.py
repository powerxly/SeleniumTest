#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-07-26 13:20
# config/SiteConfig.py

# 封装对页面和元素访问参数,及其获取方式（目前采用ini文件的读取）
# 
__default_encoding__="gbk"

import ConfigParser
import sys,os
import json
import copy

#__defaultSitePath__:缺省的站点配置目录
__defaultSitePath__='./config/sites'


def getFilesInDir(dir):
    path = os.listdir(dir)
    return path
def getIniFiles(siteConfigPath=__defaultSitePath__):
    #获取站点设置目录下所有的ini文件，文件名就是站点配置的关键字
    lists=[]
    listdir=getFilesInDir(siteConfigPath)
    for l in listdir:
        if l[-3:]=='ini':
            lists.append(l)
            #print(repr(l))
    return lists
def getPages(siteConfigPath=__defaultSitePath__):
    #站点设置文件的文件名，就是站点设置的关键字
    lists=[]
    listdir=getIniFiles(siteConfigPath)
    for l in listdir:
        lists.append(l[:-4])
    return lists
def getSitesConfig(siteConfigPath=__defaultSitePath__):
    #获取站点设置目录下的所有ini文件，将其内容读取为json配置数据，以站点关键字（文件名）为查询关键字
    #数组decodings里存放的是需要被解码成unicode的参数，例如xpath中的value，中文应该解码成unicode，否则查不到
    decodings=['xpath','partial link text','link text']
    #sites是返回的参数
    sites = {}
    names = getPages()
    cf = ConfigParser.ConfigParser()
    for l in names:
        sections={}
        #to delete  print(os.path.join(siteConfigPath,l+'.ini'))
        cf.read(os.path.join(siteConfigPath,l+'.ini'))
        secs=cf.sections()
        for s in secs:
            keyValues={}
            keys = cf.options(s)
            for k in keys:
                v = cf.get(s,k)
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
            sections[s.decode(__default_encoding__)]=keyValues
        sites[l.decode(__default_encoding__)]=sections
    return sites
def findHZ(dict,toSearch,code="default"):
    #如果汉字编码没有显示说明，那么缺省会依序尝试__default_encoding__和unicode这两种汉字编码，增强系统容错性。
    r="";
    #print(toSearch)
    #print(dict)
    if(code.lower()=="default"):
        try:
            r=dict[toSearch]
        except Exception,e:
            try:
                r=findHZ(dict,toSearch,code=__default_encoding__)
            except Exception,e:
                r=""
    else:
        r=dict[toSearch.decode(__default_encoding__)]
    return r
    
class SiteConfig():
    __siteConfigPath__=''
    __siteConfig__={}
    def __init__(self,path=__defaultSitePath__):
        self.__siteConfigPath__=path
        self.__siteConfig__ = getSitesConfig(path)
        pass
    def __str__(self):
        return json.dumps(self.__siteConfig__)
    def toJson(self):
        return(self.__siteConfig__)
    def getSite(self,site,code="default"):
        return(findHZ(self.__siteConfig__,site,code))
    def getUrls(self,site,code="default"):
        return(findHZ(self.getSite(site,code),"urls",code))
    def getUrl(self,site,page,code="default"):
        return(findHZ(self.getUrls(site,code),page,code))
    #获取用户信息[pwd,department]
    def getUsers(self,site,code="default"):
        return(findHZ(self.getSite(site,code),"users",code))
    def getUser(self,site,name,code="default"):
        return(findHZ(self.getUsers(site,code),name,code))

        
    def getElements(self,site,code="default"):
        return(findHZ(self.getSite(site,code),"elements",code))
    def getElement(self,site,name,code="default",context={}):
        print("trying getElement (site:%s,name:%s)" % (site.decode(__default_encoding__),name.decode(__default_encoding__)) )
        v = findHZ(self.getElements(site,code),name,code)
        #替换其中的伪变量,此处主要应该是元素的搜索设置，应该是一个2元素的数组
        #因为数组是引用，所以需要复制，以免修改到config中的原值
        v2 = copy.copy(v)
        if len(v2)==2:
            #print('path_translation1: %s' % v2[1])
            v2[1] = self.compute(v2[1],context)
            #print(context)
            #print('path_translation2: %s' % v2[1])
        return v2
        
    def getFlows(self,site,code="default"):
        return(findHZ(self.getSite(site,code),"flows",code))
    #获取流程配置的文件类型（目前支持ini和excel）
    def getFlowSettingType(self,site,code="default"):
        return(findHZ(self.getFlows(site,code),"settings",code))
    #计算设置中传入的伪变量,例如替换$idx$, context={'idx':1}
    def compute(self,value,context={}):
        if len(context)>0:
            #目前只有字符串才进行替换，其他类型以后再说
            if type(value)==str:
                try:
                    for k in context.keys():
                        findStr ='$'+k+'$'
                        newStr = '%s' % context[k]
                        value = value.replace(findStr,newStr)
                except:
                    raise Exception('error in calculate value(%s : %s)' % (value,context))
        return value
