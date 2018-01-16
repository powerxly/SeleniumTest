#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-15 13:22
# function/function_01.py
# 业务功能脚本（用例脚本可调用此处的功能脚本）
import unicodedata

#from encapsulation.encapsulation import UIHandle
from encapsulation.smartdotoa import SmartHandle
#from constant.constant_01 import LOGIN_URL
from config.config_01 import browser_config
from time import sleep

from selenium.webdriver.common.action_chains import ActionChains as AC

# 打开博客园首页，进行找找看搜索功能
def search(msg):
    # 打开浏览器
    driver = browser_config['firefox']()
    # 传入driver对象
    uihandle = SmartHandle(driver)
    #输入url地址
    #uihandle.get(LOGIN_URL)
    uihandle.openSite("博客园")

    # 调用二次封装后的方法，此处可见操作了哪个页面，哪个元素，msg是要插入的值，插入值的操作在另外一个用例文件中传入
    uihandle.Input('找找看输入框', msg)
    uihandle.Click('找找看按钮')
    
    #uihandle.Input('博客园首页'.decode('gbk'), '找找看输入框'.decode('gbk'), msg)
    #uihandle.Click('博客园首页'.decode('gbk').encode('utf-8'), '找找看按钮'.decode('gbk').encode('utf-8'))
    '''
    uihandle.Input('index', 'input', msg)
    uihandle.Click('index', 'button')
    '''
    uihandle.quit()
    

def aqkkoa_init():
    # 打开浏览器
    driver = browser_config['firefox']()
    # 传入driver对象
    uihandle = SmartHandle(driver)
    return uihandle
def aqkkoa_login(uihandle,username,pwd):
    #输入url地址
    #uihandle.get(LOGIN_URL)
    uihandle.openSite("aqkkoa")
    
    sleep(5)

    # 调用二次封装后的方法，此处可见操作了哪个页面，哪个元素，msg是要插入的值，插入值的操作在另外一个用例文件中传入
    #uihandel.openPage("登陆页")
    uihandle.Input('登陆页密码输入框', pwd)
    uihandle.Input('登陆页用户名输入框', username)
    uihandle.Click('登陆页登录按钮')
    
def aqkkoa_gongwen(test,uihandle):
    sleep(30)
    #显示公文菜单
    menu=uihandle.moveTo('公文管理根菜单')

    sleep(10)

    uihandle.driver.save_screenshot('./screenshot/abc1.png')
    #打开总部发文
    uihandle.Click('总部发文菜单项')
    
    
    #检查breadcrum是否正确，验证页面，因为新建按钮太常见了
    crumbs=uihandle.elements("",'面包屑')
    for c in crumbs:
        test.assertTrue(c.text in ['公文管理/'.decode('gbk'),'发文/'.decode('gbk'),'总部发文'.decode('gbk')])
    #新建流程
    
    #oa弹出的菜单层似乎会影响新建按钮的触发，移动一下鼠标，使菜单层消失，就没问题了
    uihandle.moveTo('公文新建按钮')
    sleep(5)
    e=uihandle.Click('公文新建按钮')
    sleep(5)
    
    #切换到新窗口
    uihandle.switchWindow("")
    #sleep(15)
    uihandle.select('密级选项','秘密')
    uihandle.Input('保密年限', "5")
    uihandle.select('文种','意见')
    #uihandle.Click('主送选择')
   
    uihandle.Click('拟定密按钮')
    uihandle.Click('拟定密之普密选项')
    sleep(10)
    uihandle.tableRowClick('拟定密明细表','内部非密传阅制度')
    uihandle.Click('拟定密确定按钮')
    
    #重新设置一下保密年限，是因为上面的拟密窗体弹出后，会将上传按钮位置向下挤出有效显示区域，使得上传按钮调用失败，
    uihandle.moveTo('保密年限')
    #uihandle.Input('保密年限', "4")
    #uihandle.switchWindow("")
    e=uihandle.upload('上传正文按钮','e:\\央行报告.docx')

    #重新设置一下保密年限，是因为上面的拟密窗体弹出后，会将上传按钮位置向下挤出有效显示区域，使得上传按钮调用失败，
    uihandle.moveTo('保密年限')
    uihandle.selectOrg('主送选择','慧点科技')
    uihandle.selectOrg('抄送选择','慧点科技')
    '''sleep(25)
    newdoc=uihandle.driver.find_element_by_id('btnCreateOaDispatchDoc')
    print(newdoc.text)
    newdoc.click()'''
    #uihandle.quit()