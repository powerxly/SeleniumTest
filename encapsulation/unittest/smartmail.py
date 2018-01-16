#!/usr/bin/python
# -*- coding: utf-8 -*-
import email
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import smtplib

class SmartMail(object):
    '''mail function used by smartdot testing
    '''
    def __init__(self,config={}):
        self.config = config
        
        self.readConfigs()
    def readConfigs(self):
        self.fromaddr = self.getConfig('fromaddr')
        self.toaddr = self.getConfig('toaddr')
        self.server = self.getConfig('server')
        self.username = self.getConfig('username')
        self.password = self.getConfig('password')
        self.subject = self.getConfig('subject')
        self.htmltext = self.getConfig('htmltext')
        self.plaintext = self.getConfig('plaintext')
        self.debuglevel = self.getConfig('debuglevel')
    def getConfig(self, para_name, default_value='',codebase='gbk'):
        cf = self.config
        if(cf.has_key(para_name)):
            v = cf[para_name]
        else:
            v = default_value
        if codebase!='':
            try:
                if(type(v)==str):
                    v = v.decode(codebase)
            except:
                pass
        return v
        
    def send(self,config={}):
        #将新输入的配置项合并，保存
        cf = dict(self.config,**config)
        self.config = cf
        self.readConfigs()
        
        strFrom = self.fromaddr
        
        if type(self.toaddr)==list:
            strTo = ', '.join(self.toaddr)
        else:
            strTo = self.toaddr
        
        server = self.server
        user = self.username
        
        passwd = self.password
        if not (server and user and passwd) :
            print 'incomplete login info, exit now'
            return
        # 设定root信息
        
        if not(strTo):
            print 'no receipt info, exit now'
            return
        
        msgRoot = MIMEMultipart('related')
        try:
            subject = self.subject.decode('gbk')
        except:
            subject = self.subject
        msgRoot['Subject'] = subject
        
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'
        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        #设定纯文本信息
        msgText = MIMEText(self.plaintext, 'plain', 'utf-8')
        msgAlternative.attach(msgText)
        #设定HTML信息
        msgText = MIMEText(self.htmltext, 'html', 'utf-8')
        msgAlternative.attach(msgText)
        #设定内置图片信息
        '''
        fp = open('./screenshot/显示公文菜单.png'.decode('gbk')), 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)
        '''
        #发送邮件
        smtp = smtplib.SMTP()
        #设定调试级别，依情况而定
        smtp.set_debuglevel(self.debuglevel)
        smtp.connect(server)
        smtp.login(user, passwd)
        smtp.sendmail(strFrom, strTo, msgRoot.as_string())
        smtp.quit()
        return  
