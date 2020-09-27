from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

# #phpmyadmin에서 불러올 data
# class CrawlingData(models.Model):
#     artist = models.TextField()
#     title = models.TextField()
#     h1 = models.SmallIntegerField()
#     s1 = models.SmallIntegerField()
#     v1 = models.SmallIntegerField()
#     h2 = models.SmallIntegerField()
#     s2 = models.SmallIntegerField()
#     v2 = models.SmallIntegerField()
#     h3 = models.SmallIntegerField()
#     s3 = models.SmallIntegerField()
#     v3 = models.SmallIntegerField()
#     imageurl = models.TextField()

class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

#사용자 입력 사진 data
#사용자 입력 댓글 data
