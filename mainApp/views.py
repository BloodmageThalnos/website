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
    return HttpResponseRedirect('/s/index.html')

def showPages(request, path):
    pass