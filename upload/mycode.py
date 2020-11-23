#backend.py 역할

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
from PIL import Image
import colorsys
import os
from io import BytesIO
from django.contrib.sites import requests

class GetImageColor():
    def __init__(self,imgurl): 
        self.imgurl = imgurl
        print(self.imgurl)
    
    #이미지 로드, 전처리
    def preprocess_image(self):
        #load image
        image = cv2.imread(os.path.join("."+self.imgurl))
        # resize (비율은 유지하면서 픽셀수는 128*128 로)
        scale_percent = (image.shape[0] * image.shape[1]) / (128*128) # percent of original size
        width = int(image.shape[1] / np.sqrt(scale_percent))
        height = int(image.shape[0] / np.sqrt(scale_percent))
        dim = (width, height) #비율 유지 모드
        image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
        #rgb mode
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #reshape
        image = image.reshape((image.shape[0] * image.shape[1], 3)) # height, width 통합
        return image

    #Kmeans clustering
    def get_kmeans(self):
        image = self.preprocess_image()

        #5개의 대표 색상 추출
        k = 5
        clt = KMeans(n_clusters = k)
        clt.fit(image)
        # print(image.shape)
        self.centeroid_histogram(clt)
        return clt
    
    # MeanShift Clustering
    def get_meanshift(self):
        image = self.preprocess_image()

        bandwidth = estimate_bandwidth(image, quantile=0.1, n_samples=200) #128*128에 이 파라미터가 적절한듯(조정)
        print(bandwidth)
        ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
        ms.fit(image)
        
        self.centeroid_histogram(ms)
        '''
        self.labels = ms.labels_
        self.cluster_centers = ms.cluster_centers_

        self.labels_unique = np.unique(self.labels)
        self.n_clusters_ = len(self.labels_unique)

        print("number of estimated clusters : %d" % self.n_clusters_)
        '''
        return ms
    

    def centeroid_histogram(self,clt):
        numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        (hist, _) = np.histogram(clt.labels_, bins=numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        # print(hist)
        self.plot_colors(hist,clt.cluster_centers_)
        return hist

    def plot_colors(self, hist, centroids):
        bar = np.zeros((50, 300, 3), dtype="uint8")
        startX = 0
        for (percent, color) in zip(hist, centroids):
            endX = startX + (percent * 300)
            cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),color.astype("uint8").tolist(), -1)
            startX = endX
        plt.figure()
        plt.axis('on')
        plt.imshow(bar)
        plt.savefig('./media/images/tempplot.png')
        return bar


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

    def recommend(self): #getKmeans의 output
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
    