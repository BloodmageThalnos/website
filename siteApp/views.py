import logging
import json
import os

from django.contrib.auth.models import User
from django.http import *
from django.template import loader
from django.contrib.auth import login
import subprocess
from .models import *
from hashlib import sha256
import datetime

from django.shortcuts import render

logger = logging.getLogger(__name__)

def showRoot(request):
    template = loader.get_template('root.html')
    context = {}
    return HttpResponse(template.render(context, request))


def showCv(request):
    template = loader.get_template('cv.html')
    context = {}
    return HttpResponse(template.render(context, request))


def showUploadArticle(request):
    template = loader.get_template('editarticle.html')
    context = {}
    return HttpResponse(template.render(context, request))


def showStatistics(request):
    pass


# /visit
# 用于统计页面访问信息，如访问者user、浏览页面、时间等
# 相关参数：
#  a: 1 首次访问 2 更新访问时间
def doVisit(request):
    act = request.POST.get("a")
    if act == '1':
        ip = request.META['HTTP_X_FORWARDED_FOR']if request.META.__contains__('HTTP_X_FORWARDED_FOR')else request.META['REMOTE_ADDR']
        url = request.POST.get("u")
        id = request.POST.get("b")
        user_id = 0 # TODO: 用户系统上线后修改此处
        vm = VisitModel(user_id=user_id, user_ip=ip, b_id=id_(id), url=url, duration=0)
        vm.save()
        return HttpResponse(str(vm.id))
    elif act == '2':
        id = request.POST.get('i')
        time = int(request.POST.get('t')) # millisecond
        vm = VisitModel.objects.get(id=int(id))
        if time - vm.duration > 60 + vm.duration**0.5: # perhaps attack, ignore it
            pass
        vm.duration = max(vm.duration, time)
        vm.save()
        return HttpResponse(vm.id)
    else:
        pass # error.


# /debug/<slug:path>
# 显示debug用的一些页面，包括errlog、infolog、doshelllog
# 访问dopullshell会执行服务器上的../do.sh，用来进行git pull等操作。
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
            '<html><head><meta http-equiv="refresh" content="3;url=/__debug__/doshelllog"></head></html>'
        )

    return HttpResponse('502 error.')


def showLife(request, path):
    if not User.objects.filter(username__exact=path).count():
        return HttpResponseNotFound('扫开法庭')
    if request.user.is_authenticated:
        template=loader.get_template('life.html')
        use = request.GET.get('use_saved')
        if use is not None:
            if not use.startswith('life_'+path):
                return HttpResponse('扫开大法庭')
            if not os.path.exists('./life/'+use):
                return HttpResponse('扫开二法庭' + use)
            content = open('./life/'+use, encoding='gbk').read()
        else:
            if not os.path.exists('./life/life_'+path+'.html'):
                from shutil import copyfile
                copyfile('./life/example.html','./life/life_'+path+'.html')
            content = open('./life/life_'+path+'.html', encoding='gbk').read()
        context={'content':content}
        if request.user.username == path:
            context['saveid']=sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]
        return HttpResponse(template.render(context,request))
    else:
        return HttpResponseRedirect('/login?next=/life/'+path)

def saveLife(request):
    saveid = request.POST.get('saveid')
    content = request.POST.get('content')
    auto = request.POST.get('auto')
    if saveid != sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]:
        logger.error('Somebody tried to save without authentication.')
        logger.error(content)
        return HttpResponse('保存失败，登录状态出现问题，或没有权限。')

    username = request.user.username

    # 每个用户只保存50个auto和50个手动
    # TODO: 此操作应设为脚本，而不是每次保存时调用
    life = sorted([x for x in os.listdir('./life') if x.startswith('life_'+username+'-')],key=lambda x:os.path.getmtime('./life/'+x), reverse=True)
    lifeauto = sorted([x for x in os.listdir('./life') if x.startswith('life_'+username+'_')],key=lambda x:os.path.getmtime('./life/'+x), reverse=True)
    if len(life) > 1:
        for i in range(1,len(life)):
            os.remove('./life/'+life[i])
    if len(lifeauto)>1:
        for i in range(1,len(lifeauto)):
            os.remove('./life/'+lifeauto[i])

    if auto == '1':
        with open(datetime.datetime.now().strftime('./life/life_'+username+'_自动保存-%y%m%d%H%M%S.html'), mode="w", encoding="GBK") as f:
            f.write(content)
    else:
        try:
            os.rename('./life/life_'+username+'.html',datetime.datetime.now().strftime('./life/life_'+username+'-%y%m%d%H%M%S.html'))
        except:
            pass
        with open('./life/life_'+username+'.html', mode="w", encoding="GBK") as f:
            f.write(content)
    return HttpResponse('保存成功。')

def showLifeList(request):
    pass