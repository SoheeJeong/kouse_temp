#backend.py 역할

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import cv2
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
from PIL import Image
import colorsys
import os
from io import BytesIO
from django.contrib.sites import requests
from django.conf import settings

class GetImageColor():
    def __init__(self,imgurl,title): 
        self.imgurl = imgurl
        self.imgtitle = title
    
    #이미지 로드, 전처리
    def preprocess_image(self):
        #load image
        image = cv2.imread(os.path.join("."+self.imgurl))
        ## 밝기조절
        val=10
        array=np.full(image.shape,(val,val,val),dtype=np.uint8)
        image=cv2.add(image,array)
        
        ## rgb mode
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) 

        ## 선명하게
        # 커널 생성(대상이 있는 픽셀을 강조)
        kernel = np.array([[0, -1, 0],
                        [-1, 5, -1],
                        [0, -1, 0]])
        # 커널 적용 
        image = cv2.filter2D(image, -1, kernel)
       
        ## resize (비율은 유지하면서 픽셀수는 128*128 로)
        scale_percent = (image.shape[0] * image.shape[1]) / (128*128) # percent of original size
        width = int(image.shape[1] / np.sqrt(scale_percent))
        height = int(image.shape[0] / np.sqrt(scale_percent))
        dim = (width, height) #비율 유지 모드
        image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)   
        #reshape
        image = image.reshape((image.shape[0] * image.shape[1], 3)) # height, width 통합
        return image

    # Kmeans clustering
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
        num_labels = np.arange(0, len(np.unique(clt.labels_)) + 1)
        (hist, _) = np.histogram(clt.labels_, bins=num_labels)
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
        plt.savefig(settings.MEDIA_ROOT+self.imgtitle+'_cluster_result.png')
        return bar


class Recommendation():
    def __init__(self,clt,data):
        self.clt = clt
        self.data = data # crawling data 전체 list

    def revised_rgb_to_hsv(self,r,g,b):
        (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h *= 360
        s *= 100
        v *= 100
        return h, s, v

    def recommend_pic(self): #getKmeans의 output
        #convert tuple into dataframe
        df = pd.DataFrame(self.data, columns =['id','artist','title','h1','s1','v1','h2','s2','v2','h3','s3','v3','imageurl'])
        
        for i in range(1,4): 
            for center in self.clt.cluster_centers_:
                h,s,v = Recommendation.revised_rgb_to_hsv(self,center[0],center[1],center[2])
                h=int(h)
                s=int(s)
                v=int(v)

                """
                # 비슷한 색감의 명화 추천
                roomcolor_analog(비슷한 색감) : h는 +-30도(!=0) (AND) s는동일 v는 +-5 
                # 보색의 명화 추천
                roomcolor_compl(보색): h는 +-180도 (AND) s와v는 +-5
                # 단색의 명화 추천
                roomcolor_mono(단색) : h는 동일 (AND) s는 +-10, v는 고려하지 않음
                """
                roomcolor_analog= (abs(df['h'+str(i)]-h)!=0)&(abs(df['h'+str(i)]-h)<=30)&(abs(df['s'+str(i)]-s)==0)&(abs(df['v'+str(i)]-v)<=5)
                roomcolor_compl=(abs(df['h'+str(i)]-h)==180)&(abs(df['s'+str(i)]-s)<=5)&(abs(df['v'+str(i)]-v)<=5)
                roomcolor_mono=(df['h'+str(i)]==h)&(abs(df['s'+str(i)]-s)<=10)

                # 중복을 방지하기 위해 dictionary 로 바꿨다가 다시 list로 변환
                df_analog, df_compl, df_mono = [],[],[]     
                
                #유사색-추천받은 명화 list형식으로 append          
                df_analog={
                    'title': list( dict.fromkeys(df[roomcolor_analog]['title'].values,) ),
                    'imageurl': list( dict.fromkeys(df[roomcolor_analog]['imageurl'].values,) )
                    }  
                #보색-추천받은 명화 list형식으로 append  
                df_compl={
                    'title': list( dict.fromkeys(df[roomcolor_compl]['title'].values,) ),
                    'imageurl': list( dict.fromkeys(df[roomcolor_compl]['imageurl'].values,) )
                    }
                #단색-추천받은 명화 list형식으로 append  
                df_mono={
                    'title': list( dict.fromkeys(df[roomcolor_mono]['title'].values,) ),
                    'imageurl': list( dict.fromkeys(df[roomcolor_mono]['imageurl'].values,) )
                    }
                
        return df_analog,df_compl,df_mono
    