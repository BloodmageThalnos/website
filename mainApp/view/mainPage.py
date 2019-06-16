import os
import random

from django.http import HttpResponse
from django.template import loader

from mainApp.models import ArticleModel

from .disqus import getDisqus

# 显示主页
def showMainPage(request):
    # 主页文章，显示最近3篇和随机的三篇
    # TODO: 文章多之后可以将这个结果缓存起来
    query = list(ArticleModel.objects.filter(type__exact=1).order_by('-create_date'))
    a = query[:3]
    b = query[3:]
    random.shuffle(b)
    articleQ = a+b[:3]

    # random.shuffle(articleQ)
    articles = []
    for article in articleQ:
        articles.append({
            'title':article.title,
            'content':article.content,
            'time':article.create_date,
            'img':article.cover_img,
            'category':article.category,
            'url':'/article-'+str(article.id),
        })

    # 主页message board
    disquses = getDisqus(4)

    template = loader.get_template('home.html')
    context = {
        'articles':articles,
        'disquses':disquses,
    }
    return HttpResponse(template.render(context, request))
