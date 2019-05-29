import gzip
import logging
import json

from django.contrib.auth.models import User
from django.http import *
from django.template import loader
import subprocess
from .models import *
from hashlib import sha256
import datetime

from .view.music import showMusic

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
        return HttpResponseNotFound('用户不存在！')
    if request.user.is_authenticated:
        template=loader.get_template('life.html')
        use = request.GET.get('use_saved')
        context = {}
        if use is not None:
            context['use_saved'] = True
            context['saved_filename'] = use

            if not use.startswith('life_'+path):
                return HttpResponse('use saved format error.')
            if not os.path.exists('./life/'+use):
                return HttpResponse('use saved file not exists.')
            gzip_content = open('./life/'+use, mode="rb").read()
            content = gzip.decompress(gzip_content).decode('gbk')
        else:
            if not os.path.exists('./life/life_'+path+'.html'):
                from shutil import copyfile
                copyfile('./life/example.html','./life/life_'+path+'.html')
            gzip_content = open('./life/life_'+path+'.html', mode="rb").read()
            content = gzip.decompress(gzip_content).decode('gbk')
        context['content']=content
        if request.user.username == path:
            context['saveid']=sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]
        return HttpResponse(template.render(context,request))
    else:
        return HttpResponseRedirect('/login?next=/life/'+path)

def lifeAction(request):
    action = request.POST.get('action')
    if action is None:
        return HttpResponse('请求失败！')
    elif action == 'save':
        return saveLife(request)
    elif action == 'rollback':
        return showLifeList(request)

AUTO_SAVE_MAX = 5
SAVE_MAX = 5

def saveLife(request):
    saveid = request.POST.get('saveid')
    content = request.POST.get('content')
    auto = request.POST.get('autosave')
    if saveid != sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]:
        logger.error('Somebody tried to save without authentication.')
        return HttpResponse('保存失败，登录状态出现问题，或没有权限。')

    username = request.user.username

    # gzip压缩内容后保存
    gzip_content = gzip.compress(content.encode('gbk'))
    logger.info('Before zip: %d bytes, After zip, %d bytes', len(content.encode('gbk')), len(gzip_content))

    # 每个用户只保存5个auto和5个手动保存记录，按修改时间倒序，超过的删掉。
    # TODO: 此操作应设为脚本，而不是每次保存时调用
    life = sorted([x for x in os.listdir('./life') if x.startswith('life_'+username+'-')],key=lambda x:os.path.getmtime('./life/'+x), reverse=True)
    lifeauto = sorted([x for x in os.listdir('./life') if x.startswith('life_'+username+'_')],key=lambda x:os.path.getmtime('./life/'+x), reverse=True)
    if len(life) > SAVE_MAX:
        for i in range(SAVE_MAX,len(life)):
            os.remove('./life/'+life[i])
    if len(lifeauto)>AUTO_SAVE_MAX:
        for i in range(AUTO_SAVE_MAX,len(lifeauto)):
            os.remove('./life/'+lifeauto[i])

    if auto == '1':
        with open(datetime.datetime.now().strftime('./life/life_'+username+'_AUTOSAVE-%m:%d_%H:%M:%S.html'), mode="wb") as f:
            f.write(gzip_content)
    else:
        try:
            os.rename('./life/life_'+username+'.html',datetime.datetime.now().strftime('./life/life_'+username+'-%m:%d_%H:%M:%S.html'))
        except:
            pass
        with open('./life/life_'+username+'.html', mode="wb") as f:
            f.write(gzip_content)
    return HttpResponse('保存成功。')

def showLifeList(request):
    ret = {}
    saveid = request.POST.get('saveid')
    if saveid != sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]:
        ret['success']='false'
        ret['msg']='没有权限查看。'
        return HttpResponse(json.dumps(ret))

    username = request.user.username
    life=sorted([x for x in os.listdir('./life') if x.startswith('life_'+username+'-')],
                key=lambda x: os.path.getmtime('./life/'+x),reverse=True)
    lifeauto=sorted([x for x in os.listdir('./life') if x.startswith('life_'+username+'_')],
                    key=lambda x: os.path.getmtime('./life/'+x),reverse=True)
    if len(life)>SAVE_MAX:
        for i in range(SAVE_MAX,len(life)):
            os.remove('./life/'+life[i])
    if len(lifeauto)>AUTO_SAVE_MAX:
        for i in range(AUTO_SAVE_MAX,len(lifeauto)):
            os.remove('./life/'+lifeauto[i])
    lifemerge = sorted(life[:SAVE_MAX]+lifeauto[:AUTO_SAVE_MAX], key=lambda x: os.path.getmtime('./life/'+x), reverse=True)
    ret['success']='true'
    ret['length']=len(lifemerge)
    for i in range(len(lifemerge)):
        ret[str(i)]=lifemerge[i]
    return HttpResponse(json.dumps(ret))
