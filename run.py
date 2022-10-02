#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
import os
import shutil
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from tkinter.messagebox import askyesno, showerror
from tkinter import ttk
from tkinter.ttk import Separator
import time
import detect


# In[2]:


def resize(w_box, h_box, pil_image):
    w, h=pil_image.size
    f1=1.*w_box/w
    f2=1.*h_box/h
    factor=min([f1,f2])
    width=int(w*factor)
    height=int(h*factor)
    return pil_image.resize((width, height), Image.Resampling.LANCZOS)#LANCZOS


# In[3]:


def resize2(image):
    raw_width, raw_height=image.size[0], image.size[1]
    max_width, max_height=1280, 640
    min_height=min(max_height, raw_height)
    min_width=int(raw_width*min_height/raw_height)
    if min_width>max_width:
        min_width=min(max_width, raw_width)
        min_height=int(raw_height*min_width/raw_width)
    return image.resize((min_width, min_height))


# In[4]:


def sc_mid(scW,scH):
    w=int(scW/1.35)#1280
    h=int(scH/1.3)
    x=int((scW-w)/2)
    y=int((scH-h)/2)
    return (w,h,x,y)


# In[5]:


def cv_imread(filePath):
    cv_img=cv2.imdecode(np.fromfile(filePath,dtype=np.uint8),cv2.IMREAD_COLOR)
    return cv_img


# In[6]:


def clear_detect():
    for f in os.listdir('./det_res'):
        os.remove(os.path.join('./det_res',f))


# In[7]:


def list2tuple(data):
    out=data
    a=()
    for i in out:
        a=(*a,i.split('/')[-1])
    return a


# In[8]:


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('餐食照片營養素分析系統')
        self.a=sc_mid(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.root.geometry('%dx%d+%d+%d'% self.a)
        self.root.resizable(True,True)
        self.root.configure(bg='paleturquoise')
        self.root.iconbitmap('./GUI/img/icon.ico')
        self.frame=tk.Frame(self.root,bg='paleturquoise')
        self.frame2=tk.Frame(self.root, relief='groove', borderwidth=5)#, width=1280, height=640
        self.frame2.pack_propagate(0)
        self.frame3=tk.Frame(self.root, bg='paleturquoise',width=50, height=50)#status bar
        self.frame3.pack_propagate(0)
        #root.configure(bg='#ADD8E6')#87CEEB
        self.bar_text="""餐食照片營養素分析系統"""
        self.bar_pic=ImageTk.PhotoImage(file='./GUI/img/ai-logo.png')
        self.import_btn=ImageTk.PhotoImage(file='./GUI/img/import.png')
        self.go_btn=ImageTk.PhotoImage(file='./GUI/img/go.png')
        self.off_btn=ImageTk.PhotoImage(file='./GUI/img/off.png')
        self.save_btn=ImageTk.PhotoImage(file='./GUI/img/save.png')
        self.left_btn=ImageTk.PhotoImage(file='./GUI/img/left.png')
        self.right_btn=ImageTk.PhotoImage(file='./GUI/img/right.png')
        self.saveall_btn=ImageTk.PhotoImage(file='./GUI/img/save_all.png')
        self.all_btn=ImageTk.PhotoImage(file='./GUI/img/all.png')
        
        self.pic_index=tk.IntVar()
        self.pic_index.set(0)
        self.res_exist=tk.BooleanVar()
        self.pic_exist=tk.BooleanVar()
        self.pic_exist.set(0)
        self.res_exist.set(0)
        self.pic_status_text=tk.StringVar()
        self.pic_status_text.set('')
        self.combovar=tk.StringVar()
        self.root_name=tk.StringVar()
        self.status_txt=tk.StringVar()
        self.status_txt.set('已就緒')
        
        self.lb=tk.Label(self.frame,text=self.bar_text, image=self.bar_pic, font='微軟正黑體 20 bold', compound='left', bg='paleturquoise').grid(row=0, column=0, sticky='nw', padx=6)
        self.B1=tk.Button(self.frame, text='匯入圖片', image=self.import_btn, compound='left', command=self.oas, bg='paleturquoise', bd=1).grid(row=0, column=1, sticky='nw', padx=5)
        self.B2=tk.Button(self.frame, text="單張辨識", image=self.go_btn, compound='left', command=self.process, bg='paleturquoise',bd=1).grid(row=0, column=2, sticky='nw', padx=5)
        self.B8=tk.Button(self.frame, text="全部辨識", image=self.all_btn, compound='left', command=self.process_all, bg='paleturquoise',bd=1).grid(row=0, column=3, sticky='nw', padx=5)
        self.B4=tk.Button(self.frame, text="儲存結果", image=self.save_btn, compound='left', command=self.save_result, bg='paleturquoise',bd=1).grid(row=0, column=4, sticky='nw', padx=5)
        self.B7=tk.Button(self.frame, text="全部儲存", image=self.saveall_btn, compound='left', command=self.save_ALL, bg='paleturquoise',bd=1).grid(row=0, column=5, sticky='nw', padx=5)
        self.B3 =tk.Button(self.frame, text="退出程式", image=self.off_btn, compound='left', command=self.logout, bg='paleturquoise',bd=1).grid(row=0, column=6, sticky='nw', padx=5)
        self.progress=ttk.Progressbar(self.frame, length=120, mode='determinate')
        self.frame.pack(anchor='nw', pady=(5,0))
        
        self.video=tk.Label(self.frame2, padx=1, pady=1)
        self.video.pack(anchor='center', pady=10)
        
        self.status=tk.Button(self.frame3, textvariable=self.status_txt, relief='groove', bg='deepskyblue', width=15, height=3, font='微軟正黑體 12 bold', command=self.result_info)
        self.status.pack(side='left', anchor='nw')
        self.pic_status=tk.Label(self.frame3,textvariable=self.pic_status_text, bg='paleturquoise', width=10, font=('微軟正黑體', 10, 'bold'))
        self.pic_status.pack_propagate(0)
        self.pic_status.pack(side='left', anchor='nw', padx=(355,0), pady=(29,0), ipadx=15)
        self.B5=tk.Button(self.frame3, text="上一張",  width=10, command=self.prev_photo, bg='paleturquoise').pack(side='left', anchor='nw', pady=(29,0))
        self.combo=ttk.Combobox(self.frame3, height=100, width=60, textvariable=self.combovar)
        self.combo.bind('<<ComboboxSelected>>', self.comboSel)
        
        self.combo.pack(side='left', anchor='nw', pady=(29,0))
        self.B6=tk.Button(self.frame3, text="下一張", compound='left', width=10, command=self.next_photo, bg='paleturquoise').pack(side='left', anchor='nw', pady=(30,0))
        
        
        self.frame3.pack(fill='x',pady=(20,0))#2 toolbar
        self.frame2.pack(fill='both', expand=1)#pic area pack
        self.root.mainloop()
        
    def show_img(self, path):
        img=Image.open(path)
        img_resize=resize2(img)
        imgtk = ImageTk.PhotoImage(image=img_resize)
        self.video.imgtk = imgtk
        self.video.config(image=imgtk)
        
    def progressbar(self):
        self.progress['value']=0
        self.progress['maximum']=len(name_list)-1
        self.progress.grid(row=1, column=3, sticky='n')
        
    def prog_load(self, now):
        self.progress['value']=now
        self.frame.update()
        
    def logout(self):
        if askyesno('結束程式','確定要結束程式嗎?'):
            clear_detect()
            self.root.destroy()
            
    def show_valid(self, res):
        if type(res)==str:
            self.status_txt.set('已就緒')
            self.status.config(bg='deepskyblue')
        elif res[0]==1:
            self.status_txt.set('合格!')
            self.status.config(bg='limegreen')
        elif res[0]==-1: 
            self.status_txt.set('不合格!')
            self.status.config(bg='pink')
        
            
    def oas(self):
        index=self.pic_index.set(0)
        sfname = filedialog.askopenfilenames(title='選擇',
                                            filetypes=[("jpeg files","*.jpg"),
                                                ("jpeg files","*.jpeg"),
                                                ("png files","*.png"),
                                                ("gif files","*.gif")],
                                            initialdir='../')

        if sfname=='':
            return
        clear_detect()
        global name_list, eva_list
        name_list=sfname
        eva_list=list(sfname)
        s=name_list[0].split('/')[-1]#file name
        self.root_name.set(name_list[0].split(s)[0])
        self.combo['value']=list2tuple(sfname)
        self.combo.current(0)
        self.show_img(sfname[0])
        self.res_exist.set(0)
        self.pic_exist.set(1)
        self.pic_status_text.set(f'第{1}張，共{len(name_list)}張')
        self.show_valid(eva_list[0])
    
    def process(self):
        if self.pic_exist.get()==0:
            return
        self.status_txt.set('辨識中...')
        self.status.config(bg='yellow')
        time.sleep(1)
        index=self.pic_index.get()
        im, eva_list[index]=detect.exe([name_list[index]])
        self.show_img('./det_res/result.jpg')
        self.res_exist.set(1)
        im.tofile('./det_res/'+str(index)+'.jpg')
        self.show_valid(eva_list[index])

    def process_all(self):
        if self.pic_exist.get()==0:
            return
        length=len(name_list)
        self.status_txt.set('辨識中...')
        self.status.config(bg='yellow')
        self.progressbar()
        for i in range(length):
            im, eva_list[i]=detect.exe([name_list[i]])#self.picName.get()
            im.tofile('./det_res/'+str(i)+'.jpg')  
            self.prog_load(i)
        self.progress.grid_forget()
        self.show_img('./det_res/0.jpg')
        self.res_exist.set(1)
        self.pic_status_text.set(f'第{1}張，共{len(name_list)}張')
        self.pic_index.set(0)
        self.show_valid(eva_list[0])
    
    def save_result(self):
        index=self.pic_index.get()
        if self.res_exist.get()==0:
            return
        path=filedialog.asksaveasfilename(title='儲存結果', filetypes=[("jpeg files","*.jpg"),("png files","*.png"),("gif files","*.gif"),('All Files','*')], 
                                          defaultextension='.jpg', 
                                          initialdir='../', initialfile=name_list[index].split('/')[-1])#
        if path=='':
            return
        try:
            im=Image.open('./det_res/'+str(index)+'.jpg')
            im=im.save(path)
        except:
            showerror('錯誤','圖片儲存失敗!')
            
    def save_ALL(self):
        index=self.pic_index.get()
        if self.res_exist.get()==0:
            return
        path=filedialog.askdirectory(title='儲存全部結果', initialdir='../')
        if path=='':
            return
        try:
            os.remove('./det_res/result.jpg')
            for n in os.listdir('./det_res'):
                i=int(n.split('/')[-1].split('.')[0])
                shutil.copy('./det_res/'+n, path+'/'+name_list[i].split('/')[-1])
        except:
            showerror('錯誤','圖片儲存失敗!')
            
    def prev_photo(self):
        index=self.pic_index.get()
        if self.pic_exist.get()==0 or index==0:
            return 
        name='./det_res/'+str(index-1)+'.jpg' if os.path.isfile('./det_res/'+str(index-1)+'.jpg') else name_list[index-1]
        self.show_img(name)
        self.pic_index.set(index-1)
        self.combo.current(index-1)
        self.pic_status_text.set(f'第{index}張，共{len(name_list)}張')
        self.show_valid(eva_list[index-1])
    
    def next_photo(self):
        index=self.pic_index.get()
        if self.pic_exist.get()==0 or index>=len(name_list)-1: #0123 4
            return 
        name='./det_res/'+str(index+1)+'.jpg' if os.path.isfile('./det_res/'+str(index+1)+'.jpg') else name_list[index+1]
        self.show_img(name)
        self.pic_status_text.set(f'第{index+2}張，共{len(name_list)}張')
        self.pic_index.set(index+1)
        self.combo.current(index+1)
        self.show_valid(eva_list[index+1])
    
    def comboSel(self, event):
        path=self.root_name.get()+self.combovar.get()
        index=name_list.index(path)
        name='./det_res/'+str(index)+'.jpg' if os.path.isfile('./det_res/'+str(index)+'.jpg') else path
        self.show_img(name)
        self.pic_index.set(index)
        self.pic_status_text.set(f'第{index+1}張，共{len(name_list)}張')
        self.show_valid(eva_list[index])
        
    def result_info(self):
        if self.res_exist.get()==0:
            return
        self.window=tk.Toplevel(self.root)
        self.window.pack_propagate(0)
        self.window.title('營養標準')
        self.window.geometry(f'{500}x{200}+{self.a[2]*2}+{self.a[3]*4}')
        self.text100=tk.Label(self.window, font='標楷體 15 bold', justify='left', fg='black')
        self.b=tk.Button(self.window, text='OK', command=self.close_sub, relief='raised', bd=2, width=10).pack(anchor='s', side='bottom', pady=(0,10))
        self.text100.config(text='1.全榖雜糧類需大於39%。\n\n2.蔬菜類需大於8.6%。\n\n3.豆魚肉蛋類需大於17%。\n')
        self.text100.pack(anchor='n', side='bottom', pady=10)
    
    def close_sub(self):
        self.window.destroy()


# In[9]:


GUI()


# In[10]:


#!jupyter nbconvert --to script GUI-NEW.ipynb


# In[ ]:



