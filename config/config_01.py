#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-11 13:42
# config/config_01.py
from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import *
import json

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# config配置部分
def ie_init():
    #解决ie11兼容性问题，实际发现2.x版本存在 Unable to find element on closed window问题，按网上文章修改注册表也不管用，使用3.5.1版本后解决，但是保护模式开关等失效，而且需要禁掉多余的选项
    caps = DesiredCapabilities.INTERNETEXPLORER
    #delete platform and version keys
    caps.pop("platform", None)
    caps.pop("version", None)

    #caps['ignoreProtectedModeSettings'] = True
    #caps['IntroduceInstabilityByIgnoringProtectedModeSettings'] = True
    return webdriver.Ie(capabilities=caps)


# 浏览器种类维护在此处
'''
browser_config = {
    'ie': webdriver.Ie,
    'chrome': webdriver.Chrome,
    'firefox': webdriver.Firefox
}
'''
browser_config = {
    'ie': ie_init,
    'chrome': webdriver.Chrome,
    'firefox': webdriver.Firefox
}

# 定位信息维护在此处，维护结构由外到内为：页面名称--页面下元素名称--元素的定位方式+参数
'''
locat_config = {
    '博客园首页': {
        '找找看输入框': ['id', 'zzk_q'],
        '找找看按钮': ['xpath', '//input[@value="找找看"]']
    }
}
'''
encode_config = {
    '博客园首页': {
        '找找看输入框': ['id', 'zzk_q'],
        '找找看按钮': ['xpath', '//input[@value="找找看"]']
    }
}
locat_config = json.loads(json.dumps(encode_config,encoding='gbk'))

#TODO 定位信息应该从外部读取，例如目录结构下的excel或文本文件
'''
locat_config = {
    'index': {
        'input': ['id', 'zzk_q'],
        'button': ['xpath', '//input[@value="'+'找找看'.decode('gbk')+'"]']
    }
}

config = {
    'index': {
        'input': ['id', 'zzk_q'],
        'button': ['xpath', '//input[@value="找找看"]']
    }
}
locat_config = json.loads(json.dumps(config,encoding='gbk'))
'''
