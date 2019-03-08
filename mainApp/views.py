import logging
import json
from django.http import *
from django.template import loader
from django.contrib.auth import login
# from django import cache

from django.shortcuts import render

# Create your views here.

logger = logging.getLogger(__name__)

def showMainPage(request):
    logging.info('Accessing Page / with showMainPage')

    template = loader.get_template('root.html')
    context = {}
    return HttpResponse(template.render(context, request))


def showTestPage(request, path):
    # 显示所有文章

    template = loader.get_template('test.html')
    context = {
        '':'',
    }
    return HttpResponse(template.render(context, request))