from django.db import models
from django.core.cache import cache
import pickle
from PIL import Image, ImageOps

# Create your models here.
class ArticleModel(models.Model):
    title = models.TextField()
    content = models.TextField()
    excerpt = models.TextField(default="")
    create_date = models.DateTimeField(auto_now_add=True, db_index=True)
    edit_date = models.DateTimeField(auto_now=True)
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=32, default="")
    category = models.CharField(max_length=32)
    cover_img = models.CharField(max_length=64)
    cover_img_thumb = models.CharField(max_length=64, default="")
    type = models.IntegerField(default=1) # 1为正常文章，2为待审核，3为已删除
    # url = models.CharField(max_length=64, default="")
    # related_img

    def __str__(self):
        return '【' + (self.title if len(self.title)<=20 else (self.title[:21]+'...')) + '】 ' + self.content[:min(len(self.content),30)]

    # comments
    # visited

def thumb_from_cover_img(img_path, img_path_new):
    img = Image.open(img_path)
    size = min(500, min(img.size[0], img.size[1]))
    # img.thumbnail((size,size))
    img = ImageOps.fit(img,(size,size))
    img.save(img_path_new)


class CommentModel(models.Model):
    pass


class DisqusModel(models.Model):
    user_id = models.IntegerField()
    avatar = models.CharField(max_length=64, default="")
    c_time = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=32)
    username = models.CharField(max_length=32)
    content = models.TextField()
    picture = models.CharField(max_length=64, default="")
    reply_to = models.IntegerField()
    color = models.CharField(max_length=8, default='#ff9911')

    def __str__(self):
        return '【'+self.nickname+'】 '+self.content
