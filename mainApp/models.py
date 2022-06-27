import logging
import os

from django.db import models
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

class ArticleModel(models.Model):
    title = models.TextField()
    content = models.TextField()
    excerpt = models.TextField(default="", blank=True)
    create_date = models.DateTimeField(auto_now_add=True, db_index=True)
    edit_date = models.DateTimeField(auto_now=True)
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=32, default="")
    category = models.CharField(max_length=32)
    cover_img = models.CharField(max_length=64)
    cover_img_thumb = models.CharField(max_length=64, default="")
    def get_thumb(self):
        pic=self.cover_img
        pic_path='./images/upload'+pic[pic.rfind('/'):]
        if not os.path.isfile(pic_path+'_thumb'+pic_path[-6:]):
            thumb_from_cover_img(pic_path,pic_path+'_thumb'+pic_path[-6:])
            self.cover_img_thumb=pic_path[1:]+'_thumb'+pic_path[-6:]
            self.save()

        # 缩略图url bug hack：开头不应有.
        while self.cover_img_thumb.startswith('.'):
            self.cover_img_thumb = self.cover_img_thumb[1:]
            self.save()

        return self.cover_img_thumb
    type = models.IntegerField(default=1) # 1为正常文章，2为待审核，3为已删除
    extra = models.TextField(default="", blank=True)
    # url = models.CharField(max_length=64, default="")
    # related_img

    def __str__(self):
        return '【' + (self.title if len(self.title)<=20 else (self.title[:21]+'...')) + '】 ' + self.content[:min(len(self.content),30)]

    # comments
    # visited

def thumb_from_cover_img(img_path, img_path_new):
    try:
        img = Image.open(img_path)
        size = min(500, min(img.size[0], img.size[1]))
        # img.thumbnail((size,size))
        img = ImageOps.fit(img,(size,size))
        img.save(img_path_new)
    except Exception as e:
        logger.error(e)

class CommentModel(models.Model):
    pass

class DisqusModel(models.Model):
    user_id = models.IntegerField()
    avatar = models.CharField(max_length=64, default="", blank=True)
    c_time = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=32)
    username = models.CharField(max_length=32)
    content = models.TextField()
    picture = models.CharField(max_length=64, default="", blank=True)
    reply_to = models.IntegerField()
    color = models.CharField(max_length=8, default='#ff9911')

    def __str__(self):
        return '【'+self.nickname+'】 '+self.content
