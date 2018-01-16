#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 13:22
# function/function_01.py
# 业务功能脚本（用例脚本可调用此处的功能脚本）
import unicodedata

#from encapsulation.encapsulation import UIHandle
from encapsulation.smartdotoa import SmartHandle,View
#from constant.constant_01 import LOGIN_URL
from config.config_01 import browser_config
from encapsulation.webdriver.myerrorhandler import MyErrorHandler
from encapsulation.smartdotoa import Workflow,WorkflowNode,Form
from time import sleep
import time
import re

from selenium.webdriver.common.action_chains import ActionChains as AC

def oa_init():
    # 打开浏览器
    driver = browser_config['firefox']()
    #定制异常处理程序
    driver.error_handler = MyErrorHandler(driver,screen_shot=True,site='aqkkoa')
    # 传入driver对象
    uihandle = SmartHandle(driver)
    return uihandle
def oa_login(uihandle,username):
    #打开站点，默认“首页”
    siteName = "aqkkptsj"
    uihandle.openSite(siteName)
    
    sleep(5)

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
def oa_logout(uihandle):
    uihandle.Click('系统登出按钮')
    sleep(3)
def oa_try(test,uihandle,docTitle="",runPaths='',resume=0,stop=10000,flow='移动学院团委发文'):
    
    wf = Workflow(uihandle,flow,sourceType='excel')
    wf.setDocTitle(docTitle)
    #从流程配置中获取需要运行检验的路径
    paths = wf.runPaths
    
    for p in paths:
        #runPaths为空，说明运行所有流程路径,否则，只允许指定的流程路径
        if runPaths=='' or p in runPaths:
            #该路径需要执行
            
            path = wf.getPath(p)
            print('========================')
            
            i=0 #计数器，用于判断开始节点
            for n in path:
                print('----No.%i node(%s) begin!---' % (i,n))
                
                #断点继续,跳过resume之前的节点
                if i<resume:
                    i=i+1
                    continue
                if i>=stop:
                    #运行到指定节点结束，以便人工排查问题
                    break
                #检查路径中的节点，开始一个新流程
                node = WorkflowNode(wf,n)
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
                #print(node)
                i=i+1
def oa_test_step_start(test,node):
    #由于需要循环测试，因此必须从登录开始，保证测试的原子性和可重复性
    
    uihandle = node.workflow.handle
    docTitle = node.docTitle
    
    transition = node.get('transition')

    user = node.get('user')
    assignee = node.get('assignee')
    
    oa_login(uihandle,user)

    #根据节点配置，打开对应的菜单项，进入指定视图
    oa_enter_view(node)
    
    #新建公文
    uihandle.Click('公文新建按钮')
    sleep(3)
    
    #切换到新窗口
    uihandle.switchWindow("")
    
    sleep(2)
    #根据节点配置，填写表单内容
    context = {'docTitle':docTitle}
    node.autoFillForm(context)
    
    #uihandle.Click('提交下一处理')
    #todo检查是否成功提交
    sleep(0.5)
 
    #选择分支
    if transition.lower()=='default':
        transition=''
    if (transition!=''):
        uihandle.selectTransition(transition)
    sleep(0.5)
    
    if assignee.lower()=='default':
        assignee=''

    #处理下一环节处理人
    if (assignee!=''):
        uihandle.assignee(assignee)
        sleep(1)
        
    
    #确认提示
    uihandle.Click("公文提交按钮")
    sleep(5)
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    sleep(3)
    oa_logout(uihandle)
#进入发文视图，检查指定文档
def oa_test_step_next(test,node):
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    uihandle = node.workflow.handle
    docTitle = node.docTitle
    transition = node.get('transition')
    opinion = node.get('opinion')
    
    user = node.get('user')
    assignee = node.get('assignee')
    
    oa_login(uihandle,user)

    #根据节点配置，打开对应的菜单项，进入指定视图
    oa_enter_view(node)
    
    view = View(uihandle,'公文视图')
    view.switchToViewTab('处理中')
    test.assertTrue(view.isDocInView(docTitle))
    view.clickDocInView(docTitle)
    
    sleep(10)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    sleep(3)
    
    #填写意见
    if (opinion!=''):
        uihandle.setOpinion(opinion)
            
    #选择分支
    if transition.lower()=='default':
        transition=''
    if (transition!=''):
        uihandle.selectTransition(transition)
    print('opinion:%s \n transition:%s' % (opinion,transition))
    
    
    #处理下一环节处理人
    if (assignee!=''):
        uihandle.assignee(assignee)
    
    sleep(0.5)
    
    #提交
    uihandle.Click('公文提交按钮')
    sleep(3)
 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    oa_logout(uihandle)
    
#进入保存流程跟踪的结果
def oa_save_flow_track(test,node):
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
    oa_logout(uihandle)



    
#最后一个环节，需要额外处理提示窗
def oa_test_step_end(test,node):
    #由于需要循环测试，因此必须从视图开始，保证测试的原子性和可重复性
    uihandle = node.workflow.handle
    docTitle = node.docTitle
    transition = node.get('transition')
    opinion = node.get('opinion')
    
    user = node.get('user')
    assignee = node.get('assignee')
    
    oa_login(uihandle,user)

    #根据节点配置，打开对应的菜单项，进入指定视图
    oa_enter_view(node)
    
    view = View(uihandle,'公文视图')
    view.switchToViewTab('处理中')
    test.assertTrue(view.isDocInView(docTitle))
    view.clickDocInView(docTitle)
    
    sleep(5)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    sleep(1)
    
    #填写意见
    if (opinion!=''):
        uihandle.setOpinion(opinion)
        
        
    #提交
    uihandle.Click('公文提交按钮')
    
    sleep(5)

    try:
        alt = uihandle.driver.switch_to_alert()
        print('alert prompt: %s' % alt.text)
        alt.accept()
        sleep(1)
    except:
        pass
    
    sleep(1)

 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    oa_logout(uihandle)


def oa_enter_view(node):
    #由于需要循环测试，因此必须从登录开始，保证测试的原子性和可重复性
    uihandle = node.workflow.handle
    menu = node.get('startMenu')
    if(menu!=''):
        uihandle.menu.click(menu)
        sleep(5)
        #切换到新窗口
        uihandle.switchWindow("")
    
def aqkkoa_gongwen_fawen_new_cancel(test,uihandle):
    #新建流程
    
    #先进入公文视图
    gongwen_enterFawenView(test,uihandle)
    
    #oa弹出的菜单层似乎会影响新建按钮的触发，移动一下鼠标，使菜单层消失，就没问题了
    uihandle.moveTo('公文新建按钮')
    sleep(5)
    e=uihandle.Click('公文新建按钮')
    sleep(5)
    
    #切换到新窗口
    uihandle.switchWindow("")
    #sleep(15)
    uihandle.select('密级选项','核心商密')
    uihandle.Input('保密年限', "4")
    uihandle.select('文种','意见')
    #uihandle.assignee('宋金超')
    #uihandle.Click('主送选择')
   
    #uihandle.Click('拟定密按钮')
    #uihandle.Click('拟定密之普密选项')
    #sleep(10)
    #uihandle.tableRowClick('拟定密明细表','内部非密传阅制度')
    #uihandle.Click('拟定密确定按钮')
    
    #重新设置一下保密年限，是因为上面的拟密窗体弹出后，会将上传按钮位置向下挤出有效显示区域，使得上传按钮调用失败，
    uihandle.moveTo('保密年限')
    uihandle.Input('保密范围', "办公室内部")
    uihandle.Input('定密依据', "办公室保密制度")
    #e=uihandle.upload('上传正文按钮','e:\\央行报告.docx')

    #重新设置一下保密年限，是因为上面的拟密窗体弹出后，会将上传按钮位置向下挤出有效显示区域，使得上传按钮调用失败，
    uihandle.moveTo('保密年限')
    #uihandle.selectOrg('主送选择','慧点科技')
    #uihandle.selectOrg('抄送选择','慧点科技')
    #uihandle.selectPerson('发送领导选择','宋金超')
    
    uihandle.Input('公文标题', "公文（自动测试）%s" % time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())) )
    
    uihandle.Click('公文关闭按钮')
    alt=uihandle.driver.switch_to_alert()
    alt.accept()
    
    sleep(10)
 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    

#进入发文视图
def gongwen_enterFawenView(test,uihandle):
    #显示公文菜单
    menu=uihandle.moveTo('公文管理根菜单')

    #等待菜单显示完全
    sleep(10)

    #截图验证
    uihandle.save_screenshot('./screenshot/显示公文菜单.png')
    #打开总部发文
    uihandle.Click('慧点科技发文菜单项')
    
    
    #检查breadcrum是否正确，验证页面，因为新建按钮太常见了
    crumbs=uihandle.elements("",'面包屑')
    for c in crumbs:
        test.assertTrue(c.text in ['公文管理/'.decode('gbk'),'发文/'.decode('gbk'),'慧点科技发文'.decode('gbk')])

#进入发文视图，检查指定文档
def check_gongwen_view_Doc(test,uihandle,docTitle):
    #显示公文菜单
    menu=uihandle.moveTo('公文管理根菜单')

    #等待菜单显示完全
    sleep(5)

    #截图验证
    #uihandle.save_screenshot('./screenshot/显示公文菜单.png')
    #打开总部发文
    uihandle.Click('慧点科技发文菜单项')
    
    
    #检查breadcrum是否正确，验证页面，因为新建按钮太常见了
    crumbs=uihandle.elements("",'面包屑')
    for c in crumbs:
        test.assertTrue(c.text in ['公文管理/'.decode('gbk'),'发文/'.decode('gbk'),'慧点科技发文'.decode('gbk')])
    view = View(uihandle)
    test.assertTrue(view.isTabActivated('草稿'))
    #移动一下鼠标，使得弹出菜单消失，避免遮挡处理中页签，使得切换失败
    uihandle.moveTo('公文新建按钮')
    
    view.switchToViewTab('处理中')

    test.assertTrue(view.isDocInView(docTitle))
    
    view.clickDocInView(docTitle)
    
    sleep(10)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)

    #检查完毕后，关闭该文档
    uihandle.Click('公文关闭按钮')
    alt=uihandle.driver.switch_to_alert()
    alt.accept()
    
    sleep(10)
 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    

#进入发文视图，检查指定文档
def aqkkoa_gongwen_fawen_next(test,uihandle,docTitle,next='',opinion=''):
    #显示公文菜单
    menu=uihandle.moveTo('公文管理根菜单')

    #等待菜单显示完全
    sleep(5)

    #截图验证
    #uihandle.save_screenshot('./screenshot/显示公文菜单.png')
    #打开总部发文
    uihandle.Click('慧点科技发文菜单项')
    
    sleep(3)
    
    #检查breadcrum是否正确，验证页面，因为新建按钮太常见了
    crumbs=uihandle.elements("",'面包屑')
    for c in crumbs:
        test.assertTrue(c.text in ['公文管理/'.decode('gbk'),'发文/'.decode('gbk'),'慧点科技发文'.decode('gbk')])
    view = View(uihandle)
    test.assertTrue(view.isTabActivated('草稿'))
    #移动一下鼠标，使得弹出菜单消失，避免遮挡处理中页签，使得切换失败
    uihandle.moveTo('系统登出按钮')
    
    view.switchToViewTab('处理中')

    test.assertTrue(view.isDocInView(docTitle))
    
    view.clickDocInView(docTitle)
    
    sleep(10)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    
    #填写意见
    if (opinion!=''):
        uihandle.Input('意见框',opinion)
        
        
    #处理下一环节
    n_a = next.split('|')
    if(len(n_a)==1):
        #没有分支选择，直接选用户
        transition=''
        nextAssignee = n_a[0]
    else:
        transition = n_a[0]
        nextAssignee = n_a[1]
    
    if (transition!=''):
        uihandle.selectTransition(transition)
    if (nextAssignee!=''):
        uihandle.assignee(nextAssignee)
    
    sleep(2)

    #提交
    uihandle.Click('公文提交按钮')
    
    sleep(10)
 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
    
#最后一个环节，需要额外处理提示窗
def aqkkoa_gongwen_fawen_end(test,uihandle,docTitle,next='',opinion=''):
    #显示公文菜单
    menu=uihandle.moveTo('公文管理根菜单')

    #等待菜单显示完全
    sleep(5)

    #截图验证
    #uihandle.save_screenshot('./screenshot/显示公文菜单.png')
    #打开总部发文
    uihandle.Click('慧点科技发文菜单项')
    
    
    #检查breadcrum是否正确，验证页面，因为新建按钮太常见了
    crumbs=uihandle.elements("",'面包屑')
    for c in crumbs:
        test.assertTrue(c.text in ['公文管理/'.decode('gbk'),'发文/'.decode('gbk'),'慧点科技发文'.decode('gbk')])
    view = View(uihandle)
    test.assertTrue(view.isTabActivated('草稿'))
    #移动一下鼠标，使得弹出菜单消失，避免遮挡处理中页签，使得切换失败
    uihandle.moveTo('系统登出按钮')
    
    view.switchToViewTab('处理中')

    test.assertTrue(view.isDocInView(docTitle))
    
    view.clickDocInView(docTitle)
    
    sleep(10)
    
    #切换到新窗口
    uihandle.switchWindow(docTitle)
    
    #填写意见
    if (opinion!=''):
        uihandle.Input('意见框',opinion)
        
        
    #处理下一环节
    n_a = next.split('|')
    if(len(n_a)==1):
        #没有分支选择，直接选用户
        transition=''
        nextAssignee = n_a[0]
    else:
        transition = n_a[0]
        nextAssignee = n_a[1]
    
    if (transition!=''):
        uihandle.selectTransition(transition)
    if (nextAssignee!=''):
        uihandle.assignee(nextAssignee)
    
    sleep(2)

    #提交
    uihandle.Click('公文提交按钮')
    
    sleep(10)

    #需要处理额外的确认窗口（'别忘记发文'）
    alt=uihandle.driver.switch_to_alert()
    alt.accept()
    
    sleep(1)

 
    #需要手动关闭一下driver对应的窗体句柄，不然driver会报错Unable to locate window
    uihandle.closeWindow()
        
    
    
    