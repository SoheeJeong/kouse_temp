#app.py 역할

from django.shortcuts import render
from django.conf import settings
# from django.contrib.auth.decorators import login_required #보안강화
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db import DatabaseError, connection
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse

from upload import models

from .models import CrawlingData, Image
from .forms import CrawlingDataForm, ImageForm
from .mycode import GetImageColor, Recommendation


#get query result
def get_sql_query_result(sql,param=None):
    with connection.cursor() as cursor:
        #sql문 실행
        if not param:
            cursor.execute(sql) #no parameter
        else:
            cursor.execute(sql,(param))
        #sql 실행결과 반환
        result = cursor.fetchall()
    return result

#show crawling_data table info list
def pic_list(request):
    # piclist = CrawlingData.objects.raw('SELECT * from crawling_data') #mysql query로 시도
    piclist = get_sql_query_result('SELECT artist,title,h1,s1,v1,imageurl from crawling_data')
    piclist = piclist[:20]
    result=[]
    for p in piclist:
        result.append({'artist':p[0],'title':p[1],'h1':p[2],'s1':p[3],'v1':p[4],'imageurl':p[5]})
    
    # return JsonResponse(result)
    return render(request,'upload/pic_list.html',{'pic_list':result})

#user upload image
def img_upload(request):
    """Process images uploaded by users"""
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'upload/img_upload.html', {'form': form, 'img_obj': img_obj})
    else:
        form = ImageForm()
        
    return render(request, 'upload/img_upload.html', {'form': form})

#check image clustering result
def img_clustering(request,pk):
    # pk = request.GET.get("pk",None) 

    img_obj = get_sql_query_result('SELECT id, title, image from upload_image WHERE id=%s',pk)    
    image = img_obj[0]

    GetImageColor(settings.MEDIA_URL+image[2],image[2]).get_meanshift()

    result = {
        'pk':image[0],
        'title':image[1],
        'imgurl':settings.MEDIA_URL+image[2],
        'color_info':settings.MEDIA_URL+image[2]+'_cluster_result.png',
    }

    # return JsonResponse(result)
    return render(request,'upload/img_clustering.html',{'result':result})

def comp_result(request,pk):
    # pk = request.GET.get("pk",None) 

    #df = CrawlingData.objects.all()
    pic_data = get_sql_query_result('SELECT * FROM crawling_data')
   
    #image_uploaded = get_object_or_404(Image,pk=pk) #방금 업로드한 이미지의 pk에 맞는애의 name
    image_uploaded = get_sql_query_result('SELECT id, title, image from upload_image WHERE id=%s',pk) 
    image = image_uploaded[0]
    
    #clt = GetImageColor(settings.MEDIA_URL+image[2],image[1]).get_kmeans() #room color clt with kmeans
    clt =  GetImageColor(settings.MEDIA_URL+image[2],image[1]).get_meanshift() #room color clt with meanshift

    analog,comp,mono = Recommendation(clt,pic_data).recommend_pic() #recommended images list

    result = {
        'img_info':{
            'pk':image[0],
            'title':image[1],
            'imgurl':settings.MEDIA_URL+image[2],
        },
        'clustering_result':settings.MEDIA_URL+image[2]+'_cluster_result.png',
        'recommend_result':{
            'analog':analog['imageurl'],
            'comp':comp['imageurl'],
            'mono':mono['imageurl']   
        }
    }

    # return JsonResponse(result)
    return render(request,'upload/comp_result.html',{'result':result})
    