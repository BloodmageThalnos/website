from django.db import models
from django.core.cache import cache
import pickle

# Create your models here.
class ArticleModel(models.Model):
    title = models.TextField()
    content = models.TextField()
    excerpt = models.TextField(default="")
    create_date = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateTimeField(auto_now=True)
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=32, default="")
    category = models.CharField(max_length=32)
    cover_img = models.CharField(max_length=64)
    type = models.IntegerField(default=1) # 1为正常文章，2为待审核，3为已删除
    # url = models.CharField(max_length=64, default="")
    # related_img

    def __str__(self):
        return '【' + (self.title if len(self.title)<=20 else (self.title[:21]+'...')) + '】 ' + self.content[:min(len(self.content),30)]

    # comments
    # visited

class CommentModel(models.Model):
    pass

class VisitModel(models.Model):
    pass