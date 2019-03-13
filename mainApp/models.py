from django.db import models
from django.core.cache import cache
import pickle

# Create your models here.
class ArticleModel(models.Model):
    title = models.TextField()
    content = models.TextField()
    create_time = models.TimeField(auto_now=True)
    author_id = models.IntegerField(default=0)
    # comments
    # visited

def getRecentArticles_and_cache(num):
    articles = ArticleModel.objects.order_by('-create_time')[:num]
    cache.set('recent_articles', articles.query)
    return articles

class CommentModel(models.Model):
    pass

class VisitModel(models.Model):
    pass