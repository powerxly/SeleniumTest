#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 13:22
# function/function_01.py
# 业务功能脚本（用例脚本可调用此处的功能脚本）
import unicodedata
__default_encoding__="utf-8"

#from encapsulation.encapsulation import UIHandle
from encapsulation.mobile_uat import SmartHandle,View
#from constant.constant_01 import LOGIN_URL
from config.config_01 import browser_config
from encapsulation.webdriver.myerrorhandler import MyErrorHandler
from encapsulation.mobile_uat import Workflow,WorkflowNode,Form
from time import sleep
import time
import re
from log.log import Logger

from selenium.webdriver.common.action_chains import ActionChains as AC


def oa_init():
    # 打开浏览器
    #driver = browser_config['ie']()
    driver = browser_config['firefox']()
    #定制异常处理程序
    driver.error_handler = MyErrorHandler(driver,screen_shot=True,site='mobile_uat')
    # 传入driver对象
    uihandle = SmartHandle(driver)
    return uihandle
def oa_login(uihandle,username):
    #打开站点，默认“首页”
    siteName = "移动UAT"
    uihandle.openSite(siteName)
    
    sleep(2)

    user = uihandle.getUser(username)
    id = user[0]
    pwd = user[1]
    print('user:%s  pwd:%s' % (id,pwd.encode('utf-8')))

    # 调用二次封装后的方法，此处可见操作了哪个页面，哪个元素，msg是要插入的值，插入值的操作在另外一个用例文件中传入
    #uihandel.openPage("登陆页")
    uihandle.Input('登陆页密码输入框', pwd)
    uihandle.Input('登陆页用户名输入框', id)
    uihandle.Click('登陆页登录按钮')
    
    sleep(10)
    
    #关闭注册提示
    uihandle.Click('注册提示关闭按钮')
    
    sleep(1)
def oa_try(test,uihandle,docTitle="",runPaths='',resume=0,stop=10000,flow='移动学院团委发文',retry=0):
    
    wf = Workflow(uihandle,flow,sourceType='excel')
    wf.setDocTitle(docTitle)
    #从流程配置中获取需要运行检验的路径
    paths = wf.runPaths
    uihandle.logger.info('docTitle:%s' % docTitle)
    
    for p in paths:
        #runPaths为空，说明运行所有流程路径,否则，只允许指定的流程路径
        if runPaths=='' or p in runPaths:
            #该路径需要执行
            
            path = wf.getPath(p)
            uihandle.logger.info('\n============开始执行流程（%s）的路径（%s）============' % (flow,p) )
            
            i=0 #计数器，用于判断开始节点
            for n in path:
                uihandle.logger.info('\n===========No.%i node(%s) begin!===========' % (i,n))
                print('\n--No.%i node(%s) begin:' % (i,n.decode(__default_encoding__)))
                
                #断点继续,跳过resume之前的节点
                if i<resume:
                    i=i+1
                    continue
                if i>=stop:
                    #运行到指定节点结束，以便人工排查问题
                    break
                #检查路径中的节点，开始一个新流程
                node = WorkflowNode(wf,n)
                
                attempts = retry
                
                while attempts>=0:
                    try:
                        if(node.type=='start'):
                            #首节点，意味着流程启动节点
                                    oa_test_step_start(test,node)
                        elif node.type=='screenshot':
                            #流程跟踪截图
                            oa_save_flow_track(test,node)
                        elif node.type=='end':
                            #流程结束节点
                            oa_test_step_end(test,node)
                            pass
                        else:
                            oa_test_step_next(test,node)
                            #pass
                        #成功执行，则终止尝试循环
                        attempts = -1
                    except:
                        attempts = attempts-1
                        if(attempts<0):
                            #todo 1、重新抛异常。2、在result中记录
                            raise Exception('error. stop')
                        else:
                            sleep(1)
                            print('step %i failed, try the %i time' % (i,retry-attempts))
                            #uihandle.quit()
                            sleep(4)
                #print(node)
                i=i+1
def oa_test_step_start(test,node):
    uihandle = oa_init()
    node.workflow.handle=uihandle
    #由于需要循环测试，因此必须从登录开始，保证测试的原子性和可重复性
    
    uihandle = node.workflow.handle
    docTitle = node.docTitle
    
    transition = node.get('transition')

    user = node.get('user')
    assignee = node.get('assignee')

    actions = node.getActions()
    #print("startnode actions:%s" % actions)
    
    oa_login(uihandle,user)

    menu = node.get('startMenu')
    if(menu!=''):
        uihandle.menu.click(menu)
        sleep(5)
        #切换到新窗口
        uihandle.switchWindow("")

    context = {'docTitle':docTitle}
    sleep(3)
    node.autoFillForm(context)

    #处理是否有额外操作，如果有，应在提交前完成
    actions = node.getActions()
    #print("actions:%s" % actions)
    for i in actions:
        if (i=='编号'):
            if uihandle.isDisplayed('编号按钮'):
                uihandle.Click('编号按钮')
                #需要等待时间
                sleep(3)
                try:
                    #已经编过号，这里弹出确认提示，需要关闭
                    alt = uihandle.driver.switch_to_alert()
                    print('alert prompt: %s' % alt.text)
                    alt.accept()
                    sleep(3)
                except:
                    #没编过号
                    pass
                uihandle.Click('编号确定按钮')
                sleep(3)
        elif (i.startswith("表单截图|")):
            #截图字串样例 '表单截图|align=top&selector=#mainToId_th&prefix=意见截图'
            uihandle.formScreenShot(i)
        
    uihandle.Click('提交下一处理')
    #todo检查是否成功提交
    sleep(5)
 
    #选择分支
    if transition.lower()=='default':
        transition=''
    if (transition!=''):
        uihandle.selectTransition(transition)
        uihandle.submitOpinion()
    sleep(0.5)
    
    if assignee.lower()=='default':
        assignee=''

    #处理下一环节处理人
    if (assignee!=''):
        uihandle.assignee(assignee)
        sleep(1)
        #提交人员选择结果
        uihandle.Click('人员提交按钮')
        
    sleep(5)
    
    #确认提示
    uihandle.Click("人员提交确定按钮")
    
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    uihandle.quit()
#进入发文视图，检查指定文档
def oa_test_step_next(test,node):
    uihandle = oa_init()
    node.workflow.handle=uihandle
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    #uihandle = node.workflow.handle
    docTitle = node.docTitle
    transition = node.get('transition')
    opinion = node.get('opinion')
    
    user = node.get('user')
    assignee = node.get('assignee')
    
    oa_login(uihandle,user)
    
    #切换到消息frame
    utsframe = uihandle.element('','消息帧')
    #utsframe = uihandle.driver.find_element_by_id('iframecontent-utsmain')
    uihandle.driver.switch_to_frame(utsframe)

    view = View(uihandle,'待办视图',checkSelector="table[id='todo']")
    if (not view.ready()):
        raise Exception('视图(%s)没找到，测试终止' % view.viewname)
    #todo 未正确加载怎么处理

    #test.assertTrue(view.isDocInView(docTitle))
    #实际出现过早点击，打不开文档
    sleep(1)
    found = view.clickDocInView(docTitle)
    if(not found):
        raise Exception('some error occurrs while finding document(%s) in View(%s)' % (docTitle,view.viewname))
    sleep(8)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    sleep(3)

    #处理是否有额外操作，如果有，应在提交前完成
    actions = node.getActions()
    uihandle.logger.debug("actions:%s" % actions)
    for i in actions:
        if (i=='编号'):
            uihandle.logger.info("开始编号")
            if uihandle.isDisplayed('编号按钮'):
                uihandle.Click('编号按钮')
                #需要等待时间
                sleep(3)
                try:
                    #已经编过号，这里弹出确认提示，需要关闭
                    alt = uihandle.driver.switch_to_alert()
                    uihandle.logger.debug('alert prompt: %s' % alt.text)
                    alt.accept()
                    sleep(3)
                except:
                    #没编过号
                    pass
                uihandle.Click('编号确定按钮')
                sleep(3)
            else:
                uihandle.logger.info("没找到编号按钮，继续")
             
        elif (i.startswith("表单截图|")):
            #截图字串样例 '表单截图|align=top&selector=#mainToId_th&prefix=意见截图'
            uihandle.logger.info("开始截图:参数为（%s）" % i)
            uihandle.formScreenShot(i)
        elif (i.startswith("发送文件|")):
            #发送文件
            i=i.replace('发送文件','multi').replace('&',',')
            uihandle.logger.info("发送文件:参数为（%s）" % i)
            #i最终格式'multi|部门:财务部,技术部;分公司:北京,河北'
            uihandle.field('发送文件按钮',i,'fenfa_org')
            sleep(10)
        elif (i=='发送文件_只确认'):
            uihandle.logger.info("发送文件:直发，无参数")
            #处理直接发送文件，不需要选择，只确认的情况
            uihandle.Click('发送文件按钮')
            sleep(5)
            alt = uihandle.driver.switch_to_alert()
            if(alt.text!=''):
                uihandle.logger.debug("执行发送文件操作:返回确认提示（“%s”）".decode(__default_encoding__) % alt.text)
                alt.accept()
                
                sleep(4)
                
                #发送成功确认
                alt = uihandle.driver.switch_to_alert()
                if(alt.text!=''):
                    uihandle.logger.debug("执行发送文件操作:返回成功提示（“%s”）".decode(__default_encoding__) % alt.text)
                    alt.accept()
            #需要等待页面刷新，不然后续页面还没刷出来就执行了，会报错
            sleep(10)

        elif (i=='归档'):
            uihandle.logger.debug('检查是否已经归档')
            if uihandle.isDisplayed('归档按钮'):
                uihandle.logger.info("执行归档")
                uihandle.Click('归档按钮')
                #需要等待时间
                sleep(3)
                
                #确认归档提示
                alt = uihandle.driver.switch_to_alert()
                if(alt.text!=''):
                    uihandle.logger.debug("执行归档操作:返回提示（“%s”）".decode(__default_encoding__) % alt.text)
                    alt.accept()
                    sleep(3)
                #没有alert，说明还没有归档过
                if uihandle.isDisplayed('归档确定按钮'):
                    uihandle.setArchive("短期")
                    uihandle.Click('归档确定按钮')
                    sleep(2)
                
                #归档成功确认
                alt = uihandle.driver.switch_to_alert()
                if(alt.text!=''):
                    uihandle.logger.debug("归档成功:返回提示（“%s”）".decode(__default_encoding__) % alt.text)
                    alt.accept()
                    sleep(3)
                #等待归档带来的页面刷新
                sleep(10)
            else:
                uihandle.logger.info('之前已归档，不再另行归档')
    
    uihandle.Click('提交下一处理')
    #todo检查是否成功提交
    sleep(3)
    
    #填写意见，注：由于决策性意见会触发分支的刷新，因此必须先填意见，后选分支
    if (opinion!=''):
        uihandle.setOpinion(opinion)
            
    #选择分支
    if transition.lower()=='default':
        transition=''
    if (transition!=''):
        uihandle.selectTransition(transition)
    
    uihandle.logger.info('--opinion:%s \n--transition:%s' % (opinion.decode(__default_encoding__),transition.decode(__default_encoding__)))
    #print('-opinion:%s \n-transition:%s' % (opinion.decode(__default_encoding__),transition.decode(__default_encoding__)))
    #提交前面的意见和流程分支窗体
    if (opinion!='' or transition!=''):
        sleep(0.5)
        uihandle.submitOpinion()
    
    
    #处理下一环节处理人
    if (assignee!=''):
        #等待，预防时间不足，导致选人页面未加载完成引起的错误，典型场景，党办文件-文书岗阅知
        #sleep(15)
        
        uihandle.assignee(assignee)
        sleep(5)
        #提交人员选择结果
        uihandle.Click('人员提交按钮')
    
    sleep(5)
    
    #确认提示,即使使用默认处理人，也需要确定
    if( uihandle.isDisplayed('人员提交确定按钮') ):
        prompt = uihandle.text('人员提交前提示内容','','','')
        
        print('人员提交前提示:%s'.decode(__default_encoding__) % prompt)
        uihandle.Click("人员提交确定按钮")
    else:
        #会签中一条分支结束，但还有分支没结束时，只会提示是否结束（本分支），而不会有人员提交按钮出现
        alt = uihandle.driver.switch_to_alert()
        if(alt.text!=''):
            print('当前分支结束，提示: %s'.decode(__default_encoding__) % alt.text)
            alt.accept()
    sleep(3)
 
    
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    uihandle.quit()

    #日志
    uihandle.logger.debug('流程中间环节结束')
    
#进入保存流程跟踪的结果
def oa_save_flow_track(test,node):
    uihandle = oa_init()
    node.workflow.handle=uihandle
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    uihandle = node.workflow.handle
    docTitle = node.docTitle
    filename = node.get('filename')
    
    user = node.get('user')
   
    oa_login(uihandle,user)
    
    #切换到消息frame
    utsframe = uihandle.element('','消息帧')
    uihandle.driver.switch_to_frame(utsframe)

    view = View(uihandle,'待办视图')
    #todo 未正确加载怎么处理

    #test.assertTrue(view.isDocInView(docTitle))
    #实际出现过早点击，打不开文档
    sleep(20)
    view.clickDocInView(docTitle)
    
    sleep(8)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    
    sleep(3)
   
    #截图验证
    uihandle.Click('流程跟踪按钮')
    sleep(3)
    uihandle.switchWindow('')
    uihandle.save_screenshot('./screenshot/'+docTitle+'_'+filename+'.png')
    
    #todo 解决停止响应问题
    #uihandle.Click('流程跟踪关闭按钮')
 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    uihandle.quit()



    
#最后一个环节，需要额外处理提示窗
def oa_test_step_end(test,node):
    uihandle = oa_init()
    node.workflow.handle=uihandle
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    uihandle = node.workflow.handle
    docTitle = node.docTitle
    transition = node.get('transition')
    opinion = node.get('opinion')
    actions = node.getActions()
    #print(actions)
    
    user = node.get('user')
    #assignee = node.get('assignee')
    
    oa_login(uihandle,user)
    #切换到消息frame
    utsframe = uihandle.element('','消息帧')
    uihandle.driver.switch_to_frame(utsframe)

    view = View(uihandle,'待办视图')


    #截图验证
    #uihandle.save_screenshot('./screenshot/显示公文菜单.png')

    view = View(uihandle,'待办视图')

    #实际出现过早点击，打不开文档
    sleep(15)
    view.clickDocInView(docTitle)
    
    sleep(8)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    sleep(5)
    
    for i in actions:
        if (i=='编号'):
            if uihandle.isDisplayed('编号按钮'):
                uihandle.Click('编号按钮')
                #需要等待时间
                sleep(3)
                try:
                    #已经编过号，这里弹出确认提示，需要关闭
                    alt = uihandle.driver.switch_to_alert()
                    print('alert prompt: %s' % alt.text)
                    alt.accept()
                    sleep(3)
                except:
                    #没编过号
                    pass
                uihandle.Click('编号确定按钮')
                sleep(3)
        elif (i.startswith("表单截图|")):
            #截图字串样例 '表单截图|align=top&selector=#mainToId_th&prefix=意见截图'
            uihandle.formScreenShot(i)
        elif (i=="发送文件"):
            #只为了兼容以前的用例，因为参数都写死在代码里了，所以最终应该会废弃掉
            #发送文件
            uihandle.field('发送文件按钮','multi|部门:财务部,技术部;分公司:北京,河北','fenfa_org')
            sleep(5)
        elif (i.startswith("发送文件|")):
            #发送文件
            i=i.replace('发送文件','multi').replace('&',',')
            #i最终格式'multi|部门:财务部,技术部;分公司:北京,河北'
            uihandle.field('发送文件按钮',i,'fenfa_org')
            sleep(10)
        elif (i=='发送文件_只确认'):
            uihandle.logger.info("发送文件:直发，无参数")
            #处理直接发送文件，不需要选择，只确认的情况
            uihandle.Click('发送文件按钮')
            sleep(5)
            alt = uihandle.driver.switch_to_alert()
            if(alt.text!=''):
                uihandle.logger.debug("执行发送文件操作:返回确认提示（“%s”）".decode(__default_encoding__) % alt.text)
                alt.accept()
                
                sleep(4)
                
                #发送成功确认
                alt = uihandle.driver.switch_to_alert()
                if(alt.text!=''):
                    uihandle.logger.debug("执行发送文件操作:返回成功提示（“%s”）".decode(__default_encoding__) % alt.text)
                    alt.accept()
            #需要等待页面刷新，不然后续页面还没刷出来就执行了，会报错
            sleep(10)
        elif (i=='归档'):
            print('检查是否已经归档'.decode(__default_encoding__))
            if uihandle.isDisplayed('归档按钮'):
                print('执行归档'.decode(__default_encoding__))
                uihandle.Click('归档按钮')
                #需要等待时间
                sleep(3)
                
                #确认归档提示
                alt = uihandle.driver.switch_to_alert()
                print('alert prompt: %s' % alt.text)
                alt.accept()
                sleep(3)
                #没有alert，说明还没有归档过
                if uihandle.isDisplayed('归档确定按钮'):
                    uihandle.setArchive("短期")
                    uihandle.Click('归档确定按钮')
                    sleep(2)
                
                #归档成功确认
                alt = uihandle.driver.switch_to_alert()
                print('alert prompt: %s' % alt.text)
                alt.accept()
                #等待归档带来的页面刷新
                sleep(15)
            else:
                print('已归档，不再另行归档'.decode(__default_encoding__))
   
    uihandle.Click('提交下一处理')
    #todo检查是否成功提交
    sleep(2)
    
    #填写意见，注：由于决策性意见会触发分支的刷新，因此必须先填意见，后选分支
    if (opinion!=''):
        uihandle.setOpinion(opinion)
            
    #选择分支
    if transition.lower()=='default':
        transition=''
    if (transition!=''):
        uihandle.selectTransition(transition)
    print('-opinion:%s \n-transition:%s' % (opinion.decode(__default_encoding__),transition.decode(__default_encoding__)))
    #提交前面的意见和流程分支窗体
    if (opinion!='' or transition!=''):
        sleep(0.5)
        uihandle.submitOpinion()
    
    #处理多个确认
    i=0
    while i<3:
        try:
            alt = uihandle.driver.switch_to_alert()
            print('alert prompt: %s' % alt.text)
            alt.accept()
            sleep(1)
            print('alert end')
            i=i+1
        except:
            break
        
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    uihandle.quit()
    