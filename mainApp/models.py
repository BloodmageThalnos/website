from django.db import models
from django.core.cache import cache
import pickle

# Create your models here.
class ArticleModel(models.Model):
    title = models.TextField()
    content = models.TextField()
    create_time = models.TimeField(auto_now=True)
    author_id = models.IntegerField()
    cover_img = models.CharField(max_length=64)

    # comments
    # visited

def getRecentArticles_and_cache(num):
    articles = ArticleModel.objects.order_by('-create_time')[:num]
    cache.set('recent_articles_'+str(num), articles.query)

# def saveArticle(title, content, author_id=0):
#    am = ArticleModel(title=title,content=content,author_id=author_id)
#    am.save()

class CommentModel(models.Model):
    pass

class VisitModel(models.Model):
    pass