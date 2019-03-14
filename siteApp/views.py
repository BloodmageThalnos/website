import logging
import json
from django.http import *
from django.template import loader
from django.contrib.auth import login

from django.shortcuts import render

# Create your views here.

def showHome(request):
    logging.info('Accessing Page home/ with showHome')
    template = loader.get_template('home.html')
    context = {}
    return HttpResponse(template.render(context, request))

