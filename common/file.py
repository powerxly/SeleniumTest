# -*- coding: utf-8 -*-

import sys,os
pagePath='./SeleniumTest/config/sites'

def getFilesInDir(dir):
	path = os.listdir(dir)
	return path
def getIniFiles():
	lists=[]
	listdir=getFilesInDir(pagePath)
	for l in listdir:
		if l[-3:]=='ini':
			lists.append(l)
	return lists