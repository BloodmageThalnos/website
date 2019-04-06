import logging
import json
import random
import os
import shutil
from string import *
from django.http import *
from django.template import loader
from django.contrib.auth import login
from django.core.cache import cache
from django.db.models import *
from .models import *
from Website.settings import SUPERCODE

from django.shortcuts import render

logger = logging.getLogger(__name__)


# 显示主页
def showMainPage(request):
    # 主页文章，显示最近6篇并随机排序
    articleQ = list(ArticleModel.objects.filter(type__exact=1).order_by('-create_date')[0:6])
    random.shuffle(articleQ)
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


# 显示单篇文章
# /article-(?P<id>[0-9]+)
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

###
# action 集成了各种后台操作，POST请求中act字段表示具体的操作类型：
#  edit_article 编辑文章（需要supercode，否则文章type=2）
#  up_article 上传文章（需要supercode，否则文章type=2）
#  up_img  上传图片
#  manage_img 显示图片管理器（需要supercode，否则返回_）
#  doimg_del 删除图片
#  doimg_repl 替换图片
#  doimg_find 查找引用位置（从封面图片和内容两个字段搜索）
#  load_list 显示文章列表（编辑文章功能使用）
#  load_load 加载单篇文章（编辑文章功能使用）
###
def action(request):
    act = request.POST.get('act')
    if act is None:
        return HttpResponse(json.dumps({'success':'false'}))
    elif act == 'edit_article':
        title=request.POST.get('t')   # 标题
        content=request.POST.get('c') # 内容
        pic=request.POST.get('p')     # 封面图片
        excerpt=request.POST.get('e') # 摘要
        arthur=request.POST.get('a')  # 作者
        id=request.POST.get('i')      # 文章id
        supercode=request.POST.get('supercode')
        type = 1 if supercode==SUPERCODE else 2
        try:
            am=ArticleModel.objects.get(id=int(id))
        except:
            return HttpResponse(json.dumps({'success':'false', 'msg':'id error.'}))
        am.title=title
        am.content=content
        am.cover_img=pic
        am.excerpt=excerpt
        am.author=arthur
        am.type=type
        am.save()
        return HttpResponse(json.dumps({'success': 'true'}))
    elif act == 'up_article':
        title = request.POST.get('t')
        content = request.POST.get('c')
        pic = request.POST.get('p')    # 封面图片
        excerpt = request.POST.get('e')
        arthur = request.POST.get('a')
        supercode = request.POST.get('supercode')
        type = 1 if supercode==SUPERCODE else 2
        am=ArticleModel(title=title,content=content,author_id=0,cover_img=pic,author_name=arthur,excerpt=excerpt,type=type)
        am.save()
        return HttpResponse(json.dumps({'success': 'true'}))
    elif act == 'up_img':
        pic=request.FILES.get('p')  # 封面图片
        if pic==None:
            return HttpResponse(json.dumps({'success': 'false'}))
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

        template=loader.get_template('doimg.html')
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
        if pic==None:
            return HttpResponse(json.dumps({'success': 'false', 'msg': '没有选择图片！'}))
        id = request.POST.get('id')
        if os.path.isfile('./images/upload/'+id):
            pic_url='./images/upload/'+id
            with open(pic_url,mode='wb') as f:
                for chunk in pic.chunks():
                    f.write(chunk)
            return HttpResponse(json.dumps({'success': 'true', 'msg': 'replace ok.'}))
        else:
            return HttpResponse(json.dumps({'success': 'false', 'msg': 'you fool.'}))
    elif act == 'doimg_find':
        id = request.POST.get('id')
        output = ''
        # in articles
        articles=ArticleModel.objects.filter(type__lt=3).order_by('-create_date')
        for article in articles:
            if article.content.find(id)!=-1:
                output += '在文章【'+article.title[:15]+'】中使用 1 次；\n'
            if article.cover_img.find(id)!=-1:
                output += '作为文章【'+article.title[:15]+'】的封面图片；\n'

        # in static files
        files = os.listdir('./html')
        for file in files:
            with open('./html/'+file, encoding='utf-8') as f:
                if f.read().find(id)!=-1:
                    output += 'In static file '+file+'；\n'

        if output == '':
            output = '没有找到相关信息。'
        return HttpResponse(json.dumps({'success':'true', 'msg': output}))
    elif act == 'load_list':
        articles=ArticleModel.objects.filter(type__lt=3).order_by('-create_date')
        arts = []
        for article in articles:
            arts.append({
                'title': article.title[:18]+'...',
                'id': article.id,
            })
        context={
            'articles':arts,
        }
        template=loader.get_template('loadlst.html')
        return HttpResponse(template.render(context,request))
    elif act == 'load_load':
        id = request.POST.get('id')
        try:
            article = ArticleModel.objects.get(id=id)
        except:
            return HttpResponse(json.dumps({'success': 'false', 'msg': 'you bad bad.'}))
        return HttpResponse(json.dumps({
            'success': 'true',
            'title': article.title,
            'content': article.content,
            'excerpt': article.excerpt,
            'author': article.author_name,
            'cover': article.cover_img,
        }))

    return HttpResponse(json.dumps({'success': 'false'}))


def getDisqus(num=0):
    dm = DisqusModel.objects.order_by('-c_date','-c_time')
    if num>=dm.count():
        dm = dm[:num]
    ret = []
    for d in dm:
        now = {
            'id': 'disq_'+str(d.id),
            'nickname': d.nickname,
            'username': d.username,
            'content': d.content,
            'hasimg': d.picture!='',
            'picture': '/images/upload/'+d.picture,
            'time': d.c_date.__str__()+' '+d.c_time.__str__(),
        }
        if d.avatar!='':
            now['avatar']='/images/upload/'+d.avatar
        else:
            avatars = os.listdir('./images/avatar')
            hash = sum(ord(x) for x in d.nickname)
            now['avatar']='/images/avatar/'+avatars[hash%len(avatars)]
            # 从系统中随机选择图片作为头像
        ret.append(now)
    return ret


def showDisqus(request):
    disquses = getDisqus()
    template=loader.get_template('Disqus.html')
    context={
        'disquses': disquses,
    }
    return HttpResponse(template.render(context,request))


def postDisqus(request):
    userid = 0 # TODO: 用户系统上线后修改
    avatar = request.FILES.get('avatar')
    nickname = request.POST.get('nickname')
    if userid == 0:
        ip=request.META['HTTP_X_FORWARDED_FOR']if request.META.__contains__('HTTP_X_FORWARDED_FOR')else request.META['REMOTE_ADDR']
        username = '游客 from '+ip
    else:
        username = '...'
    content = request.POST.get('content')
    pic = request.FILES.get('pic')
    reply_to = 0 # TODO: 回复功能待添加
    # TODO: 判断上传的是不是图片

    if len(content)>50 or sum(1 for x in content if x=='\n')>3:
        return HttpResponse(json.dumps({
            'success': 'false',
            'msg': '字数太长或换行过多！',
        }))

    pic_name = ''
    if pic != None:
        pic_name='disq'+''.join(random.choice(ascii_lowercase+ascii_uppercase) for _ in range(6))+pic.name[-6:]
        pic_url='./images/upload/'+pic_name
        with open(pic_url,mode='wb') as f:
            for chunk in pic.chunks():
                f.write(chunk)
    ava_name = ''
    if avatar != None:
        ava_name='disq'+''.join(random.choice(ascii_lowercase+ascii_uppercase) for _ in range(6))+avatar.name[-6:]
        ava_url='./images/upload/'+ava_name
        with open(ava_url,mode='wb') as f:
            for chunk in avatar.chunks():
                f.write(chunk)
    dm = DisqusModel(
        user_id = userid,
        avatar = ava_name,
        nickname = nickname,
        username = username,
        content = content,
        picture = pic_name,
        reply_to = reply_to
    )
    dm.save()
    return HttpResponse(json.dumps({
        'success': 'true',
    }))
