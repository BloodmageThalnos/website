import logging
import json
import random
import os
import subprocess
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
            'url':'/article-'+str(article.id),
        })

    template = loader.get_template('home.html')
    context = {
        'articles':articles,
    }
    return HttpResponse(template.render(context, request))


def showArticle(request, id):
    articleId = int(id)
    article = ArticleModel.objects.get(id=articleId)

    template = loader.get_template('readarticle.html')
    context = {
        'author':article.author_name,
        'title':article.title,
        'excerpt':article.excerpt,
        'content':article.content,
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
            'url':'/article-'+str(article.id),
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
        pic = request.FILES.get('p')    # 封面图片
        excerpt = request.POST.get('e')
        arthur = request.POST.get('a')
        pic_name = 'acp_' + ''.join(random.choice(ascii_lowercase+ascii_uppercase+digits) for _ in range(5)) + pic.name[-6:]
        pic_url = './images/upload/'+pic_name
        with open(pic_url, mode='wb') as f:
            for chunk in pic.chunks():
                f.write(chunk)
        am=ArticleModel(title=title,content=content,author_id=0,cover_img=pic_name,author_name=arthur,excerpt=excerpt)
        am.save()
        getRecentArticles_and_cache(6)
        return HttpResponse(json.dumps({'success': 'true'}))
    elif act == 'up_image':
        pic=request.FILES.get('p')  # 封面图片
        pic_name='acp_'+''.join(random.choice(ascii_lowercase+ascii_uppercase+digits) for _ in range(5))+pic.name[-6:]
        pic_url='./images/upload/'+pic_name
        with open(pic_url,mode='wb') as f:
            for chunk in pic.chunks():
                f.write(chunk)
        return HttpResponse(json.dumps({'success': 'true', 'url':'.'+pic_url}))

    return HttpResponse(json.dumps({'success': 'false'}))

def showDebug(request, path):
    if path == 'errlog':
        with open('./log/err.log', mode='r', encoding='utf-8') as f:
            return HttpResponse(f.read().replace('\n','<br />'))
    elif path=='infolog':
        with open('./log/info.log', mode='r', encoding='utf-8') as f:
            return HttpResponse(f.read().replace('\n','<br />'))
    elif path=='doshelllog':
        with open('../do.txt', mode='r', encoding='utf-8') as f:
            return HttpResponse(f.read().replace('\n','<br />'))
    elif path=='dopullshell':
        obj=subprocess.Popen(["sleep 0.1 && sh ../do.sh > ../do.txt 2>&1"]
                             , shell=True, universal_newlines=True)
        return HttpResponse(
            '<html><head><meta http-equiv="refresh" content="2;url=/__debug__/doshelllog"></head></html>'
        )

    return HttpResponse('404 error.')