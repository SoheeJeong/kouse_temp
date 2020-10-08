from django.conf.urls import url
from . import views
# from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    url(r'^$',views.pic_list, name='pic_list'),
    url(r'^imgupload/$',views.img_upload,name='img_upload'),
    url(r'^compresult/(?P<pk>\d+)/$',views.comp_result,name='comp_result'),
]
