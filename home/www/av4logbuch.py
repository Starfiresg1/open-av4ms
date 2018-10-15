#!/usr/bin/env python
#-*-coding: utf-8 -*-

import time

class Logbuch:
    
    def __init__(self):
        self.initial = True
        self.logbuch = ''
        self.lastmsg = ''
        self.lastdate = ''
        
    def update(self,msg):
        if msg == None or msg == '' or msg == self.lastmsg: return
    
        datum = time.strftime('-- %x --\n')
        if datum != self.lastdate:
            self.logbuch += datum
            self.lastdate = datum
            
        zeit = time.strftime('%H:%M')
        log = "[{:s}] {:s}\n".format(zeit,msg)
        self.logbuch += log
        self.lastmsg = msg
        self.initial = False
        
    def clear(self):
        if self.initial: return
        self.__init__()
        