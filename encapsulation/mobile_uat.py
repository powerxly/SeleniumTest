#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-08-15 13:20
# encapsulation/smartdotoa.py
import pdb
__default_encoding__="gbk"

# 用于测试慧点oa的封装部分维护在此
#from config.FlowConfig import *
from config.FlowConfigExt_mobile_uat import *
from log.log import Logger
from time import sleep

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC

import re

import win32api
import win32gui
import win32con


from encapsulation import UIHandle

'''
    查找元素的关键字，用于ini文件中的设置

    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"
'''

class SmartHandle(UIHandle):
    # 构造方法，用来接收selenium的driver对象
    @classmethod
    def __init__(self, driver):
        UIHandle.__init__(driver)
        self.driver = driver
        self.addressbook={}
        self.actionPanel=ActionPanel(self)
        self.menu=Menu(self)
    '''
    @classmethod
    def tableRowClick(cls, element,rowText, page="", siteName=""):
        success = False
        el = cls.element(page,element,siteName)
        lists=el.find_elements_by_tag_name('tr')
        for l in lists:
            #print(l.text)
            if(rowText.decode(__default_encoding__) in l.text):
                childLink = l.find_element_by_tag_name('a')
                #print('view link:%s' % childLink.get_attribute('outerHTML'))
                if (cls.driverType=='ie'):
                    ie_click(cls,childLink)
                    success=True
                else:
                    try:
                        childLink.click()
                        success=True
                    except:
                        raise Exception('some error occurrs while clicking elemnt(%s)' % element)
                break
        return success
    '''
    #处理表单字段额外参数,由于之前json包在转换中会遇到编码问题，因此手动处理，格式例如idx:1;wait:3
    @classmethod
    def extraParams(self,str):
        str=str.strip()
        if(str==""):
            return {}
        p={}
        arr = str.split(';')
        for i in arr:
            a = i.split(':')
            if(len(a)>1):
                p[a[0]]=a[1]
        return p
        
    #处理表单字段(输入为数组)
    @classmethod
    def fields(self,inputs,context={}):
        for f in inputs:
            #合并外部参数（来自测试流程，例如docTitle）和流程预置参数（来自文件）
            p = self.extraParams(f[3])
            c = dict(context,**p)
            
            self.field(f[0],f[1],f[2],context=c)

    #处理表单字段
    @classmethod
    def field(self,element,value,type='input',context={}):
        value = self.compute(value,context)
        type=type.lower()
        if(type=='input'):
            self.Input(element,value,context=context)
        elif (type == 'select'):
            self.select(element,value,context=context)
        elif (type == 'org'):
            self.selectOrg(element,value,context=context)
        elif (type == 'cjs_org'):
            self.selectCjsOrg(element,value,context=context)
        elif (type == 'fenfa_org'):
            self.selectFFOrg(element,value,context=context)
        elif (type == 'person'):
            self.selectPerson(element,value,context=context)
        elif (type == 'script'):
            self.executeScript(value,context=context)
        elif (type == 'raw_input'):
            self.executeInput(self.driver,element,value,context=context)
        elif (type == 'meeting_select'):
            self.selectMeetingPerson(element,value,context=context)
        elif (type == 'common_addressbook'):
            self.selectGenericAddressbook(element,value,context=context)
        elif (type == 'button'):
            self.Click(element,context=context)
        elif (type == 'wait'):
            sleep(1)
        
        #pdb.set_trace()
        try:
            #如果正确设置了等待参数，那么进行相应的延时
            t=int(context['wait'])
            sleep(t)
            print('字段（%s）填写后延时%i秒'.decode(__default_encoding__) % (element.decode(__default_encoding__),t))
        except:
            #否则默认延时0.1秒
            sleep(0.1)
            
        
    #添加慧点使用的地址簿对象,element是ini中的标识
    @classmethod
    def addAddressbook(self,element,type='org',context={}):
        key=element+"|"+self.currentPage+"|"+self.currentSite+"|"+type
        if(type.lower()=='person'):
            self.addressbook[key] = Personbook(self,element,self.currentPage,self.currentSite,context=context)
        elif(type.lower()=='cjs_org'):
            self.addressbook[key] = CjsOrgbook(self,element,self.currentPage,self.currentSite,context=context)
        elif(type.lower()=='fenfa_org'):
            self.addressbook[key] = FFOrgbook(self,element,self.currentPage,self.currentSite,context=context)
        elif(type.lower()=='meeting_select'):
            self.addressbook[key] = Meetingbook(self,element,self.currentPage,self.currentSite,context=context)
        elif(type.lower()=='common_addressbook'):
            self.addressbook[key] = GenericSingleAddressBook(self,element,self.currentPage,self.currentSite,keyName='待选',context=context,selectors={},buttons={'quit':'generic_addressbook_确定'},waits={})
        else:
            self.addressbook[key] = Orgbook(self,element,self.currentPage,self.currentSite,context=context)
        
        return self.addressbook[key]
    #查找已经定义的慧点使用的地址簿对象,element是ini中的标识
    @classmethod
    def getAddressbook(self,element):
        key=element+"|"+self.currentPage+"|"+self.currentSite
        return self.addressbook[key]

    #选择部门，格式例如'总部/办公厅'
    @classmethod    
    def selectOrg(self,element, orgLinks,context={}):
        book=self.addAddressbook(element,'org',context=context)
        book.open()
        #book.expandOrgBranch(orgLinks)
        #book.rightMove()
        book.clickOrgItems(orgLinks)
        book.close()
        #选择部门，格式例如'总部/办公厅'
    @classmethod    
    def selectCjsOrg(self,element, orgLinks,context={}):
        book=self.addAddressbook(element,'cjs_org',context=context)
        book.open()
        #book.expandOrgBranch(orgLinks)
        #book.rightMove()
        book.clickOrgItems(orgLinks)
        book.close()
    #选择分发部门，格式例如'总部'
    @classmethod    
    def selectFFOrg(self,element, orgLinks,context={}):
        book=self.addAddressbook(element,'fenfa_org',context=context)
        book.open()
        #book.expandOrgBranch(orgLinks)
        #book.rightMove()
        #book.clickOrgItems(orgLinks)
        book.clickMultiOrgItems(orgLinks)
        book.close()
    #选择会议参与人，格式例如'政企分公司/徐殿刚（政企）'
    @classmethod    
    def selectMeetingPerson(self,element, orgLinks,context={}):
        book=self.addAddressbook(element,'meeting_select',context=context)
        book.open()
        book.clickMultiOrgItems(orgLinks)
        book.close()
    #选择参与人或部门，lazytree格式的通用选择器，格式例如'政企分公司/徐殿刚（政企）'，通过参数配置以适应不同的模块
    @classmethod    
    def selectGenericAddressbook(self,element, orgLinks,context={}):
        book=self.addAddressbook(element,'common_addressbook',context=context)
        book.open()
        book.clickMultiOrgItems(orgLinks)
        book.close()
    @classmethod    
    def selectPerson(self,element, username,context={}):
        user = self.getUser(username)
        id = user[0]
        orgLinks = user[2]
        book=self.addAddressbook(element,'person',context=context)
        book.open()
        book.expandOrgBranch(orgLinks)
        book.clickPersonItem(username)
        book.rightMove()
        book.close()
    @classmethod    
    def assignee(self,personList):
        panel=self.actionPanel
        panel.setAssignee(personList)
    @classmethod    
    def setOpinion(self,opinion):
        panel=self.actionPanel
        panel.setOpinion(opinion)
    @classmethod    
    def selectTransition(self,transition):
        panel=self.actionPanel
        panel.selectTransition(transition)
    @classmethod    
    def submitOpinion(self):
        panel=self.actionPanel
        panel.submitOpinion()
    @classmethod    
    def clickMenu(self,menus):
        menu=self.menu
        menu.click(menus)
    @classmethod    
    def setArchive(self,option):
        panel=self.actionPanel
        panel.setArchive(option)

class Addressbook(object):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="",context={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.context = context
    #打开地址簿窗口
    def open(self):
        self.button.click()
        sleep(3)
        #self.frame = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['id','selIframe']))
        #self.handle.driver.switch_to_frame(self.frame)
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        quitButton=self.handle.Click("地址簿选择确定按钮",context=self.context)
        sleep(3)
    '''
    #将选中项右移到右边窗口
    @classmethod    
    def rightMove(self):
        self.handle.Click("地址簿选择右移按钮")
    ''' 
    #点击组织item项
    def clickOrgItem(self, orgName):
        if (orgName==''):
            return
        find_str=orgName.decode(__default_encoding__)
        #xpath="//li[contains(@id,'departmentTree')]/span[contains(@id,'_switch')]/following-sibling::*[1][@title='"+find_str+"']"
        selector='#ydxyDept>li[title="'+find_str+'"]'
        item = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
        item.click()
    def clickOrgItems(self, orgLinks):
        #先把多个部门分拆
        orgs=orgLinks.split(',')
        for o in range(0,len(orgs)):
            #然后分拆部门路径
            chains=orgs[o].split('/')
            for i in range(0,len(chains)):
                self.clickOrgItem(chains[i])
                sleep(0.5)

#组织树对象    
class Orgbook(Addressbook):
    pass
#分发组织树对象    
class FFOrgbook(Addressbook):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="", context={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.context = context
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        quitButton=self.handle.Click("地址簿选择确定按钮",context=self.context)
        sleep(2)
        #处理确认窗口
        try:
            #提示确认
            alt = self.handle.driver.switch_to_alert()
            print('alert prompt: %s' % alt.text)
            alt.accept()
            sleep(2)
            #确认发送成功
            alt = self.handle.driver.switch_to_alert()
            print('alert prompt: %s' % alt.text)
            alt.accept()
            
        except:
            pass
        sleep(2)
    #点击组织item项
    def clickOrgItem(self,oList, orgName):
        if (orgName==''):
            return
        oList.click(orgName)
    #在一个指定列表中添加多个部门选项，部门之间用逗号分隔
    def clickOrgItems(self, section ,orgLinks):
        #获取指定列表
        oList = Ulist(self.handle,section)
        #先把多个部门分拆
        orgs=orgLinks.split(',')
        for o in range(0,len(orgs)):
            #然后分拆部门路径
            chains=orgs[o].split('/')
            for i in range(0,len(chains)):
                self.clickOrgItem(oList,chains[i])
                sleep(0.5)
    def clickMultiOrgItems(self, nameList):
        #先判断和分拆可能的多分发组织树(multi开头识别)
        multiPrefix='multi|'
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.startswith(multiPrefix)):
            #标识样例：multi|省公司:北京,上海;境外:辛姆巴科公司;专业:终端公司;部门列表:综合部,技术部;直属:研究院;其他单位:香港
            multiList = nameList[len(multiPrefix):].split(';') #分号分隔不同的区段
            #多区段列表显示更慢，需要多等一会
            sleep(1)
            for c in multiList:
                arr = c.split(":")
                section = arr[0]
                names = arr[1]
                self.clickOrgItems(section,names)
        else:
            #todo容错以后处理
            #self.selectSingleTree(nameList)
            pass
#基本地址簿模型
class GenericSingleAddressBook(Addressbook):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="",keyName='待选',context={},selectors={},buttons={},waits={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.keyName = keyName
        self.context = context
        #相关css选择器设置
        #--相关选择器的默认值
        sel = {}
        sel['root']='table.maintable td.col-md-1'
        sel['title']='span'
        sel['cntr']='ul[id]'
        sel['items']='li[id]'
        #用传入的参数selectors覆盖默认值
        sel_inst = dict(sel,**selectors)
        self.selectors = sel_inst
        #--相关按钮的默认值
        btns = {}
        btns['quit']='会议纪要_选人确定'
        self.buttons = dict(btns,**buttons)
        #--等待时间的默认值
        ws = {}
        ws['quit_before'] = 0
        ws['quit_after']= 2
        self.waits = dict(ws,**waits)
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        self.wait(self.waits['quit_before'])
        
        element = self.buttons['quit']
        quitButton=self.handle.Click(element,context=self.context)
        
        self.wait(self.waits['quit_after'])
    #等待延时
    def wait(self,_time):
        try:
            t = float(_time)
            sleep(t)
        except:
            print('Waiting time setting(%s) error, ignored it' % _time)
    #点击组织item项
    def clickOrgItem(self, name,section='待选'):
        if (name==''):
            return
        oTree = LazyTree(self.handle,section, self.selectors)
        oTree.ready()
        oTree.expand(name)
        
    #在一个指定列表中添加多个部门选项，部门之间用逗号分隔
    def clickOrgItems(self, section ,orgLinks):
        #获取指定列表
        oTree = LazyTree(self.handle,section, self.selectors)
        #等待LazyTree加载完成
        oTree.ready()
        oTree.expandAll(orgLinks)
    def clickMultiOrgItems(self, nameList):
        #先判断和分拆可能的多分发组织树(multi开头识别)
        multiPrefix='multi|'
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.startswith(multiPrefix)):
            #标识样例：multi|省公司:北京,上海;境外:辛姆巴科公司;专业:终端公司;部门列表:综合部,技术部;直属:研究院;其他单位:香港
            multiList = nameList[len(multiPrefix):].split(';') #分号分隔不同的区段
            #多区段列表显示更慢，需要多等一会
            sleep(1)
            for c in multiList:
                arr = c.split(":")
                section = arr[0]
                names = arr[1]
                self.clickOrgItems(section,names)
        else:
            #单分类，默认都使用“待选”作为类别关键字
            if (':' in nameList):
                arr = c.split(":")
                section = arr[0]
                names = arr[1]
                self.clickOrgItems(section,names)
            else:
                #使用默认分类
                self.clickOrgItems(self.keyName,nameList)
            

#会议相关人组织树对象    
class Meetingbook(GenericSingleAddressBook):
    # 构造方法，用来接收selenium调用所需的对象
    def __init__(self, handle, element, page="", siteName="",keyName='待选',context={},selectors={},buttons={},waits={}):
        self.handle = handle
        self.button = handle.element(page,element,siteName,context=context)
        self.page = page
        self.siteName = siteName
        self.keyName = keyName
        self.context = context
        #相关css选择器设置
        #--默认值
        sel = {}
        sel['root']='table.maintable td.col-md-1'
        sel['title']='span'
        sel['cntr']='ul[id]'
        sel['items']='li[id]'
        
        #用传入的参数selectors覆盖默认值
        sel_inst = dict(sel,**selectors)
        self.selectors = sel_inst
        
        #--相关按钮的默认值
        btns = {}
        btns['quit']='会议纪要_选人确定'
        self.buttons = dict(btns,**buttons)
        #--等待时间的默认值
        ws = {}
        ws['quit_before'] = 0
        ws['quit_after']= 2
        self.waits = dict(ws,**waits)
            
 
#会签组织树对象    
class CjsOrgbook(Addressbook):
    #点击组织item项
    def clickOrgItem(self, orgName):
        if (orgName==''):
            return
        find_str=orgName.decode(__default_encoding__)
        print("CjsOrgbook-click orgname:%s" % find_str)
        selector='#huiQianChuShi>li[title="'+find_str+'"]'
        #print(selector)
        item = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
        item.click()
class Personbook(Orgbook):
    #点击组织item项
    @classmethod    
    def clickPersonItem(self, name):
        find_str=name.decode(__default_encoding__)
        xpath="//ul[@id='waitSelect']/li[@name='"+find_str+"']"
        item = WebDriverWait(self.handle.driver, 15).until(EC.presence_of_element_located(['xpath',xpath]))
        item.click()
        sleep(3)
    
class ActionPanel():
    # 构造方法，用来接收selenium调用所需的对象
    @classmethod
    def __init__(self, handle):
        self.handle = handle
        self.checklist={}
        self.initialized = False
    # 填写归档选项
    @classmethod
    def setArchive(self,option):
        #试图设置归档选项
        options=['永久','长期','短期','临时']
        if (option=="" or not option in options):  #为空，或非法数值，则不处理
            return
            
        #归档类型选择
        els = self.handle.elements("","归档选项")
        label=option.decode(__default_encoding__)
        for l in els:
            #print('label:%s vs %s' % (label,l.text))
            if(label in l.text):
                el=l.find_element_by_tag_name('input')
                el.click()
        sleep(0.5)
    # 填写意见
    @classmethod
    def setOpinion(self,opinion):
        options=['同意。','不同意。','其它']
        if (opinion==""):  #为空，则不处理
            return
        seperators='|'  #支持的分隔符
        list = re.split('['+seperators+']',opinion)
        
        if(list[0] in options):
            radio = list[0]
            if(len(list)>1):
                opinion = list[1]
            else:
                opinion = ""
        else:
            #没有参数，说明不是决策性意见
            radio = ''
            opinion = list[-1]
            
        #意见输入
        
        if(opinion!=''):
            self.handle.Input("意见框",opinion)
        #意见类型选择
        if radio!='':
            els = self.handle.elements("","意见选项")
            #决策意见，需要进行选择
            for l in els:
                label=radio.decode(__default_encoding__)
                
                if(label == l.text):
                    el=l.find_element_by_tag_name('input')
                    el.click()
        sleep(0.5)

    # 公文意见和分支区域的提交
    @classmethod
    def submitOpinion(self):
        label = '提交'.decode(__default_encoding__)
        region=self.handle.driver.find_element_by_css_selector('#grcspSubmitWindow')
        els = region.find_elements_by_css_selector('div.modal-footer>button')
        for l in els:
            if(label in l.text):
                l.click()

        sleep(1)
        
    # 设置（修改）处理人，样例（'范宁,宋金超'）
    @classmethod
    def setAssignee(self,nameList):
        #统一添加延时，避免加载缓慢引起ztree.getTreeRootId方法报错
        sleep(1)
        multiPrefix='multi|'
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.startswith(multiPrefix)):
            #标识是4会签框格式类似'主办:张三,李四;协办:王五'，会自动在“主办”中选择张三和李四，“协办”选择王五
            cjsList = nameList[len(multiPrefix):].split(';') #分号分隔不同的会签区段
            #多会签显示更慢，需要多等一会
            sleep(1)
            for c in cjsList:
               self.selectSingleTree(c)
        else:
            self.selectSingleTree(nameList)
        sleep(2)
    # 设置处理人，样例（'部门1/范宁,部门2/宋金超'）
    @classmethod
    def selectSingleTree(self,nameList):
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        if(nameList.find(':')>=0):
            #页面上存在多个ztree选择器，需要分别选择，格式类似'主办:部门1/张三,部门2李四'，会自动在“主办”中选择张三和李四
            r = nameList.split(':')
            region = r[0]
            nList = r[1]
        else:
            #页面上只存在一个ztree选择器，就不区分了，简化接口
            region = ""
            nList = nameList
        
            
        ztree = Ztree(self.handle,region)
        ztree.expandAll(nList)
    '''        
    # 设置（会签）处理人，样例（'范宁,宋金超'）
    @classmethod
    def setCjsAssignee(self,nameList):
        if (nameList=="" or nameList.lower()=='default'):  #为空或缺省值，则不处理
            return
        seperators=',;'  #支持的分隔符
        list = re.split('['+seperators+']',nameList)

        #依次选择，由于使用的是ztree变形，人员和部门都在左边，只不过人员是叶子节点，所以使用混合路径展开
        
        for n in list:
            root = self.getZtreeRoot(n)
            self.expandZtrees(root,n)
            #留出页面节点展开的时间
            sleep(1)
        sleep(2)
    '''
    '''
    #点击叶子节点的a链接
    @classmethod    
    def clickLeaf(self, leaf):
        find_str=leaf.decode(__default_encoding__)
        # 用于ztree-like的叶子节点触发（A链接）
        if(self.cjs):
            id = 'grcsp_left_cjs_deps'
        else:
            id = 'grcsp_left_'
        selector = "li[id^='"+id+"']>a[title='"+find_str+"']"
        #print('selector:%s' % selector)
        link = None
        try:
            #在本选择器中，link可能已经被点击，挪到了右侧区域，所以要处理一下
            link = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
            #print('ok')
        except:
            pass
        #print('link type:%s' % type(link))
        if(link!=None):
            link.click()
    '''
    '''
    #展开父部门分支
    @classmethod    
    def toggleBranch(self, branch, action='toggle'):
        success=True
        print('try to expand branch:%s ' % branch)
        find_str=branch.decode(__default_encoding__)
        # 用于ztree-like的干节点展开
        id = 'grcsp_left_cjs_deps'
        xpath="//li[contains(@id,'"+id+"')]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        #print(xpath)
        switch = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['xpath',xpath]))
        el_class = switch.get_attribute('class')
        #print(el_class)
        if (action=='open'):
            #打开操作，只展开
            if ('_close' in el_class):
                self.expandAndScroll(switch)
            else:
                success=False
        elif(action=='close'):
            #关闭操作，只关闭
            if (not '_close ' in el_class):
                self.expandAndScroll(switch)
            else:
                success=False
        else:
            #否则，切换状态
            self.expandAndScroll(switch)
        return success
   
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    @classmethod    
    def expandAndScroll(self, switch):
        scrollby = 180 #默认滚动高度
        self.jScroll(0)
        iniClass = switch.get_attribute('class')
        switch.click()
        i=0
        scrollTop=0
        while(switch.get_attribute('class')==iniClass and i<5):
            #click以后，class没有变化，说明元素不在显示区域，需要滚动对应的div后重新尝试
            scrollTop=scrollTop+scrollby
            self.jScroll(scrollTop)
            sleep(1)
            switch.click()
            i=i+1
        print('scroll time:%i' % i)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    @classmethod    
    def jScroll(self, top):
        jscode="$('div.left>div.autoOverflow').scrollTop(%s)" % top
        self.handle.driver.execute_script(jscode)
        
    #从头展开某个部门路径，格式例如'总部/办公厅'，前面的会展开分支，最后一个是点击部门，用于显示部门内容
    @classmethod    
    def expandZtree(self, treeLinks):
        chains=treeLinks.split('/')
        for i in range(0,len(chains)):
            if (i==len(chains)-1):
                #链条的最后一个是点击叶子节点，用于显示部门内容
                print('leaf:%s' % chains[i])
                self.clickLeaf(chains[i])
            else:
                #链条的前面几个会展开分支
                print('branch:%s' % chains[i])
                success = self.toggleBranch(chains[i],'open')
                if (not success):
                    break
            sleep(3)
    '''    
    # 选择流程分支（文本匹配）
    @classmethod
    def selectTransition(self,transitionText):
        if (transitionText=="" or transitionText.lower()=='default'):  #为空或缺省值，则不处理
            return
        
        trans = transitionText.decode(__default_encoding__)
        els = self.handle.elements('','流程分支选择')
        found = False
        for l in els:
            if(trans in l.text):
                c = l.get_attribute('class')
                if (not 'active' in c ):
                    l.click()
                found = True
                break
        #如果找不到，说明流程有变动
        if (not found):
            raise Exception('指定分支（%s）不存在，请检查' % transitionText)
        else:
            sleep(1)
    # 检查页面特定标识，判断当前环节类型，并在对象中设置该标识，以便以合适的方式继续流程
    @classmethod
    def initlize(self,nameList):
        pass

class View():
    # 构造方法，用来接收selenium调用所需的对象
    
    def __init__(self, handle, viewName="",checkSelector="table[id='todo']"):
        self.handle = handle
        self.viewname = viewName
        self.tabs,self.activeTabIndex = self.__getTabs__()
        self.checkSelector = checkSelector
        
    #触发视图是否ready的检查，使用初始化时传入的参数readyFunc
    
    #检查视图是否加载完成
    def ready(self,delay=5,count=20):
        driver = self.handle.driver
        ready = False
        count = 30
        delay = 2
        
        while not ready and count>0:
            count=count-1
            try:
                tbl = driver.find_element_by_css_selector(self.checkSelector)
            except:
                sleep(delay)
                continue
            #todo容器没问题了，但还要检查视图内容是否出现
            try:
                trs = tbl.find_elements_by_tag_name('tr')
            except:
                sleep(delay)
                continue
            if (len(trs)>0):
                #有内容了，退出等待循环，设置成功标志
                ready=True
        return ready
        
    #触发视图操作（为方便，输入操作的部分文本即可，有多个匹配，触发第一个）,可用于翻页等视图操作
    def clickAction(self, label):
        actions = []
        els = self.handle.elements('', '待办视图操作','')
        i=0
        label=label.decode(__default_encoding__)
        found = False
        for l in els:
            if(label in l.text):
                c = l.get_attribute('class')
                if (not 'disabled' in c ):
                    btn = l.find_element_by_tag_name('a').click()
                    sleep(1)
                    found = True
                else:
                    print('the action(%s) had already been disbled, so ignore it' % label.decode(__default_encoding__))
            i=i+1
        if not found:
            print('the action(%s) does no exist, so ignore it' % label.decode(__default_encoding__))
        return found
    #从页面获取所有视图页签名称，返回数组
    
    def __getTabs__(self):
        #获取当前视图页面中的页签，返回对象列表
        tabs = []
        els = self.handle.elements('', '公文页签','')
        i=0
        active=-1
        for l in els:
            label = l.text
            if (label!=''):
                c = l.get_attribute('class')
                if (active==-1 and 'active' in c ):
                    active=i
                tabs.append(label)
                i=i+1
        return tabs,active
    #从对象获取所有视图页签名称，返回数组
    
    def switchToViewTab(self,tabName):
        name=tabName.decode(__default_encoding__)
        els = self.handle.elements('', '公文页签','')
        i=0
        for l in els:
            label = l.text
            c = l.get_attribute('class')
            if (name in label and not 'active' in c ):
                self.activeTabIndex=i
                l.click()
                break
            i=i+1
        sleep(5)
    
    def isTabActivated(self,tabName):
        name=tabName.decode(__default_encoding__)
        tabs=self.tabs
        flag=False
        i=0
        for l in tabs:
            if(name in l and i==self.activeTabIndex):
                flag=True
                break
        return flag
    #判断文档是否在视图中显示（通过文本匹配）
    
    def isDocInView(self,docTitle,max_try=10):
        for i in range(0,max_try-1):
            rowNum = self.handle.findRowInTable('公文视图',docTitle)
            found = (rowNum>-1)
            if (found):
                return True
            else:
                #尝试翻页以后再检查
                self.clickAction('下一页')
        #没有找到，返回False
        return False
    
    def clickDocInView(self,docTitle,max_try=10):
        print(('扩展：在视图（%s）中打开文档(%s)' % (self.viewname,docTitle)).decode(__default_encoding__))

        for i in range(0,max_try-1):
            try:
                print(i)
                success = self.handle.tableRowClick(self.viewname,docTitle)
            except:
                #found but failure in clicking the element
                raise Exception('some error occurrs while clicking document(%s) in View(%s)' % (docTitle,self.viewname))

            if (success):
                sleep(5)
                return True
            else:
                #尝试翻页以后再检查
                next_found = self.clickAction('下一页')
                sleep(3)
                if (not next_found or i==max_try-1):
                    #下一页按钮没找到，或禁用了，则终止翻页处理
                    print('The doc(%s) is not found in view(%s) after (%i) tries' % (docTitle.decode(__default_encoding__),self.viewname.decode(__default_encoding__),i+1))
                    break
        sleep(1)
        return False
        
    def check(self):
        pass
def toUnicode(str):
    try:
        return str.decode(__default_encoding__)
    except:
        return str
        
class Menu():
    # 构造方法，用来接收selenium调用所需的对象
    @classmethod
    def __init__(self, handle):
        self.handle = handle
    #点击菜单项
    @classmethod    
    def click(self, menus):
        if (menus==""):  #为空，则不处理
            return
        chains=menus.split('/')
        menu1=None
        print(menus.decode(__default_encoding__))
        #根菜单
        els = self.handle.elements("","公文管理根菜单","")
        for l in els:
            #print(l.text)
            if(toUnicode(chains[0]) in l.text):
                actions = AC(self.handle.driver)
                actions.move_to_element(l)
                actions.perform()
                menu1=l
                break
        sleep(1)
        #二级菜单
        if (self.handle.driverType=='ie'):
            #在ie下出现在上级菜单元素下find_element_by_link_text(chains[1].decode('gbk'))找不到元素（ Unable to find element with link text）但firefox下正常，直接在driver下查也正常，怀疑是ie driver的bug，因此先用本函数绕过，以后有时间再查原因吧
            sub=ie_find_element_by_link_text(menu1,chains[1])
            link = sub.get_attribute('href')
            #print('link:%s' % link)
            self.handle.driver.execute_script('window.open("'+link+'")')
        else:
            sub=menu1.find_element_by_link_text(toUnicode(chains[1]))
            if(sub!=None):
                sub.click()
        sleep(3)
#在ie下出现在上级菜单元素下find_element_by_link_text(chains[1].decode('gbk'))找不到元素（ Unable to find element with link text）但firefox下正常，直接在driver下查也正常，怀疑是ie driver的bug，因此用本函数绕过
def ie_find_element_by_link_text(parent,text):
    els=parent.find_elements_by_tag_name('a')
    label = text.decode(__default_encoding__)
    for l in els:
        if(label in l.get_attribute('innerText')):
            print('found element:%s' % l.get_attribute('innerText'))
            return l
    return None
#在视图等场景下，firefox正常，但是ie下，a link可以点击执行，界面上也出现数据加载中提示，但相应的文档窗口没有打开
def ie_click(handle,node):
    #print(node.get_attribute('outerHTML'))
    link = node.get_attribute('href')
    jscript = node.get_attribute('onclick')
    target = node.get_attribute('targrt')
    if(jscript!=''):
        #print('1')
        #处理转义字符，不然移动的sso会出现问题
        jscript = jscript.replace('&amp;','&')
        #print('jscript:%s' % jscript)
        handle.driver.execute_script(jscript)
    elif (link!=''):
        #print('2')
        if(target.lower()=='_blank'):
            #处理转义字符，不然移动的sso会出现问题
            href = href.replace('&amp;','&')
            #print('href:%s' % href)
            href = href.replace('&amp;','&')
            handle.driver.execute_script('window.open("'+href+'")')
        else:
            node.click()
    else:
        print('ie_click cannot handle the link: %s' % node.get_attribute('outerHTML'))
#流程对象
class Workflow():
    # 构造方法
    @classmethod
    def __init__(self, handle, flowName, docTitle='', sourceType='ini'):
        self.handle = handle
        self.config = SmartFlow(flowName,sourceType)
        self.flowName = flowName
        self.title = self.config.getFlowTitle(flowName)
        self.runPaths = self.config.getRunPaths(flowName)
        self.docTitle = docTitle  #保存当前标题，流程中唯一
    def setDocTitle(self,docTitle):
        self.docTitle = docTitle
    # 获取表单填写项
    @classmethod
    def getForm(self,formName):
        return Form(self,formName)

    def getPath(self,name):
        return self.config.getPath(self.flowName,name)
    # 获取节点
    @classmethod
    def getNode(self,nodeName):
        node = WorkflowNode(self,nodeName)
        return node
        
#流程节点对象
class WorkflowNode():
    # 构造方法
    
    def __init__(self, wf, nodeName, docTitle=''):
        self.workflow = wf
        self.config = wf.config.getNode(wf.flowName,nodeName)
        #print(self.config)
        if(docTitle==''):
            docTitle = wf.docTitle
        self.docTitle = docTitle  #保存当前标题，流程中唯一
        
        if (self.config.has_key('type')):
            self.type = self.config['type']
        else:
            self.type = ''
        
    def setDocTitle(self,docTitle):
        self.docTitle = docTitle
        self.workflow.setDocTitle(docTitle)
    # 获取节点信息
    def get(self,prop,default=''):
        if (self.config.has_key(prop)):
            return self.config[prop]
        else:
            return default
        
    # 获取节点所使用的表单信息
    def getType(self):
        nodeType = self.get('type')
        return nodeType
    # 获取节点所使用的actions
    def getActions(self):
        actions = self.get('actions')
        if actions=='':
            #对应参数不存在
            actions=[]
        else:
            actions=actions.split(',')
        return actions
    def getForms(self):
        forms =[]
        fnames = self.get('forms')
        if (fnames!=''):
            seperators=',;'  #支持的分隔符
            list = re.split('['+seperators+']',fnames)
            for l in list:
                form = self.workflow.getForm(l)
                if form.exists():
                    forms.append(form)
        return forms
    # 根据节点所使用的表单信息，自动填写页面表单
    
    def autoFillForm(self,context={}):
        forms = self.getForms()
        for f in forms:
            fname = f.name
            self.workflow.handle.logger.debug('====填写表单(%s)=====' % fname)
            prefix = 'dynamicxxxx|'
            if fname.startswith(prefix):
                fname = fname[len(prefix):]
                #动态表格
                self.workflow.handle.logger.debug('====动态表格(%s)=====' % fname)
                dnt = DynamicTable(self.workflow.handle, fname, rootSelector='.dynamicTable',addButton='动态表格添加按钮')
                dnt.add()
                dnt.fields(f.formInputs(),context)
            else:
                #print(f.formInputs())
                self.workflow.handle.fields(f.formInputs(),context)
            sleep(1)
    
    def __str__(self):
        keys=self.config.keys()
        r=''
        for k in keys:
            r = r+'%s:%s, ' %(k,self.config[k])
        return "Flow Node:{%s}" % r
        
#流程节点对象
class Form():
    # 构造方法
    
    def __init__(self, wf, formName):
        self.workflow = wf
        self.config = wf.config.getForm(wf.flowName,formName)
        if len(self.config)==0:
            raise Exception('Error in getting the setting of form(%s)' % formName)
        self.name = formName
    # 获取表单信息
    
    def formInputs(self):
        return self.config
    
    def exists(self):
        return len(self.config)>0
    
    def __str__(self):
        r=''
        for i in self.config:
            r = r+'['
            r = r+ ','.join(i)
            r = r+']\n'
        return ("Form:\n[\n%s]" % r)
#ul列表对象
class Ulist():
    #构造方法
    def __init__(self, uihandle, listName):
        self.handle = uihandle
        self.trees ={}
        id = self.getRootId(listName)
        self.id = id
    #获取ul list的标识根节点，作为查找子元素的根起点
    def getRootId(self,listName):
        uihandle = self.handle
        find_str=listName.decode(__default_encoding__)
        root = None
        id = ''
        
        print('listName:%s' % listName.decode(__default_encoding__))
        #先找外层td
        selector = '#GEditModal .maintable .col-md-1'
        WebDriverWait(uihandle.driver, 20)
        searchPath = ["css selector",selector]
        els = uihandle.driver.find_elements(*searchPath)
        
        #再找内层的列表，检查标题，看哪个列表是所需列表
        for el in els:
            id = self.getInnerId(el,find_str)
            if id!='':
                #成功获得第一个满足条件的列表的id，则结束递归
                break;
        return id
    #需要支持列表的嵌套，处理列表的递归查询
    def getInnerId(self,topElement,find_str):
        id = '' #返回值
        selector_title = 'span'
        selector_container = 'table tr'
        oCntrs = topElement.find_elements_by_css_selector(selector_container)
        if(len(oCntrs)==0):
            #不存在子容器，直接处理
            oTitle = topElement.find_element_by_css_selector(selector_title)
            #print('inner title:%s' % oTitle.text)
            if(find_str=="" or find_str in oTitle.text):
                print('found:%s' % oTitle.text)
                #支持局部匹配
                root = topElement.find_element_by_css_selector('ul[id]')
                id = root.get_attribute('id')
        else:
            #存在子容器，递归处理
            for el in oCntrs:
                id = self.getInnerId(el,find_str)
                #print('getInnerId:%s' % id)
                if id!='':
                    #成功获得对应列表的id，则结束递归
                    break
        return id    
        
    #点击列表的指定名称的节点，支持局部匹配，找到第一个为止
    def click(self,text):
        uihandle = self.handle
        find_str=text.decode(__default_encoding__)

        #找到对应的容器ul
        WebDriverWait(uihandle.driver, 20)
        root = uihandle.driver.find_element_by_id(self.id)
        
        els = root.find_elements_by_css_selector('li[title]')
        for el in els:
            label = el.text
            if(find_str=="" or find_str in label):
                print('found:%s' % label)
                el.click()
                #找到第一个，就退出循环
                break;
'''
    def clickNode(self,el):
        link = None
        try:
            #在本选择器中，link可能已经被点击，挪到了右侧区域，所以要处理一下
            #link = self.root.find_element_by_css_selector(selector)
            link = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
            #print('ok')
        except:
            pass
        #print('link type:%s' % type(link))
        
        if(link!=None):
            #self.clickAndScroll(link)
            link.click()
'''    
#ztree对象
class Ztree():
    # 构造方法
    
    def __init__(self, uihandle, treeName):
        self.handle = uihandle
        self.trees ={}
        id,flag_id = self.getTreeRootId(treeName)
        self.id = id
        if ('cjs' in self.id):
            self.cjs = True
        else:
            self.cjs = False
        
    #获取ztree的标识根节点，作为查找子元素的根起点
    def getTreeRootId(self,treeName):
        uihandle = self.handle
        find_str=treeName.decode(__default_encoding__)
        root = None
        id = ''
        
        max_try = 120
        attemps=max_try
        #uihandle.logger.info('try to find the tree of name:%s' % treeName)
        selector = '#grcsp_select_item_trees div[id^=selectItems_]'
        WebDriverWait(uihandle.driver, 20)
        searchPath = ["css selector",selector]
        
        found = False
        while not found and attemps>0:
            els = uihandle.driver.find_elements(*searchPath)
            found = (len(els)>0)
            attemps = attemps -1
            sleep(1)
        
        if not found:
            raise Exception('can not find the tree("%s--%s") in %i times tries, so stop the testing now!' % (treeName,selector,max_try))
        
        #els = uihandle.driver.find_elements_by_css_selector(selector)
        uihandle.logger.debug('found tree roots, %i matches' % len(els))
        selector_title = '.listTitle'
        for el in els:
            oTitle = el.find_element_by_css_selector(selector_title)
            if(find_str=="" or find_str in oTitle.text):
                print('found the ztree title: %s' % oTitle.text)
                #支持局部匹配
                root = el
                id = el.get_attribute('id')
                flag_el = root.find_element_by_css_selector('li[id^=grcsp_left]')
                flag_id = flag_el.get_attribute('id')
                #找到第一个，就退出循环
                break;
        return id,flag_id
    #点击叶子节点的a链接
    def clickLeaf(self, leaf):
        find_str=leaf.decode(__default_encoding__)
        # 用于ztree-like的叶子节点触发（A链接）
        if(self.cjs):
            id = 'grcsp_left_cjs_deps'
        else:
            id = 'grcsp_left_'
        selector ="#" +self.id+ " li[id^='"+id+"']>a[title='"+find_str+"']"
        #print('selector:%s' % selector)
        link = None
        try:
            #在本选择器中，link可能已经被点击，挪到了右侧区域，所以要处理一下
            #link = self.root.find_element_by_css_selector(selector)
            link = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
            #print('ok')
        except:
            pass
        #print('link type:%s' % type(link))
        if(link!=None):
            self.clickAndScroll(link)
            #link.click()
    #展开父部门分支
    def toggleBranch(self, branch, action='toggle'):
        success=True
        #print('try to expand branch:%s ' % branch)
        find_str=branch.decode(__default_encoding__)
        # 用于ztree-like的干节点展开
        #id = 'grcsp_left_cjs_deps'
        id = 'grcsp_'    #党办文件文书环节，阅知被改成了grcsp_right_notify_sid,所以为了兼容性，改为这样
        xpath="//div[@id='"+self.id+"']//li[contains(@id,'"+id+"')]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        #xpath="//li[contains(@id,'"+id+"')]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        #print(xpath)
        #switch = self.root.find_element_by_xpath(xpath)
        switch = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['xpath',xpath]))
        el_class = switch.get_attribute('class')
        #print(el_class)
        if (action=='open'):
            #打开操作，只展开
            if ('_close' in el_class):
                self.expandAndScroll(switch)
            else:
                success=False
        elif(action=='close'):
            #关闭操作，只关闭
            if (not '_close ' in el_class):
                self.expandAndScroll(switch)
            else:
                success=False
        else:
            #否则，切换状态
            self.expandAndScroll(switch)
        return success
   
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def clickAndScroll(self, el):
        #展开部门时，由于人员可能会在显示区域以外，此时，click不会报错，对应的js不会执行（或有效执行），因此，此处通过对点击效果的检查（例如左侧隐藏，右侧显示），来判断是否已经“有效”点击，如果没有，则卷滚后继续点击，直到成功为止
        scrollby = 80 #默认滚动高度
        self.jScroll(0)
        iniStatus = el.is_displayed()
        #print('ini:%s' % iniStatus)
        if (el.is_displayed()):
            el.click()
        else:
            #元素隐藏了，说明已经被选中到右边,目前就这样了，不再继续处理
            pass
        sleep(1)
        #下面先注掉，遇到问题再针对性处理
        '''
        i=0
        scrollTop=0
        scrollLeft=0
        while(el.is_displayed()==iniStatus and i<5):
            #click以后，class没有变化，说明元素不在显示区域，需要滚动对应的div后重新尝试
            #print('no%i:%s' % (i,el.is_displayed()))
            scrollTop=scrollTop+scrollby
            self.jScroll(scrollTop)
            el.click()
            sleep(1)
            i=i+1
        #print('scroll time:%i' % i)
        '''
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def expandAndScroll(self, switch):
        scrollby = 80 #默认滚动高度
        self.jScroll(0)
        iniStatus = switch.get_attribute('class')
        switch.click()
        i=0
        scrollTop=0
        scrollLeft=0
        while(switch.get_attribute('class')==iniStatus and i<5):
            #click以后，class没有变化，说明元素不在显示区域，需要滚动对应的div后重新尝试
            scrollTop=scrollTop+scrollby
            self.jScroll(scrollTop,0)
            sleep(1)
            switch.click()
            i=i+1
        #print('scroll times:%i' % i)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def jScroll(self, top=0, left=0):
        jscode="t=$('div#"+self.id+" div.left>div.autoOverflow');t.scrollTop(%i);t.scrollLeft(%i);" % (top,left)
        self.handle.driver.execute_script(jscode)
    #从头展开某个部门路径，格式例如'总部/办公厅'，前面的会展开分支，最后一个是点击部门，用于显示部门内容
    def expand(self, treeLinks):
        chains=treeLinks.split('/')
        for i in range(0,len(chains)):
            if (i==len(chains)-1):
                #链条的最后一个是点击叶子节点，用于显示部门内容
                print('leaf:%s clicked' % chains[i].decode(__default_encoding__))
                self.clickLeaf(chains[i])
            else:
                #链条的前面几个会展开分支
                print('branch:%s expanded' % chains[i].decode(__default_encoding__))
                success = self.toggleBranch(chains[i],'open')
                #党办通知中第9环节文书岗处理中，阅知项：政企分公司下有上千人，展开耗时
                sleep(2)
                #if (not success):
                    #break
            sleep(1)
    def expandAll(self, paths):
        #在当前tree上同时展开多个路径
        seperators=','  #支持的分隔符
        list = re.split('['+seperators+']',paths)
        
        #依次选择，由于使用的是ztree变形，人员和部门都在左边，只不过人员是叶子节点，所以使用混合路径展开
        
        for n in list:
            self.expand(n)
            #留出页面节点展开的时间
            sleep(1)
#动态表格对象
class DynamicTable():
    #构造方法
    def __init__(self, uihandle, name, rootSelector='.dynamicTable',addButton='动态表格添加按钮'):
        self.handle = uihandle
        self.root = rootSelector
        self.name = name
        self.addButton = addButton
    #打开地址簿窗口
    def add(self):
        btn = self.handle.element('',addButton)
        btn.click()
        sleep(3)
        #self.frame = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['id','selIframe']))
        #self.handle.driver.switch_to_frame(self.frame)
    #关闭地址簿窗口
    def close(self):
        #self.handle.driver.switch_to_default_content()
        quitButton=self.handle.Click("地址簿选择确定按钮")
        sleep(3)
    #处理动态表格的字段填写
    def fields(self,inputs,context={}):
        for f in inputs:
            self.field(f[0],f[1],f[2],context)
#ztree对象
class LazyTree():
    # 构造方法
    
    def __init__(self, uihandle,treeName, selectors={}, wait=0):
        #selectors{'root','title','cntr','items'}分别是地址树的根节点，标题节点,容器节点，选项节点的css选择器
        #wait，可选参数是为了处理由于候选人太多不能按时加载，增加的延时参数（单位秒），会在根节点找到后，继续延时指定时间，保证地址树能够加载显示完毕。
        self.handle = uihandle
        self.selectors =selectors
        root_id,cntr_id = self.getTreeRootId(treeName)
        self.root_id = root_id
        self.cntr_id = cntr_id
        if(cntr_id==''):
            #容器节点没有id属性，则用根节点来代替（前缀是root|）。
            self.id = root_id
        else:
            self.id = cntr_id
        
        self.type = "simple"
        self.wait = wait
        
    #处理懒加载，高延时的大数据量地址树的展开
    #参数：wait-每次等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def __findElements_by_xpath(self,cntr,sub_selector,wait=1,max_try=120,min_required=1,wait_for_complete=2):
        return self.__findElements(cntr,'xpath',sub_selector,wait,max_try,min_required,wait_for_complete)
    #参数：wait-每次等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def __findElements_by_css_selector(self,cntr,sub_selector,wait=1,max_try=120,min_required=1,wait_for_complete=2):
        return self.__findElements(cntr,'css selector',sub_selector,wait,max_try,min_required,wait_for_complete)
    
    #参数：wait-每次等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def __findElements(self,cntr,selector_type,sub_selector,wait=1,max_try=120,min_required=1,wait_for_complete=2):
        uihandle = self.handle
        
        attemps=max_try
        #通过尝试获取子元素来判断懒加载是否完成
        searchPath = [selector_type,sub_selector]
        
        found = False
        while not found and attemps>0:
            els = cntr.find_elements(*searchPath)
            found = (len(els)>=min_required)
            attemps = attemps -1
            sleep(wait)
        
        if not found:
            #延时后仍未找到指定根节点，抛异常退出
            raise Exception('can not find the tree("%s--%s") in %i times tries, so stop the testing now!' % (treeName,selector,max_try))
        else:
            #为保险起见，额外等待时间
            sleep(wait_for_complete)
        return els
        
    #获取地址树结构的标识根节点，作为查找子元素的根起点
    def getTreeRootId(self,treeName):
        uihandle = self.handle
        find_str=treeName.decode(__default_encoding__)
        root = None
        id = ''
        
        #查找根节点，并进行适当等待，直到根节点找到为止
        selector_root = self.selectors['root']
        els = self.__findElements_by_css_selector(uihandle.driver,selector_root)
        '''
        max_try = 120
        attemps=max_try
        #uihandle.logger.info('try to find the tree of name:%s' % treeName)
        WebDriverWait(uihandle.driver, 20)
        searchPath = ["css selector",selector_root]
        
        found = False
        while not found and attemps>0:
            els = uihandle.driver.find_elements(*searchPath)
            found = (len(els)>0)
            attemps = attemps -1
            sleep(1)
        
        #延时后仍未找到指定根节点，抛异常退出
        if not found:
            raise Exception('can not find the tree("%s--%s") in %i times tries, so stop the testing now!' % (treeName,selector,max_try))
        '''
        
        #可能存在多个满足条件的根节点，那么根据标题筛选出需要的那个
        uihandle.logger.debug('found tree roots, %i matches' % len(els))
        selector_title = self.selectors['title']
        selector_cntr = self.selectors['cntr']
        i=0
        root_id=""
        cntr_id=""
        for el in els:
            #标题节点
            oTitle = el.find_element_by_css_selector(selector_title)
            if(find_str=="" or find_str in oTitle.text):
                print('found the ztree title: %s' % oTitle.text)
                #支持局部匹配
                root = el
                root_id = el.get_attribute('id')
                
                cntr = root.find_element_by_css_selector(selector_cntr)
                cntr_id = cntr.get_attribute('id')
                
                #找到第一个，就退出循环
                break;
            i = i+1
        if root_id=="" and cntr_id=="":
            raise Exception('cannot get the id of addresstree, please contact you testing supportor')
        return root_id,cntr_id
    #点击叶子节点的a链接
    def clickLeaf(self, leaf):
        find_str=leaf.decode(__default_encoding__)
        # 用于ztree-like的叶子节点触发（A链接）
        selector ="#" +self.id+ " li[id^='"+self.id+"']>a[title='"+find_str+"']"
        #print('selector:%s' % selector)
        link = None
        try:
            #在本选择器中，link可能已经被点击，挪到了右侧区域，所以要处理一下
            #link = self.root.find_element_by_css_selector(selector)
            link = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['css selector',selector]))
            #print('ok')
        except:
            pass
        #print('link type:%s' % type(link))
        if(link!=None):
            if (link.is_displayed()):
                link.click()
            else:
                #元素隐藏了，说明已经被选中到右边,目前就这样了，不再继续处理
                pass
            #self.clickAndScroll(link)
            #link.click()
    #展开父部门分支
    def toggleBranch(self, branch, action='toggle'):
        success=True
        #print('try to expand branch:%s ' % branch)
        find_str=branch.decode(__default_encoding__)
        # 用于ztree-like的干节点展开
        
        #id = 'grcsp_left_cjs_deps'
        #id = 'grcsp_'  
        
        #获取部门展开手柄
        xpath="//*[@id='"+self.id+"']//li[@id]/a[@title='"+find_str+"']/preceding-sibling::*[1][contains(@id,'_switch')]"
        
        #print(xpath)
        #处理懒加载
        switch = self.__findElements_by_xpath(self.handle.driver,xpath)[0]
        #switch = self.root.find_element_by_xpath(xpath)
        #switch = WebDriverWait(self.handle.driver, 10).until(EC.presence_of_element_located(['xpath',xpath]))
        
        target_id = switch.get_attribute('id')
        
        #将对应的节点移动到显示区域，以便展开（实测，如果不在显示区域，点击不报错，但也不会展开）
        self.targetScroll(self.cntr_id,target_id)
        
        el_class = switch.get_attribute('class')
        #print(el_class)
        if (action=='open'):
            #打开操作，只展开
            if ('_close' in el_class):
                self.expandAndWait(switch)
            else:
                success=False
        elif(action=='close'):
            #关闭操作，只关闭
            if (not '_close ' in el_class):
                self.expandAndWait(switch)
            else:
                success=False
        else:
            #否则，切换状态
            self.expandAndWait(switch)
        return success
    '''    
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def clickAndScroll(self, el):
        #展开部门时，由于人员可能会在显示区域以外，此时，click不会报错，对应的js不会执行（或有效执行），因此，此处通过对点击效果的检查（例如左侧隐藏，右侧显示），来判断是否已经“有效”点击，如果没有，则卷滚后继续点击，直到成功为止
        scrollby = 80 #默认滚动高度
        self.jScroll(0)
        iniStatus = el.is_displayed()
        #print('ini:%s' % iniStatus)
        if (el.is_displayed()):
            el.click()
        else:
            #元素隐藏了，说明已经被选中到右边
            pass
        sleep(1)
        i=0
        scrollTop=0
        scrollLeft=0
        while(el.is_displayed()==iniStatus and i<10):
            #click以后，class没有变化，说明元素不在显示区域，需要滚动对应的div后重新尝试
            #print('no%i:%s' % (i,el.is_displayed()))
            scrollTop=scrollTop+scrollby
            self.jScroll(scrollTop)
            el.click()
            sleep(1)
            i=i+1
        #print('scroll time:%i' % i)
    '''
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def expandAndWait(self, switch, max_try=120, wait=1,retry=2):
        #增加了对等待图标的检测，如果等待图标消失，还没展开，则直接结束，重新访问
        switch_id = switch.get_attribute('id')
        ico_id = switch_id.replace('_switch','_ico')
        ico = self.handle.driver.find_element_by_id(ico_id)
        iniStatus = switch.get_attribute('class')
        icoStatus = ico.get_attribute('class')
        switch.click()
        i=0
        completed = False
        loading = False
        ready = False
        while(not completed and i<max_try):
            #click以后，class没有变化，说明需要等待展开（即ajax异步加载完成）
            i=i+1
            if i%10==0:
                print('scroll times:%i \r' % i),
            sleep(wait)
            #检测
            tempico = ico.get_attribute('class')
            if (not loading and '_loading' in tempico):
                #检测到加载等待图标
                loading = True
                
            if (loading and '_loading' not in tempico):
                #从加载等待状态退出
                loading = False
                ready = True
                #print("no.%i:%s" % (i,tempico))
                icoStatus = tempico
            completed = (switch.get_attribute('class')!=iniStatus)
            
            if (ready and not completed):
                #异常情况，等待已经结束，但是没有展开，例如中移动的党委会议纪要的参与人首次打开的情况，那么再处理一下(尝试数retry减一)
                if retry >0:
                    print('fail to expand ,try time left %i' % retry-1)
                    self.expandAndWait(switch,max_try,wait,retry-1)
                else:
                    #重试结束，抛异常退出
                    raise Exception('Fail to expand the lazytree finally , please reporte to your supportor')
                
        return completed
    #用于检查在异步加载的情况下，指定的异步子元素是否存在（加载完成或达到指定的个数）
    #参数：wait-每次轮询等待时间；max_try-尝试次数；min_required-至少要获取多少子元素才算加载完成；wait_for_complete-完成前需要额外等待多少时间
    def waitForReady(self,cntr,selector_type,sub_selector,wait=1,max_try=240,min_required=1,wait_for_complete=1):
        els = self.__findElements(cntr,selector_type,sub_selector,wait,max_try,min_required,wait_for_complete)
        return (len(els)>=min_required)
        
    def ready(self):
        cntr = self.handle.driver.find_element_by_id(self.id)
        success=self.waitForReady(cntr,'css selector',self.selectors['items'],wait=1,max_try=240,min_required=1,wait_for_complete=1)
        return success
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效(将目标元素，移到中央位置)
    def targetScroll(self, baseId, targetId):
        jscode = "!function(){base = $('#"+baseId+"');base.scrollTop(0);t=$('#"+targetId+"');scrollY=t.offset().top-(base.offset().top+base.height()/2-t.height()/2);base.scrollTop(scrollY);}()"
        self.handle.driver.execute_script(jscode)
    #用于滚动尝试,通过检查css的变化来确认滚动是否生效
    def jScroll(self, top=0, left=0):
        jscode="t=$('#"+self.id+"');t.scrollTop(%i);t.scrollLeft(%i);" % (top,left)
        self.handle.driver.execute_script(jscode)
    #从头展开某个部门路径，格式例如'总部/办公厅'，前面的会展开分支，最后一个是点击部门，用于显示部门内容
    def expand(self, treeLinks):
        chains=treeLinks.split('/')
        for i in range(0,len(chains)):
            if (i==len(chains)-1):
                #链条的最后一个是点击叶子节点，用于显示部门内容
                print('leaf:%s clicked' % chains[i].decode(__default_encoding__))
                self.clickLeaf(chains[i])
            else:
                #链条的前面几个会展开分支
                print('branch:%s expanded' % chains[i].decode(__default_encoding__))
                success = self.toggleBranch(chains[i],'open')
                #党办通知中第9环节文书岗处理中，阅知项：政企分公司下有上千人，展开耗时
                sleep(2)
                #if (not success):
                    #break
            sleep(1)
    def expandAll(self, paths):
        #在当前tree上同时展开多个路径
        seperators=','  #支持的分隔符
        list = re.split('['+seperators+']',paths)
        
        #依次选择，由于使用的是ztree变形，人员和部门都在左边，只不过人员是叶子节点，所以使用混合路径展开
        
        for n in list:
            self.expand(n)
            #留出页面节点展开的时间
            sleep(1+self.wait)
