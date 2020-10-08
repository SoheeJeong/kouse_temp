import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from PIL import Image
import colorsys
import os

class MyClass():
    def __str__(self):
        return self.text
    def print_something(self):
        print('hello world')

class GetImageColor():
    def __str__(self):
        return self.text
    def getClt(self,imgurl):
        image = cv2.imread(os.path.join(imgurl))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image = image.reshape((image.shape[0] * image.shape[1], 3)) # height, width 통합
        print(image.shape)

        # 5개의 대표 색상 추출
        k = 5
        clt = KMeans(n_clusters = k)
        clt.fit(image)
        return clt

class Recommendation():
    def revised_rgb_to_hsv(self,r, g, b):
        (h, s, v) = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h *= 360
        s *= 100
        v *= 100
        return h, s, v

    def recommend(self,clt): #getClt의 output
        df_analog=[]
        df_compl=[]
        df_mono=[]

        for i in range(1,4): 
            for center in clt.cluster_centers_:
                h,s,v = Recommendation.revised_rgb_to_hsv(center[0],center[1],center[2])
                h=int(h)
                s=int(s)
                v=int(v)

                #비슷한 색감의 명화 추천
                ## roomcolor_analog(비슷한 색감) : h는 +-30도(!=0) (AND) s는동일 v는 +-5 

                #보색의 명화 추천
                ## roomcolor_compl(보색): h는 +-180도 (AND) s와v는 +-5

                #단색의 명화 추천
                ## roomcolor_mono(단색) : h는 동일 (AND) s는 +-10, v는 고려하지 않음

                roomcolor_analog= (abs(df['h'+str(i)]-h)!=0)&(abs(df['h'+str(i)]-h)<=30)&(abs(df['s'+str(i)]-s)==0)&(abs(df['v'+str(i)]-v)<=5)
                roomcolor_compl=(abs(df['h'+str(i)]-h)==180)&(abs(df['s'+str(i)]-s)<=5)&(abs(df['v'+str(i)]-v)<=5)
                roomcolor_mono=(df['h'+str(i)]==h)&(abs(df['s'+str(i)]-s)<=10)

                df_analog.append(df[roomcolor_analog]['제목'].values.tolist())  #유사색-추천받은 명화 '제목' list형식으로 append
                df_compl.append(df[roomcolor_compl]['제목'].values.tolist())  #보색-추천받은 명화 '제목' list형식으로 append
                df_mono.append(df[roomcolor_mono]['제목'].values.tolist()) #단색-추천받은 명화 '제목' list형식으로 append
            
        return df_analog,df_compl,df_mono
            
    def analog_result(self,df_analog,df_compl,df_mono):
        analog_img_bytes = []
        print("유사색 출력 갯수 : ", len(df_analog))
        print("유사색의 명화 추천 : ")
        for i in range(0,3):
            for j in range(0,6):
                try:
                    img_title = df_analog[i][j] 
                    print(img_title)
                    url = df.loc[[df.loc['제목']==img_title],['이미지url']]
                    # print(url)
                    response = requests.get(url)
                    image_bytes = io.BytesIO(response.content)
                    analog_img_bytes.append(image_bytes)
                    # img = PIL.Image.open(analog_image_bytes)
                    # img.show()
                except:
                    None
        print("="*50)
        return analog_img_bytes

    def compl_result(self,df_compl):
        compl_img_bytes = []
        print("\n보색의 명화 추천 : ")
        for i in range(0,3):
            for j in range(0,6):
                try:
                    img_title = df_compl[i][j] 
                    print(img_title)
                    url = df.loc[[df.loc['제목']==img_title],['이미지url']]
                    # print(url)
                    response = requests.get(url)
                    image_bytes = io.BytesIO(response.content)
                    compl_img_bytes.append(image_bytes)
                    # img = PIL.Image.open(compl_image_bytes)
                    # img.show()
                except:
                    None
        print("="*50)
        return compl_img_bytes

    def mono_result(self,df_mono):
        mono_img_bytes = []
        print("\n단색의 명화 추천 : ")
        for i in range(0,3):
            for j in range(0,6):
                try:
                    img_title = df_mono[i][j] 
                    print(img_title)
                    url = df.loc[[df.loc['제목']==img_title],['이미지url']]
                    # print(url)
                    response = requests.get(url)
                    image_bytes = io.BytesIO(response.content)
                    mono_img_bytes.append(image_bytes)
                    # img = PIL.Image.open(mono_image_bytes)
                    # img.show()
                except:
                    None
        return mono_img_bytes