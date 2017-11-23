#coding=utf-8
from Tkinter import Toplevel
from ttk import *
import os
import tkFileDialog
import tkMessageBox
import flash_test
from Tkinter import *


def get_path(ico):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    base_path=unicode(base_path,"gb2312")
    return os.path.join(base_path, ico)


class Application(Frame):
    file_list=[]
    buffer_list=[]
    def __init__(self, master):
        Frame.__init__(self, master)
        self.root = master
        self.root.title('Flash Read/Write Test(v1.0.1,qing.guo)')
        self.root.geometry('750x400')
        self.root.resizable(0, 0)  # 禁止调整窗口大小
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.iconbitmap(get_path('flash.ico'))

    def creatWidgets(self):
        frame_left = Frame(self.root, width=400, height=400, bg='#C1CDCD')
        frame_right = Frame(self.root, width=350, height=400, bg='#C1CDCD')

        frame_left.grid_propagate(0)
        frame_right.propagate(0)
        frame_right.grid_propagate(0)

        frame_left.grid(row=0, column=0)
        frame_right.grid(row=0, column=1)

        self.v1 = StringVar()
        self.v2 = StringVar()
        self.v3 = StringVar()
        self.v4 = StringVar()
        self.v5 = StringVar()
        self.v5.set(flash_test.path)
        type_list = [u'只测读',u'只测写',u'只测读写',u'测试所有']

        Label(frame_left, text=u"选择设备id:",bg='#C1CDCD').grid(row=0, column=0, pady=20, padx=5)
        self.cb1 = Combobox(frame_left, width=25, textvariable=self.v1,postcommand=self.cb1_click)
        self.cb1.grid(row=0, column=1, ipady=1, padx=5, sticky=W)
        self.cb1.bind('<<ComboboxSelected>>', self.cb1_select)

        Label(frame_left, text=u"测试类型:",bg='#C1CDCD').grid(row=1, column=0, pady=20, padx=5)
        self.cb2 = Combobox(frame_left, width=25, textvariable=self.v2, values=type_list)
        self.cb2.grid(row=1, column=1, ipady=1, padx=5, sticky=W)
        self.cb2.current(3)

        Button(frame_left, text=u"设置文件大小:", command=self.set_file,bg='#C1CDCD').grid(row=2, column=0, pady=20, padx=5)
        e1=Entry(frame_left, width=38, textvariable=self.v3)
        e1.grid(row=2, column=1, ipady=1, padx=5, sticky=W)
        e1.bind("<KeyPress>",lambda e:"break")
        Button(frame_left, text=u"设置buffer大小:", command=self.set_buffer,bg='#C1CDCD').grid(row=3, column=0, pady=20, padx=5)
        e2=Entry(frame_left, width=38, textvariable=self.v4)
        e2.grid(row=3, column=1, ipady=1, padx=5, sticky=W)
        e2.bind("<KeyPress>", lambda e: "break")

        self.b1=Button(frame_left, text=u"开始测试", command=self.start_test,bg='#C1CDCD')
        self.b1.grid(row=4, column=0, padx=5, pady=15)
        self.b2=Button(frame_left, text=u"保存当前数据", command=self.save_data,bg='#C1CDCD')
        self.b2.grid(row=4, column=1, padx=5, pady=15)

        Button(frame_left, text=u"测试结果", command=self.open_file,bg='#C1CDCD').grid(row=5, column=0, padx=5, pady=15)
        Entry(frame_left, width=38, textvariable=self.v5).grid(row=5, column=1, ipady=1, padx=5, pady=15)

        scrollbar = Scrollbar(frame_right,bg='#C1CDCD')
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_msglist = Text(frame_right, yscrollcommand=scrollbar.set,bg='#C1CDCD')
        self.text_msglist.pack(side=RIGHT, fill=BOTH)
        scrollbar['command'] = self.text_msglist.yview
        self.text_msglist.tag_config('green', foreground='#008B00')
        self.text_msglist.tag_config('blue', foreground='#0000FF')
        self.text_msglist.tag_config('red', foreground='#FF3030')
        self.text_msglist.tag_config('purple', foreground='#CD00CD')
        
        self.text_msglist.insert(END,u'测试前将测试文件放在D:\\flash_test_file\文件夹中\n','purple')

        self.text_msglist.insert(END,u'文件命名规则为test1M.rar  test64M.rar  test1024M.rar等...\n','purple')
        self.text_msglist.insert(END,u'设置文件大小，根据文件夹中的实际文件大小(M)填写数字 ，如1,64,1024\n','purple')
        self.text_msglist.insert(END,u'设置buffer大小中填写 1,4,512,1024，自动会乘以1024...\n','purple')
    def cb1_click(self):
        device_list = os.popen('adb devices').readlines()
        self.cb1['values'] = device_list

    def cb1_select(self,event):
        v=self.v1.get()
        self.v1.set(v.split()[0])

    def start_test(self):
        device=self.v1.get()
        test_type=self.v2.get()
        if device == '' or device.isspace():
            self.text_msglist.insert(END, 'please input device id\n', 'red')
            return -1
        self.f1=flash_test.Flash(1,device,test_type,'flash_test',self.file_list,self.buffer_list,app)
        self.f1.setDaemon(True)
        self.f1.start()
        self.b1.config(state='disabled')

    def save_data(self):
        self.f1.write_xls()
        self.text_msglist.insert(END,u'当前数据已保存到Excel表格，继续测试\n','purple')

    def set_file(self):
        window = Toplevel(self,bg='#C1CDCD')
        window.title('set_file_size')
        window.geometry('400x400')
        window.resizable(0, 0)  # 禁止调整窗口大小

        file_num = 16
        var=[]
        for i in range(file_num):
            var.append(StringVar())
        Label(window, text=u"请填写需要生成的测试文件大小，单位M(无需填满):",bg='#C1CDCD').grid(row=0, column=0,columnspan=4, pady=5, padx=15)
        for j in range(file_num/2):
            Label(window, text=u"文件大小"+str(j*2)+":",bg='#C1CDCD').grid(row=j+1, column=0, pady=8, padx=10)
            Entry(window, width=10, textvariable=var[j*2]).grid(row=j+1,column=1,pady=8,padx=10)
            Label(window, text=u"文件大小"+str(j*2+1)+":",bg='#C1CDCD').grid(row=j+1, column=2, pady=8, padx=10)
            Entry(window, width=10, textvariable=var[j*2+1]).grid(row=j+1, column=3, pady=8, padx=10)

        def get_file_list():
            v3 = ''
            self.file_list[:] = []
            for k in range(file_num):
                v=var[k].get()
                if v=='' or v.isspace() or not v.isdigit():
                    continue
                else:
                    self.file_list.append(int(v))
            self.file_list=list(set(self.file_list))
            if 0 in self.file_list:
                self.file_list.remove(0)
            self.file_list.sort()
            for size in self.file_list:
                v3=v3+str(size)+'M'+','
            print v3
            self.v3.set(v3)
            window.destroy()
        Button(window, text=u"确定",width=20, command=get_file_list,bg='#C1CDCD').grid(row=file_num/2+2, column=0, columnspan=4,pady=8, padx=10)
        window.protocol("WM_DELETE_WINDOW", window.destroy)

    def set_buffer(self):
        window = Toplevel(self,bg='#C1CDCD')
        window.title('set_buffer_size')
        window.geometry('400x300')
        window.resizable(0, 0)  # 禁止调整窗口大小
        window.protocol("WM_DELETE_WINDOW", self.close)
        buffer_num = 10
        var=[]
        for i in range(buffer_num):
            var.append(StringVar())
        Label(window, text=u"请填写输入/输出块大小，单位k(无需填满)，代表每次读/写多少kb",bg='#C1CDCD').grid(row=0, column=0,columnspan=4, pady=5, padx=15)
        for j in range(buffer_num/2):
            Label(window, text=u"buffer_size "+str(j*2)+":",bg='#C1CDCD').grid(row=j+1, column=0, pady=8, padx=10)
            Entry(window, width=10, textvariable=var[j*2]).grid(row=j+1,column=1,pady=8,padx=10)
            Label(window, text=u"buffer_size "+str(j*2+1)+":",bg='#C1CDCD').grid(row=j+1, column=2, pady=8, padx=10)
            Entry(window, width=10, textvariable=var[j*2+1]).grid(row=j+1, column=3, pady=8, padx=10)

        def get_buffer_list():
            v4 = ''
            self.buffer_list[:] = []
            for k in range(buffer_num):
                v=var[k].get()
                if v=='' or v.isspace() or not v.isdigit():
                    continue
                else:
                    self.buffer_list.append(int(v))
            self.buffer_list=list(set(self.buffer_list))
            if 0 in self.buffer_list:
                self.buffer_list.remove(0)
            self.buffer_list.sort()
            for size in self.buffer_list:
                v4=v4+str(size)+'k'+','
            print v4
            self.v4.set(v4)
            window.destroy()
        Button(window, text=u"确定",width=20, command=get_buffer_list,bg='#C1CDCD').grid(row=buffer_num/2+2, column=0, columnspan=4,pady=8, padx=10)
        window.protocol("WM_DELETE_WINDOW", window.destroy)

    def open_file(self):
        filename = tkFileDialog.askopenfilename(initialdir=flash_test.path)
        if filename == '':
            return 0
        os.startfile(filename)

    def close(self):
        result = tkMessageBox.askokcancel(title=u"退出", message=u"确定退出程序? 请先保存测试数据!")
        if result:
            self.root.quit()
            self.root.destroy()


if __name__ == "__main__":

        root = Tk()
        app = Application(root)
        app.creatWidgets()
        app.mainloop()
