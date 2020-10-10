import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from PIL import Image
import colorsys
import os
from io import BytesIO
from django.contrib.sites import requests
from iteration_utilities import unique_everseen

class GetImageColor():
    def __init__(self,imgurl): 
        self.imgurl = imgurl
        print(self.imgurl)

    def getClt(self):
        image = cv2.imread(os.path.join("."+self.imgurl))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image.reshape((image.shape[0] * image.shape[1], 3)) # height, width 통합

        #5개의 대표 색상 추출
        k = 5
        clt = KMeans(n_clusters = k)
        clt.fit(image)
        print(image.shape)
        
        return clt

class Recommendation():
    def __init__(self,clt,df):
        self.clt = clt
        self.df = df # crawling data 전체 list

    def revised_rgb_to_hsv(self,r,g,b):
        (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h *= 360
        s *= 100
        v *= 100
        return h, s, v

    def recommend(self): #getClt의 output
        df = self.df
        keyDict = {'title','imageurl'}
        df_analog = dict([(key, []) for key in keyDict])
        df_compl = dict([(key, []) for key in keyDict])
        df_mono = dict([(key, []) for key in keyDict])

        for i in range(1,4): 
            for center in self.clt.cluster_centers_:
                h,s,v = Recommendation.revised_rgb_to_hsv(self,center[0],center[1],center[2])
                h=int(h)
                s=int(s)
                v=int(v)
                print('h,s,v:',h,s,v) #여기 왜 두번나옴?
                '''
                비슷한 색감의 명화 추천
                # roomcolor_analog(비슷한 색감) : h는 +-30도(!=0) (AND) s는동일 v는 +-5 
                보색의 명화 추천
                # roomcolor_compl(보색): h는 +-180도 (AND) s와v는 +-5
                단색의 명화 추천
                # roomcolor_mono(단색) : h는 동일 (AND) s는 +-10, v는 고려하지 않음
                '''
                roomcolor_analog= []
                roomcolor_compl = []
                roomcolor_mono = []
                if i==1:
                    roomcolor_analog, roomcolor_compl, roomcolor_mono= self.case1(df,h,s,v)
                elif i==2:
                    roomcolor_analog, roomcolor_compl, roomcolor_mono= self.case2(df,h,s,v)
                else:
                    roomcolor_analog, roomcolor_compl, roomcolor_mono= self.case3(df,h,s,v)
                
                for j in roomcolor_analog:
                    if df[j].title not in df_analog['title']: #중복 제거 위한 if문
                        df_analog['title'].append(df[j].title) #유사색-추천받은 명화 '제목' list형식으로 append
                        df_analog['imageurl'].append(df[j].imageurl)
                    # print("analog: ",df[j].title,"\n")
                for j in roomcolor_compl:
                    if df[j].title not in df_compl['title']: #중복 제거 위한 if문
                        df_compl['title'].append(df[j].title)  #보색-추천받은 명화 '제목' list형식으로 append
                        df_compl['imageurl'].append(df[j].imageurl) 
                    # print("compl: ",df[j].title,"\n")
                for j in roomcolor_mono:
                    if df[j].title not in df_mono['title']: #중복 제거 위한 if문
                        df_mono['title'].append(df[j].title)  #단색-추천받은 명화 '제목' list형식으로 append
                        df_mono['imageurl'].append(df[j].imageurl) 
                    # print("mono: ",df[j].title,"\n")
        return df_analog,df_compl,df_mono

    def case1(self,df,h,s,v): #h1,s1,v1
        roomcolor_analog= []
        roomcolor_compl = []
        roomcolor_mono = []

        for idx in range(0,len(df)):
            if (abs(df[idx].h1-h)!=0)&(abs(df[idx].h1-h)<=30)&(abs(df[idx].s1-s)==0)&(abs(df[idx].v1-v)<=5):
                roomcolor_analog.append(idx)
                # print('analog',idx)
            if (abs(df[idx].h1-h)==180)&(abs(df[idx].s1-s)<=5)&(abs(df[idx].v1-v)<=5):
                roomcolor_compl.append(idx)
                # print('compl',idx)
            if (df[idx].h1==h)&(abs(df[idx].s1-s)<=10):
                roomcolor_mono.append(idx)
                # print('mono',idx)
        return roomcolor_analog, roomcolor_compl, roomcolor_mono

    def case2(self,df,h,s,v): #h2,s2,v2
        roomcolor_analog= []
        roomcolor_compl = []
        roomcolor_mono = []

        for idx in range(0,len(df)):
            if (abs(df[idx].h2-h)!=0)&(abs(df[idx].h2-h)<=30)&(abs(df[idx].s2-s)==0)&(abs(df[idx].v2-v)<=5):
                roomcolor_analog.append(idx)
                # print('analog',idx)
            if (abs(df[idx].h2-h)==180)&(abs(df[idx].s2-s)<=5)&(abs(df[idx].v2-v)<=5):
                roomcolor_compl.append(idx)
                # print('compl',idx)
            if (df[idx].h2==h)&(abs(df[idx].s2-s)<=10):
                roomcolor_mono.append(idx)
                # print('mono',idx)
        return roomcolor_analog, roomcolor_compl, roomcolor_mono

    def case3(self,df,h,s,v): #h3,s3,v3
        roomcolor_analog= []
        roomcolor_compl = []
        roomcolor_mono = []

        for idx in range(0,len(df)):
            if (abs(df[idx].h3-h)!=0)&(abs(df[idx].h3-h)<=30)&(abs(df[idx].s3-s)==0)&(abs(df[idx].v3-v)<=5):
                roomcolor_analog.append(idx)
                # print('analog',idx)
            if (abs(df[idx].h3-h)==180)&(abs(df[idx].s3-s)<=5)&(abs(df[idx].v3-v)<=5):
                roomcolor_compl.append(idx)
                # print('compl',idx)
            if (df[idx].h3==h)&(abs(df[idx].s3-s)<=10):
                roomcolor_mono.append(idx)
                # print('mono',idx)
        return roomcolor_analog, roomcolor_compl, roomcolor_mono
    
    # def analog_result(self,df_analog,df_compl,df_mono):
    #     df = self.df
    #     analog_img_bytes = []
    #     print("유사색 출력 갯수 : ", len(df_analog['title']))
    #     print("유사색의 명화 추천 : ")
    #     for i in range(0,len(df_analog)):
    #         try:
    #             title = df_analog[i]['title'] 
    #             imageurl = df_analog[i]['imageurl'] 
    #             print('title:',title,'imageurl: ',imageurl)
    #             response = requests.get(imageurl)
    #             image_bytes = BytesIO(response.content)
    #             analog_img_bytes.append(image_bytes)
    #             img = Image.open(image_bytes)
    #             img.show()
    #         except:
    #             None
    #     print("="*50)
    #     return analog_img_bytes

    # def compl_result(self,df_compl):
    #     df = self.df
    #     compl_img_bytes = []
    #     print("\n보색의 명화 추천 : ")
    #     for i in range(0,len(df_compl)):
    #         try:
    #             title = df_compl[i]['title'] 
    #             imageurl = df_compl[i]['imageurl'] 
    #             print('title:',title,'imageurl: ',imageurl)
    #             response = requests.get(imageurl)
    #             image_bytes = BytesIO(response.content)
    #             compl_img_bytes.append(image_bytes)
    #             # img = Image.open(compl_img_bytes)
    #             # img.show()
    #         except:
    #             None
    #     print("="*50)
    #     return compl_img_bytes

    # def mono_result(self,df_mono):
    #     df = self.df
    #     mono_img_bytes = []
    #     print("\n단색의 명화 추천 : ")
    #     for i in range(0,len(df_mono)):
    #         try:
    #             title = df_mono[i]['title'] 
    #             imageurl = df_mono[i]['imageurl'] 
    #             print('title:',title,'imageurl: ',imageurl)
    #             response = requests.get(imageurl)
    #             image_bytes = BytesIO(response.content)
    #             mono_img_bytes.append(image_bytes)
    #             # img = Image.open(mono_img_bytes)
    #             # img.show()
    #         except:
    #             None
    #     return mono_img_bytes