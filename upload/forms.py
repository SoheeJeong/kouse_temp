from django import forms
from .models import CrawlingData, Image

#PostForm이라는 form을 만들자
class CrawlingDataForm(forms.ModelForm):

    class Meta:
        model = CrawlingData
        fields = ('artist','title','h1','s1','v1','h2','s2','v2','h3','s3','v3','imageurl')

class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Image
        fields = ('title', 'image')