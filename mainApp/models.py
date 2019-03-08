from django.db import models

# Create your models here.
class ArticleModel(models.Model):
    title = models.TextField()
    content = models.TextField()
    create_time = models.TimeField(auto_now=True)
    author_id = models.IntegerField(default=0)
    # comments
    # visited

def getRecentArticles_and_cache(num=5):
    # articles = ArticleModel.objects.order_by()
    pass

class CommentModel(models.Model):
    pass

class VisitModel(models.Model):
    pass