from django.conf.urls import url
from . import views
# from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    url(r'^$',views.pic_list, name='pic_list'), #나중에 name으로부터 url을 생성할 수 있음/template 밑에 html에서 사용 가능
    url(r'^imgupload/$',views.img_upload,name='img_upload'),
    url(r'^imgkmeans/(?P<pk>\d+)/$',views.img_kmeans,name='img_kmeans'),
    url(r'^compresult/(?P<pk>\d+)/$',views.comp_result,name='comp_result'),
]
