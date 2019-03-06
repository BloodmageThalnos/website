import logging
import json
from django.http import *
from django.template import loader
from django.contrib.auth import login

from django.shortcuts import render

# Create your views here.

logger = logging.getLogger(__name__)

def showMainPage(request):
    logging.info('Accessing Page / with showMainPage')
    #return HttpResponseRedirect('/s/index.html')
    template = loader.get_template('root.html')
    context = {}
    return HttpResponse(template.render(context, request))


def showPages(request, path):
    pass