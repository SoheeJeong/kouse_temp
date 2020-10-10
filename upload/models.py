# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class CrawlingData(models.Model):
    artist = models.TextField()
    title = models.TextField()
    h1 = models.SmallIntegerField()
    s1 = models.SmallIntegerField()
    v1 = models.SmallIntegerField()
    h2 = models.SmallIntegerField()
    s2 = models.SmallIntegerField()
    v2 = models.SmallIntegerField()
    h3 = models.SmallIntegerField()
    s3 = models.SmallIntegerField()
    v3 = models.SmallIntegerField()
    imageurl = models.TextField()

    class Meta:
        managed = False
        db_table = 'crawling_data'

class Image(models.Model):
    title = models.CharField(max_length = 500)
    image = models.ImageField(upload_to='images')
    #user = models.CharField(max_length = 100)

    def __str__(self):
        return self.title