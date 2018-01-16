#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017-05-17 11:19
# log/log.py

import logging
import logging.handlers
import sys,os

_srcfile=__file__.lower().replace('.pyc','.py')
def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        #print(dir(sys.exc_info()[2].tb_frame))
        return sys.exc_info()[2].tb_frame.f_back
def findCaller():
    #由于多包了一层log.py，导致log日志中都记载的是log.py，而不是调用该封装的程序，此处不去修改logging，用变通的方法实现(adapter的extra)
    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.
    """
    f = currentframe()
    #On some versions of IronPython, currentframe() returns None if
    #IronPython isn't run with -X:Frames.
    if f is not None:
        f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)"
    while hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        #print ('file:%s vs %s' % (filename,_srcfile))
        if filename == _srcfile:
            f = f.f_back
            continue
        rv = (co.co_filename, f.f_lineno, co.co_name)
        break
    return rv
class MyLoggerAdapter(logging.LoggerAdapter):
    #由于多包了一层log.py，导致log日志中都记载的是log.py，而不是调用该封装的程序，此处不去修改logging，用变通的方法实现(adapter的extra)

    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs["extra"] = self.extra
        return msg, kwargs

# 日志类
class Logger():
    LOG_FILE = 'mylogs.log'

    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler
    #fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s - %(ip)s'
    fmt = '%(asctime)s - %(myfilename)s:%(mylineno)s - %(myfuncName)s - %(message)s'

    formatter = logging.Formatter(fmt)   # 实例化formatter
    handler.setFormatter(formatter)      # 为handler添加formatter

    __logger = logging.getLogger('mylogs')    # 获取名为tst的logger
    __logger.addHandler(handler)           # 为logger添加handler
    __logger.setLevel(logging.DEBUG)
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    #console_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console_formatter = logging.Formatter('【%(levelname)s】%(message)s')
    console.setFormatter(console_formatter)
    # 将定义好的console日志handler添加到root logger
    logging.getLogger('').addHandler(console)
    
    extra_dict = {}
    logger = MyLoggerAdapter(__logger, extra_dict)
    
    def loginfo(self, message):
        filename, lineno, co_name = findCaller()
        #print("-file:%s\ncode:%s\nline:%s" % (filename,co_name,lineno))
        self.logger.info(message,extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})

    def logdebug(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.debug(message,extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
        
    def info(self, message):
        filename, lineno, co_name = findCaller()
        #print("-file:%s\ncode:%s\nline:%s" % (filename,co_name,lineno))
        self.logger.info(message,extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})

    def debug(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.debug(message,extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
    def warning(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.warning(message,extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
    def error(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.error(message,extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})
    def critical(self, message):
        filename, lineno, co_name = findCaller()
        self.logger.critical(message,extra={"myfilename":filename,"mylineno":lineno,"myfuncName":co_name})