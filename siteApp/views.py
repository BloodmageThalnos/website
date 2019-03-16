import logging
import json
from django.http import *
from django.template import loader
from django.contrib.auth import login

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