import logging
import json
import random
import os
import shutil
import subprocess
from string import *
from django.http import *
from django.template import loader
from django.contrib.auth import login
from django.core.cache import cache
from django.db.models import *
from .models import *
from Website.settings import SUPERCODE

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
            'img':article.cover_img,
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


def action(request):
    act = request.POST.get('act')
    if act is None:
        return HttpResponse(json.dumps({'success':'false'}))
    elif act == 'up_article':
        title = request.POST.get('t')
        content = request.POST.get('c')
        pic = request.POST.get('p')    # 封面图片
        excerpt = request.POST.get('e')
        arthur = request.POST.get('a')
        supercode = request.POST.get('supercode')
        if supercode==SUPERCODE:
            type = 1
        else:
            type = 2
        am=ArticleModel(title=title,content=content,author_id=0,cover_img=pic,author_name=arthur,excerpt=excerpt,type=type)
        am.save()
        getRecentArticles_and_cache(6)
        return HttpResponse(json.dumps({'success': 'true'}))
    elif act == 'up_img':
        pic=request.FILES.get('p')  # 封面图片
        pic_name='img'+''.join(random.choice(ascii_lowercase+ascii_uppercase+digits) for _ in range(8))+pic.name[-6:]
        pic_url='./images/upload/'+pic_name
        with open(pic_url,mode='wb') as f:
            for chunk in pic.chunks():
                f.write(chunk)
        return HttpResponse(json.dumps({'success': 'true', 'url':'.'+pic_url}))
    elif act == 'manage_img':
        page = request.POST.get('page')
        supercode = request.POST.get('sc')
        if supercode!=SUPERCODE:
            return HttpResponse("_")
        imgs = []
        imgfrom = 10*(int(page)-1)
        imgto = 10*int(page)-1
        imglist = os.listdir('./images/upload')
        imglist.sort(key=lambda x:os.path.getmtime('./images/upload/'+x), reverse=True)
        for img in imglist:
            imgs.append({
                'url': '/images/upload/'+img,
                'id': img,
            })

        template=loader.get_template('manageImgs.html')
        context={
            'imgs': imgs,
        }
        return HttpResponse(template.render(context,request))
    elif act == 'doimg_del':
        id = request.POST.get('id')
        if os.path.isfile('./images/upload/'+id):
            shutil.move('./images/upload/'+id,'./images/deleted/'+id)
            return HttpResponse(json.dumps({'success': 'true', 'msg': 'delete ok.'}))
        else:
            return HttpResponse(json.dumps({'success': 'false', 'msg': 'you idiot.'}))
    elif act == 'doimg_repl':
        pic=request.FILES.get('p')  # 封面图片
        id = request.POST.get('id')
        if os.path.isfile('./images/upload/'+id):
            pic_url='./images/upload/'+id
            with open(pic_url,mode='wb') as f:
                for chunk in pic.chunks():
                    f.write(chunk)
            return HttpResponse(json.dumps({'success': 'true', 'msg': 'replace ok.'}))
        else:
            return HttpResponse(json.dumps({'success': 'false', 'msg': 'you fool.'}))


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