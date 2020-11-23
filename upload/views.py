#app.py 역할

from django.shortcuts import render
# from django.contrib.auth.decorators import login_required #보안강화
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import CrawlingData, Image
from .forms import CrawlingDataForm, ImageForm
from .mycode import GetImageColor, Recommendation

# Create your views here.
#show crawling_data table info list
def pic_list(request):
    # MyClass.print_something()
    # piclist = CrawlingData.objects.all() #django 명령어 사용
    piclist = CrawlingData.objects.raw('SELECT * from crawling_data') #mysql query로 시도
    piclist = piclist[:20]
    return render(request,'upload/pic_list.html',{'pic_list':piclist})

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

#check image kmeans result
def img_kmeans(request,pk):
    img_obj = get_object_or_404(Image,pk=pk) #방금 업로드한 이미지
    GetImageColor(img_obj.image.url)
    return render(request,'upload/img_kmeans.html',{'img_obj':img_obj,'color_info':'/media/images/tempplot.png'})

def comp_result(request,pk):
    image_uploaded = get_object_or_404(Image,pk=pk) #방금 업로드한 이미지의 pk에 맞는애의 name
    df = CrawlingData.objects.all()

    temp1 = GetImageColor(image_uploaded.image.url)
    
    #clt = temp1.get_kmeans() #room color clt with kmeans
    clt = temp1.get_meanshift() #room color clt with meanshift
    
    temp2 = Recommendation(clt,df)
    analog,comp,mono = temp2.recommend() #recommended images list
    # analog_imgs = temp2.analog_result(analog,comp,mono) #show recommended images
    return render(request,'upload/comp_result.html',{'img_info':image_uploaded,'color_info':'/media/images/tempplot.png','analog':analog,'comp':comp,'mono':mono,
                            'analogimg':analog['imageurl'],'compimg':comp['imageurl'],'monoimg':mono['imageurl']})