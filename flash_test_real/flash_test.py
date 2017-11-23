#coding=utf-8
import subprocess
import threading
from Tkinter import *
import xlwt
import os
import time
import logging
import traceback

read=[]
write=[]
read_write=[]

file_path=os.path.abspath(sys.argv[0])  
path_list=file_path.split('\\')
path_list.pop()
path='\\'.join(path_list)


path=path+'\\result\\'
log_path=path+'\\'

log_path=unicode(log_path,"gb2312")
path=unicode(path,"gb2312")

if not os.path.exists(path): os.makedirs(path)
if not os.path.exists(log_path): os.makedirs(log_path)

def createlogger(name): 
    """Create a logger named specified name with the level set in config file.
    """   
    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    fh = logging.FileHandler(log_path+"\\flash_test.txt")
    #ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d: [%(levelname)s] [%(name)s] [%(funcName)s] %(message)s',
        '%y%m%d %H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def log_traceback(traceback):
    """print traceback information with the log style.
     
    """
    str_list = traceback.split("\n")
    for string in str_list:
        logger.warning(string)   
    
logger = createlogger("flash_test_real")



class Flash(threading.Thread):

    def __init__(self, threadID,device,test_type,log_name,file_list,buffer_list,app):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.device=device
        self.test_type=test_type
        self.logger = createlogger(log_name)
        self.file_list=file_list
        self.buffer_list=buffer_list
        self.app=app


    def creat_file(self, file_size):

        subprocess.call('adb -s %s push D:\\flash_test_file\\test%sM.rar /sdcard/test.db'%(self.device,file_size),shell=True)
        self.app.text_msglist.insert(END, 'creat file \n', 'green')
        self.logger.info("creat file")


    def delete_file(self):

        subprocess.call('adb -s %s shell rm -f /sdcard/test.db'%self.device,shell=True)
        subprocess.call('adb -s %s shell rm -f /sdcard/test2.db'%self.device,shell=True)
        self.app.text_msglist.insert(END, 'delete file \n', 'green')
        self.logger.info("delete file")
         
    def read_cmd(self, buffer_size):

        cmd='adb -s %s shell time dd if=/sdcard/test.db of=/dev/null bs=%s'%(self.device,buffer_size)
        return cmd

    def write_cmd(self, buffer_size, file_size):

        count=file_size*1024*1024/buffer_size
        
        cmd='adb -s %s shell time dd if=/dev/zero of=/sdcard/test.db bs=%s count=%s'%(self.device,buffer_size,count)
        return cmd

    def read_write_cmd(self, buffer_size):

        cmd='adb -s %s shell time dd if=/sdcard/test.db of=/sdcard/test2.db bs=%s'%(self.device,buffer_size)
        return cmd

    def get_speed(self, cmd):

        info=subprocess.check_output(cmd,shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        index1=info.index('(')
        index2=info.index(')')
        speed_info=info[index1+1:index2-10]
        self.logger.info(speed_info)
        speed=round(float(speed_info)/1024,3)
        return speed

    def read_speed(self,buffer_size,file_size):
        summation = 0
        self.app.text_msglist.insert(END,'file_size:%sM  buffer_size:%s \n'% (file_size, buffer_size),'green')
        self.creat_file(file_size)
        for i in range(3):
            read_speed=self.get_speed(self.read_cmd(buffer_size))
            self.app.text_msglist.insert(END,'read_speed:%skb/s \n'%read_speed, 'blue')
            self.logger.info('read_speed:%skb/s \n'%read_speed)
            read.append(read_speed)
            summation += read_speed
        self.delete_file()
        avg_speed = round(summation / 3, 3)
        read.append(avg_speed)
        self.app.text_msglist.insert(END, 'average_speed:%skb/s \n\n' % avg_speed, 'purple')
        self.app.text_msglist.see(END)
        self.logger.info('average_speed:%skb/s'%avg_speed)

    def write_speed(self,buffer_size,file_size):
        summation = 0
        self.app.text_msglist.insert(END, 'file_size:%sM  buffer_size:%s \n' % (file_size, buffer_size), 'green')
        for i in range(3):
            write_speed=self.get_speed(self.write_cmd(buffer_size,file_size))
            self.app.text_msglist.insert(END, 'write_speed:%skb/s \n'%write_speed, 'blue')
            self.logger.info('write_speed:%skb/s \n'%write_speed)
            write.append(write_speed)
            summation += write_speed
            self.delete_file()
        avg_speed = round(summation / 3, 3)
        write.append(avg_speed)
        self.app.text_msglist.insert(END, 'average_speed:%skb/s \n\n' % avg_speed, 'purple')
        self.app.text_msglist.see(END)
        self.logger.info('average_speed:%skb/s' % avg_speed)

    def read_write_speed(self,buffer_size,file_size):
        summation = 0
        self.app.text_msglist.insert(END, 'file_size:%sM  buffer_size:%s \n' % (file_size, buffer_size), 'green')
        self.logger.info('file_size:%sM  buffer_size:%s \n' % (file_size, buffer_size))
        for i in range(3):
            self.creat_file(file_size)
            read_write_speed=self.get_speed(self.read_write_cmd(buffer_size))
            self.app.text_msglist.insert(END, 'read_write_speed:%skb/s \n'%read_write_speed, 'blue')
            self.logger.info('read_write_speed:%skb/s'%read_write_speed)
            read_write.append(read_write_speed)
            summation += read_write_speed
            self.delete_file()
        avg_speed = round(summation / 3, 3)
        read_write.append(avg_speed)
        self.app.text_msglist.insert(END, 'average_speed:%skb/s \n\n' % avg_speed, 'purple')
        self.logger.info('average_speed:%skb/s ' % avg_speed)
        self.app.text_msglist.see(END)

    def write_xls(self):
        w = xlwt.Workbook(encoding='utf-8')
        ws = w.add_sheet('result', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        fnt = xlwt.Font()
        fnt.name = 'Arial'
        fnt.height = 210
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        style.font = fnt
        style.alignment = alignment
        col0 = ws.col(0)
        col1 = ws.col(1)
        col2 = ws.col(2)
        col3 = ws.col(3)
        col4 = ws.col(4)
        col5 = ws.col(5)
        col0.width = col1.width = 256 * 20
        col2.width = col3.width = col4.width = col5.width = 256 * 15
        title = [u'文件大小(MB)', u'每次读写大小(kb)', u'第一次', u'第二次', u'第三次', u'平均值']
        l1 = len(self.file_list)
        l2 = len(self.buffer_list)
        length = l1 * l2
        ws.write_merge(0, 0, 0, 5, u'读速度(kb/sec)', style)
        ws.write_merge(length + 2, length + 2, 0, 5, u'写速度(kb/sec)', style)
        ws.write_merge(2 * length + 4, 2 * length + 4, 0, 5, u'读写速度(kb/sec)', style)
        # 绘制表格
        for i in [1, length + 3, 2 * length + 5]:
            for j in range(6):
                ws.write(i, j, title[j], style)

        for k in [2, length + 4, 2 * length + 6]:
            for l in range(l1):
                for b in self.buffer_list:
                    ws.write(k, 0, self.file_list[l], style)
                    ws.write(k, 1, b, style)
                    k = k + 1

        # 写入结果数据
        def save_r():
            for i in range(length):
                for j in range(4):
                    try:
                        ws.write(i + 2, j + 2, read[4 * i + j], style)
                    except IndexError:
                        return -1

        def save_w():
            for i in range(length + 2, 2 * length + 2):
                for j in range(4):
                    try:
                        ws.write(i + 2, j + 2, write[4 * (i - length - 2) + j], style)
                    except IndexError:
                        return -1

        def save_rw():
            for i in range(2 * length + 4, 3 * length + 4):
                for j in range(4):
                    try:
                        ws.write(i + 2, j + 2, read_write[4 * (i - 2 * length - 4) + j], style)
                    except IndexError:
                        return -1

        if self.test_type == u'只测读':
            save_r()
        elif self.test_type == u'只测写':
            save_w()
        elif self.test_type == u'只测读写':
            save_rw()
        else:
            save_r()
            save_w()
            save_rw()
        #date = time.strftime('-%Y-%m-%d-%H-%M', time.localtime(time.time()))
        #w.save(path + self.device+date+'flash.xls')
        w.save(path + self.device+'_flash.xls')

    def run(self):
        read[:]=[]
        write[:]=[]
        read_write[:]=[]
        try:
            for file_size in self.file_list:
                #self.creat_file(file_size)
                for buffer_size in self.buffer_list:
                    buffer_size= buffer_size*1024
                    if self.test_type==u'只测读':
                        self.read_speed(buffer_size,file_size)
                    elif self.test_type==u'只测写':
                        self.write_speed(buffer_size,file_size)
                    elif self.test_type==u'只测读写':
                        self.read_write_speed(buffer_size,file_size)
                    else:
                        self.read_speed(buffer_size,file_size)
                        self.write_speed(buffer_size,file_size)
                        self.read_write_speed(buffer_size,file_size)
                    self.write_xls()  
                #self.delete_file()
            self.write_xls()
        except Exception,e:
            log_traceback(traceback.format_exc())
            self.app.text_msglist.insert(END, traceback.format_exc(),'red')
            self.write_xls()
        self.app.text_msglist.insert(END,u'测试完成,数据已保存在结果目录\n','green')
        self.logger.info(u'测试完成,数据已保存在结果目录')
        self.app.b1.config(state='normal')

    
