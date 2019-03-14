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

def getRecentArticles_and_cache(last, first=0):
    if ArticleModel.objects.count()<last:
        return False
    articles = ArticleModel.objects.order_by('-create_time')[first:last]
    cache.set('recent_articles_'+str(last-first), articles.query)
    return True

# def saveArticle(title, content, author_id=0):
#    am = ArticleModel(title=title,content=content,author_id=author_id)
#    am.save()

class CommentModel(models.Model):
    pass

class VisitModel(models.Model):
    pass