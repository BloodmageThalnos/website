import logging
import json
import random
import os
from string import *
from django.http import *
from django.template import loader
from django.contrib.auth import login
from django.core.cache import cache
from django.db.models import *
from .models import *

from django.shortcuts import render

# Create your views here.

logger = logging.getLogger(__name__)

def showMainPage(request):
    if cache.get('recent_articles_6') is None:
        getRecentArticles_and_cache(6)

    # 显示所有文章
    articleQ = QuerySet()
    articleQ.query = cache.get('recent_articles_6')
    articles = []
    for article in articleQ:
        articles.append({
            'title':article.title,
            'content':article.content,
            'time':article.create_time,
            'img':'/images/upload/'+article.cover_img,
            'category':article.category,
        })

    template = loader.get_template('home.html')
    context = {
        'articles':articles,
    }
    return HttpResponse(template.render(context, request))


def showTestPage(request):
    if cache.get('recent_articles_3') is None:
        getRecentArticles_and_cache(3)

    # 显示所有文章
    articleQ = QuerySet()
    articleQ.query = cache.get('recent_articles_3')
    articles = []
    for article in articleQ:
        articles.append({
            'title':article.title,
            'content':article.content,
            'time':article.create_time,
            'img':'/images/upload/'+article.cover_img,
            'category':article.category,
        })

    template = loader.get_template('test.html')
    context = {
        'articles':articles,
    }
    return HttpResponse(template.render(context, request))

def action(request):
    act = request.POST.get('act')
    if act is None:
        return HttpResponse(json.dumps({'success':'false'}))
    elif act == 'up_article':
        title = request.POST.get('t')
        content = request.POST.get('c')
        pic = request.FILES.get('p')
        pic_name = 'acp_' + ''.join(random.choice(ascii_lowercase+ascii_uppercase+digits) for _ in range(5)) + pic.name[-6:]
        pic_url = './images/upload/'+pic_name
        with open(pic_url, mode='wb') as f:
            for chunk in pic.chunks():
                f.write(chunk)
        am=ArticleModel(title=title,content=content,author_id=0,cover_img=pic_name)
        am.save()
        getRecentArticles_and_cache(3)
        getRecentArticles_and_cache(6)
        return HttpResponse(json.dumps({'success': 'true'}))

    return HttpResponse(json.dumps({'success': 'false'}))

def showDebug(request, path):
    if path == 'errlog':
        with open('./log/err.log', mode='r', encoding='utf-8') as f:
            return HttpResponse(f.read().replace('\n','<br />'))
    elif path=='infolog':
        with open('./log/info.log', mode='r', encoding='utf-8') as f:
            return HttpResponse(f.read().replace('\n','<br />'))
    elif path=='dopullshell':
        out = os.subprocess.check_output(['sh','../do.sh'])
        return HttpResponse(out)

    return HttpResponse('404 error.')