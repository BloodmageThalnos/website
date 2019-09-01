import gzip
import logging
import json
import subprocess

from .models import VisitModel, id_
from .view.music import *
from .view.life import *
from .view.quest import *

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
        user_id = request.user.id
        vm = VisitModel(user_id=user_id, user_ip=ip, b_id=id_(id), url=url, duration=0)
        vm.save()
        return HttpResponse(str(vm.id))
    elif act == '2':
        id = request.POST.get('i')
        time = int(request.POST.get('t')) # millisecond
        try:
            vm = VisitModel.objects.get(id=int(id))
        except:
            return None # 数据库中没有id，直接无视
        if time - vm.duration > 60 + vm.duration**0.5 or time < vm.duration: # 不合法的更新，无视之
            return None
        vm.duration = time
        vm.save()
        return HttpResponse(vm.id)
    else:
        pass # error act_id


# /debug/<slug:path>
# 显示 debug 用的一些后台页面，包括 errlog、infolog、doshelllog
# 访问dopullshell会执行服务器上的../do.sh，用来进行git pull等操作。
def showDebug(request, path=''):
    if request.user.username != "dva":
        return HttpResponseRedirect('/login?next=/__debug__/'+path)
    if path == '':
        template = loader.get_template('log.html')
        context = {"name": "View logs..."}
        return HttpResponse(template.render(context, request))
    elif path == 'errlog':
        with open('./log/err.log', mode='r', encoding='utf-8') as f:
            template = loader.get_template('log.html')
            context = {"name":"Error.log", "output": f.read()}
            return HttpResponse(template.render(context, request))

    elif path=='infolog':
        with open('./log/info.log', mode='r', encoding='utf-8') as f:
            template = loader.get_template('log.html')
            context = {"name":"Info.log", "output": f.read()}
            return HttpResponse(template.render(context, request))

    elif path=='doshelllog':
        with open('../do.txt', mode='r', encoding='utf-8') as f:
            template = loader.get_template('log.html')
            context = {"name":"Shell.log", "output": f.read()}
            return HttpResponse(template.render(context, request))

    elif path=='dopullshell':
        subprocess.Popen(["sleep 0.1 && sh ../do.sh > ../do.txt 2>&1"]
                             , shell=True, universal_newlines=True)
        return HttpResponse(
            '<html><head><meta http-equiv="refresh" content="3;url=/__debug__/doshelllog"></head></html>'
        )

    elif path=='clearlog':
        with open('./log/info.log', mode="w") as f:
            f.write('Log cleared. \n')
        with open('./log/err.log', mode="w") as f:
            f.write('Log cleared. \n')

    return HttpResponseRedirect('/__debug__/')