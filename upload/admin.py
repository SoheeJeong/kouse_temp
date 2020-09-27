from django.contrib import admin
from .models import CrawlingData

# Register your models here.
# 출력할 ResourceAdmin 클래스를 만든다
class CrawlingDataAdmin(admin.ModelAdmin):
  list_display = ('id', 'artist','title','h1','s1','v1','h2','s2','v2','h3','s3','v3','imageurl')

admin.site.register(CrawlingData,CrawlingDataAdmin)

