#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 13:20
# encapsulation/encapsulation.py
import pdb
# 封装部分维护在此
__default_encoding__="gbk"

#from config.config_01 import locat_config
from config.SiteConfig import *
from log.log import Logger
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains as AC

import re,time

import win32api
import win32gui
import win32con
#获取到标题为文件上传的窗
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


class UIHandle():
    currentPage=''
    currentSite=''
    logger = Logger()
    siteConfig = SiteConfig()

    # 构造方法，用来接收selenium的driver对象
    @classmethod
    def __init__(cls, driver):
        cls.driver = driver
        #由于需要考虑driver的兼容性和特殊bug，因此需要记录浏览器类型，以供后续甄别和回避特定浏览器的bug
        typeStr = '%s' % type(driver)  # 例如：<class 'selenium.webdriver.firefox.webdriver.WebDriver'>
        list = typeStr.split('.')
        cls.driverType = list[2]
        cls.logger.debug('在浏览器（%s）中初始化UIHandle和测试驱动' % cls.driverType)

    # 输入地址
    @classmethod
    def get(cls, url):
        cls.logger.debug('打开url(%s)' % url)
        cls.driver.get(url)

    # 关闭浏览器驱动
    @classmethod
    def quit(cls):
        cls.logger.debug('测试驱动关闭')
        cls.driver.quit()

    # element对象（还可加入try，截图等。。。）
    @classmethod
    def element(cls, page, element,siteName="",text="",context={}):
        if(siteName==""):
            #没有提供站点参数，则默认当前站点
            siteName=cls.currentSite
        if(page==""):
            #没有提供页面参数，则默认当前页面
            page=cls.currentPage

        #方便起见，页面信息为内置隐含参数，不需要每次人工输入，打开站点首页或更新页面后，对象会自动更新该参数
        page=cls.currentPage
        
        #日志
        cls.logger.info('页面元素（%s）-(page:%s;site:%s)' % (element,page,siteName))

        el = None
        if(text!=""):
            #需要进行文本比较，那么先选出所有符合条件的元素，然后找出第一个符合text条件的元素
            t=text.decode(__default_encoding__)
            els = cls.elements(page, element,siteName="",context=context)
            for l in els:
                if(t in l.text):
                    el = l
                    break
        else:
            # 不需要查询文本，直接查找指定条件的元素即可
            # 加入隐性等待
            # 此处便可以传入config_o1中的dict定位参数
            #el = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located(locat_config[page][element]))
            searchPath = cls.siteConfig.getElement(siteName,element,context=context)
            el = WebDriverWait(cls.driver, 50).until(EC.presence_of_element_located(searchPath))
        # 加入日志
        cls.logger.debug('页面元素（%s）ok--page:%s;site:%s' % (element,page,siteName))
        return el
    @classmethod
    def elementClickable(cls, page, element,siteName="",text="",context={}):
        if(siteName==""):
            #没有提供站点参数，则默认当前站点
            siteName=cls.currentSite
        if(page==""):
            #没有提供页面参数，则默认当前页面
            page=cls.currentPage

        #方便起见，页面信息为内置隐含参数，不需要每次人工输入，打开站点首页或更新页面后，对象会自动更新该参数
        page=cls.currentPage

        # 加入日志
        cls.logger.info('可点击元素（%s）-(page:%s;site:%s)' % (element,page,siteName))

        el = None
        if(text!=""):
            #需要进行文本比较，那么先选出所有符合条件的元素，然后找出第一个符合text条件的元素
            t=text.decode(__default_encoding__)
            els = cls.elements(page, element,siteName="",context=context)
            for l in els:
                if(t in l.text):
                    el = l
                    break
        else:
            # 不需要查询文本，直接查找指定条件的元素即可
            # 加入隐性等待
            # 此处便可以传入config_o1中的dict定位参数
            #el = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located(locat_config[page][element]))
            searchPath = cls.siteConfig.getElement(siteName,element,context=context)
            el = WebDriverWait(cls.driver, 60).until(EC.element_to_be_clickable(searchPath))
        # 加入日志
        cls.logger.debug('可点击元素（%s）ok--page:%s;site:%s' % (element,page,siteName))
        return el
    # element对象(还未完成。。。)
    @classmethod
    def elements(cls, page, element,siteName="",context={}):
        if(siteName==""):
            #没有提供站点参数，则默认当前站点
            siteName=cls.currentSite
        if(page==""):
            #没有提供页面参数，则默认当前页面
            page=cls.currentPage

        #方便起见，页面信息为内置隐含参数，不需要每次人工输入，打开站点首页或更新页面后，对象会自动更新该参数
        page=cls.currentPage

        # 加入日志
        cls.logger.debug('元素集合（%s）-(page:%s;site:%s)' % (element,page,siteName))
        # 加入隐性等待
        WebDriverWait(cls.driver, 20)
        searchPath = cls.siteConfig.getElement(siteName,element,context=context)
        #els = cls.driver.find_elements(*locat_config[page][element])
        els = cls.driver.find_elements(*searchPath)
        # 注意返回的是list
        cls.logger.debug('元素集合（%s）ok--page:%s;site:%s' % (element,page,siteName))
        return els

    # send_keys方法
    @classmethod
    def Input(cls,element, msg,page="", siteName="",context={}):
        el = cls.element(page, element, siteName,context=context)
        el.clear()
        el.send_keys(msg.decode(__default_encoding__))

    #检查传入的字串是否是可替换关键字，这里有两种（静态关键字和公式关键字），静态关键字可以直接用context替换，公式关键字类似now[fmt:yyyy-m-d]，需要有业务逻辑计算扩展
    @classmethod
    def replace_with_key(self,key,context={}):
        keys = context.keys()
        replace_flag = False
        key = key.strip()
        if (key in keys):
            #context静态替换优先
            v = "%s" % context[key]
            replace_flag = True
        elif(key.startswith('now')):
            #填写当前时间
            if(key.startswith('now[') and key.endswith(']')):
                #时间带格式等参数设置
                params = key[4:-1].split(',')
                fmt = '%Y-%m-%d'
                for p in params:
                    arr = p.split(':')
                    p_name = arr[0]
                    p_value = arr[1]
                    if(p_name=='fmt'):
                        fmt=p_value
                    #其他参数以后需要时再添加
                v=time.strftime(fmt,time.localtime(time.time()))
                
            else:
                #缺省时间格式
                v=time.strftime('%Y%m%d',time.localtime(time.time()))
                
            pass
            replace_flag = True
        elif(key=='timestamp'):
            #填写当前时间戳
            v=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
            replace_flag = True
        else:
            #都找不到，不是可替换key，保留原值
            v = key
            replace_flag = False
        return (v,replace_flag)
    #计算设置中传入的伪变量,例如替换$docTitle$, context={'docTitle':'公文'}
    @classmethod
    def compute(self,value,context={}):
        seperator = '$'
        if(len(context))==0:
            return value
        arr = value.split(seperator)
        keys = context.keys()
        if(len(arr)>=2):
            s=arr[0]
            last_key = False
            for i in range(1,len(arr)):
                f = arr[i]
                if(last_key==True):
                    #上一个片段是可替换关键字，由于已经使掉分隔符，后面不管是空字串还是其他分分隔符字串，都不应该是可替换关键字
                    last_key = False
                    #因不可能是可替换关键字，直接追加本片段,不加分隔符
                    s = "%s%s" % (s,f)
                else:
                    v,replace_flag = self.replace_with_key(f,context)
                    
                    if(replace_flag==True):
                        #找到一个可替换key值,替换掉
                        #标记一下，用于下一片段判断分隔符是否应该去掉
                        last_key = True
                        #替换关键字
                        s = "%s%s" % (s,v)
                    else:
                        #这个片段不是关键字，则直接添加，并恢复分隔的分隔符
                        s = "%s%s%s" % (s,seperator,f)
            value=s
        return value
    #执行指定的js代码
    @classmethod
    def executeScript(self,script,context={}):
        self.driver.execute_script(script)
    #添加慧点使用的地址簿对象,element是ini中的标识
    @classmethod
    def executeInput(self,cntr,element,value,context={}):
        css_selector = self.getElementSelector('',element,context=context)
        if css_selector=="":
            raise Exception('cannot found the element(%s)\'s selector defination. please contact your test supporter' % element)
        
        el = cntr.find_element_by_css_selector(css_selector)
        id = el.get_attribute('id')
        if (id==''):
            name = el.get_attribute('name')
            selector = '*[name="%s"]' % name
        else:
            selector = '#%s' % id
        script = "(function(sel,value){$(sel).val(value);}('"+selector+"','"+value+"'))"
        print('script run:\n%s' % script)
        
        self.driver.execute_script(script)

    # 获取指定元素的锚定义
    @classmethod
    def getElementPath(cls, page, element,siteName="",context={}):
        if(siteName==""):
            #没有提供站点参数，则默认当前站点
            siteName=cls.currentSite
        if(page==""):
            #没有提供页面参数，则默认当前页面
            page=cls.currentPage

        #方便起见，页面信息为内置隐含参数，不需要每次人工输入，打开站点首页或更新页面后，对象会自动更新该参数
        page=cls.currentPage
        searchPath = cls.siteConfig.getElement(siteName,element,context=context)
        return searchPath

    # 获取指定元素的css 选择器
    @classmethod
    def getElementSelector(cls, page, element,siteName="",context={}):
        
        path = cls.getElementPath(page,element,siteName,context=context)
        
        pathType = path[0].lower()
        value =  path[1]
        if(pathType=='id'):
            selector = '#%s' % value
        elif(pathType=='css selector'):
            selector = value
        else:
            #不能获取合法的css选择器，干脆返回空值，以供后续代码识别
            selector = ""
        return selector

    # click方法
    @classmethod
    def Click(cls, element, page="", siteName="", context={}):
        el = cls.elementClickable(page,element,siteName,context=context)
        print('element click:%s' % element.decode(__default_encoding__))
        #print("tag:%s,id:%s" % (el.tag_name,el.id))
        el.click()
    # Following is updated by lianhua
    
    # 打开指定站点，如果设置中有'首页'或指定页面的url设置，则打开对应的网页url
    @classmethod
    def openSite(cls,siteName,page='首页'):
        s=cls.siteConfig
        url=s.getUrl(siteName,page)
        if(url==""):
            raise ValueError('站点页面URL设置有误，请检查'.decode(__default_encoding__))
            return False
        cls.logger.loginfo(url)
        cls.driver.get(url)
        #更新当前站点和页面设置，便于后续的连续简易处理
        cls.currentSite=siteName
        cls.currentPage=page
        return True

    # 打开指定页面,站点名称参数可选，默认为当前使用的站点
    @classmethod
    def openPage(cls,page,siteName=""):
        if(siteName==""):
            #没有提供站点参数，则默认当前站点
            siteName=cls.currentSite
        cls.openSite(siteName,page)
        sleep(5)

    # 模拟鼠标移动，用于菜单等动态显示元素
    @classmethod
    def moveTo(cls, element, page="", siteName="", context={}):
        el = cls.element(page,element,siteName,context=context)
        actions = AC(cls.driver)
        actions.move_to_element(el)
        actions.perform()
 
    # 下拉框选择,通过选项文本来选择
    @classmethod
    def select(cls, element,optionText, page="", siteName="",context={}):
        el = cls.element(page,element,siteName,context=context)
        opts=el.find_elements_by_tag_name('option')
        for opt in opts:
            if(optionText.decode(__default_encoding__) in opt.text):
                opt.click()
                break
    # 获取指定元素所对应的文本
    @classmethod
    def text(cls, element, page="", siteName="", default='',context={}):
        text = default
        try:
            el = cls.element(page,element,siteName,context=context)
            text = el.text
        except:
            pass
        return text

    # 点击列表的指定文本的行的链接（假设该行链接都一样）
    @classmethod
    def tableRowClick(cls, element,rowText, page="", siteName="", context={}):
        success = False
        el = cls.element(page,element,siteName,context=context)
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
    # 从视图中查找指定文本的列和行号（是tr的序号，不见得是真正的行号，因为可能包含标题行）
    @classmethod
    def findRowInTable(cls, element,rowText, page="", siteName="", context={}):
        n=-1
        findStr = rowText.decode(__default_encoding__)
        els = cls.element(page,element,siteName,context=context)
        lists=els.find_elements_by_tag_name('tr')
        i=0
        for l in lists:
            s = l.text
            #print("line:%s" % s)
            if(findStr in s):
                n=i
                break
            i = i+1
        return n
    # 切换到指定窗口,通过窗口标题选择,使用in判断，支持部分匹配，找到第一个为止
    @classmethod
    def switchWindow(cls, title=""):
        wlst=cls.driver.window_handles
        cls.windows = wlst
        i = 0
        for handle in wlst:
            cls.driver.switch_to_window(handle)
            cls.activeWinIdx = i
            wtitle=cls.driver.title
            if((title=="" and wtitle=="") or (title!="" and title.decode(__default_encoding__) in wtitle)):
                break
            i = i+1
    # 当窗口被关闭以后，driver并不会自动更新当前窗体，这是再查找元素，还是试图在原窗体句柄中查询，所以会出现unable to locate window错误，因此，我们需要增加一个步骤，显式关闭之前的窗体，并设置当前窗体为之前窗体（逻辑是窗体列表减一）,当然，如果手动设置了title，则自动切换到title对应的窗体上
    @classmethod
    def closeWindow(cls, title=""):
        if(title!=''):
            #手动设置了title，则自动切换到title对应的窗体上
            cls.switchWindow(title)
        else:
            wlst = cls.windows
            actIdx = cls.activeWinIdx
            if (actIdx>0):
                #默认设置为之前的窗体（假设是依次打开的，所以依次关闭）
                cls.driver.switch_to_window(wlst[actIdx-1])
                cls.windows=cls.driver.window_handles
                cls.activeWinIdx = actIdx-1
            else:
                #关闭的是第一个窗体，则默认切换为之后的窗体
                cls.windows=cls.driver.window_handles
                cls.driver.switch_to_window(cls.windows[0])
                cls.activeWinIdx = actIdx-1
    # 上传文件
    @classmethod
    def upload(cls,element, filePath="",context={}):
        #el = cls.moveTo(element)
        el = cls.elementClickable("",element,"",context=context)
        el.click()
        
        procHandle = win32gui.FindWindow(None,'文件上传'.decode(__default_encoding__))
        win32gui.SetForegroundWindow(procHandle) 
        #获取到类名为ComboBoxEx32的选择框
        edit = win32gui.FindWindowEx(procHandle,0,"ComboBoxEx32",None)
        win32api.SendMessage(edit, win32con.WM_SETTEXT, 0, filePath)
        openBt = win32gui.FindWindowEx(procHandle,0,"Button",'打开(&O)'.decode(__default_encoding__))
        #进行鼠标的点击
        win32api.PostMessage(openBt, win32con.WM_LBUTTONDOWN, 0, 0)
        win32api.PostMessage(openBt, win32con.WM_LBUTTONUP, 0, 0)

    #判断某元素是否显示
    @classmethod
    def isDisplayed(cls,element,context={}):
        try:
            el = cls.element('',element,context=context)
            return el.is_displayed()
        except:
            return False
    #判断是否存在某元素
    @classmethod
    def isElementExist(cls,element,context={}):
        siteName=cls.currentSite
        searchPath = cls.siteConfig.getElement(siteName,element,context=context)
        t=searchPath[0]
        v=searchPath[1]
        try:
            #cls.element('',element)
            el = cls.driver.find_element(t,v)
            if (el.is_displayed()):
                print('--check:%s exists!!!!' % element.decode(__default_encoding__))
                return True
        except:
            return False
        return False
    #判断是否存在alert
    @classmethod
    def isAlertPresent(cls):#有问题的函数，有时间再研究
        try:
            alt = cls.driver.switch_to_alert()  #这个不管用，不会抛异常啊？？？？
            return True
        except:
            return False

    #截图
    @classmethod
    def save_screenshot(cls, filePath=""):
        if filePath!="":
            filePath=filePath.decode(__default_encoding__)
            cls.driver.save_screenshot(filePath)
    #sample：表单截图|align=top&selector=#mainToId_th&prefix=意见截图
    @classmethod
    def formScreenShot(self,actionStr):
        if not actionStr.startswith('表单截图'):
            return
            
        settings=actionStr.split('|')[1]
        parameters = settings.split('&')
        para={}
        for p in parameters:
            v=p.split('=')
            if len(v)==2 and v[0]!='':
                para[v[0].lower()]=v[1]
        #处理截图文件名
        now = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
        if(para.has_key('prefix')):
            filename  = "%s_%s.png" % (para['prefix'],now)
        else:
            filename  = "表单截图_%s.png" % now
        fname = './screenshot/'+filename
        #print('filename:%s' % fname)
        #处理目标元素的选择器（目前只支持css选择器）,如果没有，则不再卷滚定位，直接截图
        if(para.has_key('prefix')):
            selector = para['selector']
        else:
            selector = ""
            
        #如果是元素定位截图（selector不为空），则需要处理截图时的元素定位（目前支持上-top、中-center）
        if(para.has_key('align')):
            align = para['align'].lower()
        else:
            align = ""
        #print('align:%s' %align)
        #处理元素定位卷滚
        if(selector!=""):
            if(align=='center'):
                self.centerElementInWindow(selector)
            elif(align=='top'):
                self.topElementInWindow(selector)
        
        #截图
        self.save_screenshot(fname)
        
        
    #获取配置文件中的用户信息
    @classmethod
    def getUser(cls, name):
        return cls.siteConfig.getUser(cls.currentSite,name)
    #将指定的用户名列表（字符串）转换为用户数组
    @classmethod
    def getUsers(cls, nameList):
        seperators=',;: '  #支持的分隔符,注意：正则的分隔符不支持中文，中文逗号与“超”冲突，会以\xac分割超
        list = re.split('['+seperators+']',nameList)
        names = []
        infos = []
        for n in list:
            names.append(n)
            infos.append(cls.getUser(n))
        return names,infos
    #卷滚屏幕，使指定元素（通过css selector选择）居中，方便后续操作，例如截图
    @classmethod
    def centerElementInWindow(self, selector):
        func = 'function __centerElementInWindow(el){targetY=el.offset().top+el.height()/2; screenHeight=document.documentElement.clientHeight;scrolly=targetY - screenHeight/2;    if(scrolly>0) window.scroll(0,scrolly);}'
        jscode=func+"t=$('"+selector+"'); __centerElementInWindow(t);"
        self.driver.execute_script(jscode)
    #卷滚屏幕，使指定元素（通过css selector选择）置顶，方便后续操作，例如表格截图
    @classmethod
    def topElementInWindow(self, selector):
        func = 'function __topElementInWindow(el){scrolly=el.offset().top-el.height()/2;if(scrolly>0) window.scroll(0,scrolly);}'
        jscode=func+"t=$('"+selector+"'); __topElementInWindow(t)"
        self.driver.execute_script(jscode)
