#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import torch
import pandas as pd    
import pickle
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
model = torch.hub.load("./yolov5-master","custom",path='./weight/0924/exp100/weights/best.pt',source='local', device='cpu')
model.conf = 0.35


# In[2]:


classes=['vegtable','rice','meat','fried meat']
cls2name={'vegtable':'蔬菜', 'rice':'全榖雜糧', 'meat':'豆魚肉蛋', 'fried meat':'豆魚肉蛋(高油)'}
colors=[(0,139,0),(19,69,139),(0,55,205),(160,32,240)]
meat_reg=pickle.load(open('./sav/meat_REG.sav','rb'))
oil_reg=pickle.load(open('./sav/oil_REG.sav','rb'))
rice_reg=pickle.load(open('./sav/rice_REG.sav','rb'))
veg_reg=pickle.load(open('./sav/veg_REG.sav','rb'))
heat_reg=pickle.load(open('./sav/heat_REG.sav','rb'))
reg=[veg_reg, rice_reg, meat_reg, oil_reg]


# In[3]:


def detect(path):
    results = model(path)
    res=results.pandas().xyxy[0].to_numpy()
    return res


# In[4]:


def get_area(data,x,y):
    result=np.zeros(5,dtype=float)
    result1=np.zeros(5,dtype=float)
    for obj in data:
        result[obj[-2]]+=((obj[3]-obj[1])/y)*((obj[2]-obj[0])/x)
    result1[0]=.0 if result[0]==.0 else veg_reg.predict([[result[0]]])[0]
    result1[2]=.0 if result[2]+result[3]==.0 else meat_reg.predict([[result[2]+result[3]]])[0]
    result1[1]=.0 if result[1]==.0 else rice_reg.predict([[result[1]]])[0]
    result1[3]=oil_reg.predict([[result[0],result[2],result[3]]])[0]
    result1[4]=heat_reg.predict([[result1[1],result1[2],result1[0],result1[3]]])[0] #'rice_num','meat_num','veg_num','oil_num'
    return result1


# In[5]:


def get_area_single(data,x,y):
    result=((data[3]-data[1])/y)*((data[2]-data[0])/x)
    return result


# In[6]:


def check_pass(res):
    if res[0]<39:
        return (-1, 0)
    elif res[1]<8:
        return (-1, 1)
    elif res[2]<17:
        return (-1, 2)
    else:
        return (1, 0)


# In[1]:


def draw(im, box, txt_color=(255,255,255)):#Arial.ttf
    y, x = im.shape[:2]
    font=ImageFont.truetype('./font/TaipeiSansTCBeta-Regular.ttf', max(round(sum(im.shape) / 2 * 0.02), 12))
    im0=Image.fromarray(im)
    draw = ImageDraw.Draw(im0)
    total_num=get_area(box,x,y)
    total_num_sum=total_num[:-1].sum()
    summary='全榖雜糧類: {}%\n蔬菜類: {}%\n豆魚肉蛋類: {}%\n油脂類: {}份\n熱量: {}大卡'.format(int(total_num[1]/total_num_sum*100), int(total_num[0]/total_num_sum*100),
                                                                                    int(total_num[2]/total_num_sum*100), round(total_num[3]/2, 1), int(total_num[4]))
                                                                   
    for data in box:
        cl=data[-1]
        box1=data[:-3]
        area=get_area_single(box1,x,y) 
        color=colors[data[-2]]
        cls_index=2 if cl=='fried meat' else classes.index(cl)
        value=round(reg[cls_index].predict([[area]])[0], 1) 
        value=round(value/3, 1) if data[-2]==1 else value
        label=cls2name[cl]+' '+str(value)+'份'
        p1, p2 = (int(box1[0]), int(box1[1])), (int(box1[2]), int(box1[3])) 
        lw= max(round(sum(im.shape) / 2 * 0.003), 2)
        draw.rectangle(box1, width=lw, outline=color)  # box
        if label:
            _ , _ , w, h = font.getbbox(label)  # text width, height
            outside = box1[1] - h >= 0  # label fits outside box
            draw.rectangle((box1[0],
                            box1[1] - h if outside else box1[1],
                            box1[0] + w + 1,
                            box1[1] + 1 if outside else box1[1] + h + 1), fill=color)
            draw.text((box1[0], box1[1] - h if outside else box1[1]), label, fill=txt_color, font=font)  
    font2 = ImageFont.truetype('./font/TaipeiSansTCBeta-Regular.ttf', max(round(sum(im.shape) / 2 * 0.025), 12))#70
    w1, h1 = font2.getsize_multiline(summary)
    draw.rectangle([(0,0), (w1+10,h1+10)], fill=(130,221,238))
    draw.text((0,0),summary,fill=(205,0,0), font=font2)
    return np.asarray(im0), check_pass([int(total_num[1]/total_num_sum*100), int(total_num[0]/total_num_sum*100),int(total_num[2]/total_num_sum*100)])


# In[8]:


def exe(get):
    name_list=[]
    path_list=get
    for i, name in enumerate(path_list):
        pic=cv2.imdecode(np.fromfile(name, dtype=np.uint8), cv2.IMREAD_COLOR)
        img, failed=draw(pic, detect(name).tolist())
        a=cv2.imencode('.jpg', img)[1]
        a.tofile('./det_res/result.jpg')
        #cv2.imwrite('./det_res/'+name.split('/')[-1], img)
    return a, failed


# In[9]:


#exe(['./AIGO_valid/images/370.jpg'])


# In[ ]:




