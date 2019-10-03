import json
import random
import shutil
import os
from string import ascii_lowercase, ascii_uppercase, digits

from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from mainApp.models import thumb_from_cover_img, ArticleModel


###
# action 集成了各种后台操作，POST请求中act字段表示具体的操作类型：
#  edit_article 编辑文章
#  up_article 上传文章
#  up_img  上传图片
#  manage_img 显示图片管理器
#  doimg_del 删除图片
#  doimg_repl 替换图片
#  doimg_find 查找引用位置（从封面图片和内容两个字段搜索）
#  load_list 显示文章列表（编辑文章功能使用）
#  load_label 加载标签列表（最多使用的10个标签）
#  load_load 加载单篇文章（编辑文章功能使用）
###
def action(request):
    # 权限控制
    # 目前权限控制采用一把梭：所有操作强制只能 dva，因为没有第二名管理员；若增加管理员则可考虑采用is_staff
    # if not request.user.is_staff:
    if not request.user.username == 'dva':
        return HttpResponse(json.dumps({'success':'false', 'msg':'未登录或没有权限！'}))

    act = request.POST.get('act')
    if act is None:
        return HttpResponse(json.dumps({'success':'false'}))
    elif act == 'edit_article':
        title=request.POST.get('t')   # 标题
        content=request.POST.get('c') # 内容
        pic=request.POST.get('p')     # 封面图片
        excerpt=request.POST.get('e') # 摘要
        arthur=request.POST.get('a')  # 作者
        id_=request.POST.get('i')     # 文章id
        label=request.POST.get('l')   # 分类
        type_ = 1
        try:
            am = ArticleModel.objects.get(id=int(id_))
        except:
            return HttpResponse(json.dumps({'success':'false', 'msg':'id error, please check.'}))
        am.title=title
        am.content=content
        am.cover_img=pic
        am.excerpt=excerpt
        am.author=arthur
        '''
        if am.type==1 and type==2:
            return HttpResponse(json.dumps({'success': 'false', 'msg':'supercode error.'}))
        elif am.type==3:
            return HttpResponse(json.dumps({'success': 'false', 'msg':'attempt to edit deleted article failed.'}))
            '''
        am.type=type_
        am.category=label

        # 处理缩略图
        pic_path='./images/upload'+pic[pic.rfind('/'):]
        if not os.path.isfile(pic_path+'_thumb'+pic_path[-6:]):
            thumb_from_cover_img(pic_path,pic_path+'_thumb'+pic_path[-6:])
        am.cover_img_thumb=pic_path[1:]+'_thumb'+pic_path[-6:]

        am.save()

        # 成功，跳转到文章页面
        return HttpResponseRedirect('/article-'+str(am.id))
    elif act == 'up_article':
        title=request.POST.get('t')   # 标题
        content=request.POST.get('c') # 内容
        pic=request.POST.get('p')     # 封面图片
        excerpt=request.POST.get('e') # 摘要
        arthur=request.POST.get('a')  # 作者
        label=request.POST.get('l')   # 分类
        type_ = 1
        am = ArticleModel(
            title=title,
            content=content,
            author_id=0,
            cover_img=pic,
            author_name=arthur,
            excerpt=excerpt,
            category=label,
            type=type_
        )

        # 处理缩略图
        pic_path='./images/upload'+pic[pic.rfind('/'):]
        if not os.path.isfile(pic_path+'_thumb'+pic_path[-6:]):
            thumb_from_cover_img(pic_path,pic_path+'_thumb'+pic_path[-6:])
        am.cover_img_thumb=pic_path[1:]+'_thumb'+pic_path[-6:]

        am.save()

        # 成功，跳转到文章页面
        HttpResponseRedirect('/article-'+str(am.id))
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
        id_ = request.POST.get('id')
        if os.path.isfile('./images/upload/' + id_):
            if os.path.isfile('./images/upload' + id_ + '_thumb' + id_[-6:]): # 删除缩略图
                os.remove('./images/upload' + id_ + '_thumb' + id_[-6:])
            os.makedirs('./images/deleted/', exist_ok=True)
            shutil.move('./images/upload/' + id_, './images/deleted/' + id_)
            return HttpResponse(json.dumps({'success': 'true', 'msg': 'delete ok.'}))
        else:
            return HttpResponse(json.dumps({'success': 'false', 'msg': 'you idiot.'}))
    elif act == 'doimg_repl':
        pic=request.FILES.get('p')  # 封面图片
        if pic is None:
            return HttpResponse(json.dumps({'success': 'false', 'msg': '没有选择图片！'}))
        id_ = request.POST.get('id')
        if os.path.isfile('./images/upload/' + id_):
            pic_url='./images/upload/' + id_
            if os.path.isfile('./images/upload' + id_ + '_thumb' + id_[-6:]): # 删除缩略图
                os.remove('./images/upload' + id_ + '_thumb' + id_[-6:])
            with open(pic_url,mode='wb') as f:
                for chunk in pic.chunks():
                    f.write(chunk)
            return HttpResponse(json.dumps({'success': 'true', 'msg': 'replace ok.'}))
        else:
            return HttpResponse(json.dumps({'success': 'false', 'msg': 'you fool.'}))
    elif act == 'doimg_find':
        id_ = request.POST.get('id')
        output = ''
        # in articles
        articles=ArticleModel.objects.filter(type__lt=3).order_by('-create_date')
        for article in articles:
            if article.content.find(id_)!=-1:
                output += '在文章【'+article.title[:15]+'】中使用 1 次；\n'
            if article.cover_img.find(id_)!=-1:
                output += '作为文章【'+article.title[:15]+'】的封面图片；\n'

        # in static files
        files = os.listdir('./html')
        for file in files:
            with open('./html/'+file, encoding='utf-8') as f:
                if f.read().find(id_)!=-1:
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
    elif act == 'load_label':
        articles=ArticleModel.objects.filter(type__lt=3).values('category').annotate(dcount=Count('category')).order_by('-dcount')
        count = articles.count()
        if count > 10:
            articles = articles[:10]
        arts = []
        for article in articles:
            arts.append({
                'name': article['category'],
            })
        context={
            'labels':arts,
        }
        template=loader.get_template('loadlabel.html')
        return HttpResponse(template.render(context,request))
    elif act == 'load_load':
        id_ = request.POST.get('id')
        try:
            article = ArticleModel.objects.get(id=id_)
        except:
            return HttpResponse(json.dumps({'success': 'false', 'msg': 'you bad bad.'}))
        return HttpResponse(json.dumps({
            'success': 'true',
            'title': article.title,
            'content': article.content,
            'excerpt': article.excerpt,
            'author': article.author_name,
            'cover': article.cover_img,
            'label': article.category,
        }))

    return HttpResponse(json.dumps({'success': 'false'}))
