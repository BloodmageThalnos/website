import logging
import json
from django.http import *
from django.template import loader
from django.contrib.auth import login
import subprocess

from django.shortcuts import render

# Create your views here.

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
            '<html><head><meta http-equiv="refresh" content="2;url=/__debug__/doshelllog"></head></html>'
        )

    return HttpResponse('502 error.')