import logging
import json
from django.http import *
from django.template import loader
from django.contrib.auth import login

from django.shortcuts import render

# Create your views here.

logger = logging.getLogger(__name__)

def showPage(request, path):
    logger.info('Accessing Page %s with showMainPage' % path)
    with open('./html/' + path, encoding='UTF-8') as f:
        html = f.read()
    return HttpResponse(html)

def showMusic(request, path):
    if path.endswith('mp3'):
        with open('./music/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="audio/mpeg3")


def showAssets(request, path):
    if path.endswith('css'):
        with open('./assets/' + path, encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html, content_type="text/css")

    if path.endswith('js'):
        with open('./assets/' + path, encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-javascript")

    if path.endswith('woff') or path.endswith('woff2'):
        with open('./assets/'+path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-woff")

    if path.endswith('ttf'):
        with open('./assets/'+path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-ttf")

    logging.info('Accessing /%s with showAssets matched nothing.' % path)
    return None


def showImages(request, path):
    if path.endswith('jpg') or path.endswith('jpeg'):
        with open('./images/'+path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="image/jpeg")
    if path.endswith('png'):
        with open('./images/'+path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="image/png")


    logging.info('Accessing /%s with showImages matched nothing.' % path)
    return None


def showSource(request, path):
    if path.endswith('cpp'):
        with open('./source/'+path, mode="r", encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html)

    logging.info('Accessing /%s with showSource matched nothing.' % path)
    return None

def showBin(request, path):
    if path.endswith('css'):
        with open('./bin/' + path, encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html, content_type="text/css")

    if path.endswith('js'):
        with open('./bin/' + path, encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-javascript")

    if path.endswith('woff') or path.endswith('woff2'):
        with open('./bin/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-woff")

    if path.endswith('ttf'):
        with open('./bin/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-ttf")

    logging.info('Accessing /%s with showBin matched nothing.' % path)
    return None

def showStatic(request, path):
    if path.endswith('dat'):
        with open('./static/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html)

    if path.endswith('png'):
        with open('./static/'+path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="image/png")

    if path.endswith('css'):
        with open('./static/' + path, encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html, content_type="text/css")

    if path.endswith('js'):
        with open('./static/' + path, encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-javascript")

    if path.endswith('woff') or path.endswith('woff2'):
        with open('./static/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-woff")

    if path.endswith('ttf'):
        with open('./static/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-ttf")

    logging.info('Accessing /%s with showBin matched nothing.' % path)
    return None

def showFont(request, path):
    if path.endswith('woff') or path.endswith('woff2'):
        with open('./fonts/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-woff")

    if path.endswith('ttf'):
        with open('./fonts/' + path, mode="rb") as f:
            html = f.read()
        return HttpResponse(html, content_type="application/x-font-ttf")

    logging.info('Accessing /%s with showFont matched nothing.' % path)
    return None