import logging
from django.http import *
from django.template import loader
from django.contrib.auth import login

# Create your views here.

logger = logging.getLogger(__name__)

def showPage(request, path):
    logger.info('Accessing Page %s with showMainPage' % path)
    try:
        with open('./html/' + path, encoding='UTF-8') as f:
            html = f.read()
        return HttpResponse(html)
    except FileNotFoundError:
        logger.error('File not found: %s' % path)
        return HttpResponse(None)

def showMusic(request, path):
    try:
        if path.endswith('mp3'):
            with open('./music/' + path, mode="rb") as f:
                html = f.read()
            return HttpResponse(html, content_type="audio/mpeg3")
        if path.endswith('m4a'):
            with open('./music/' + path, mode="rb") as f:
                html = f.read()
            return HttpResponse(html, content_type="audio/mp4")
    except FileNotFoundError:
        logger.error('File not found: %s' % path)
        return HttpResponse(None)

def showAssets(request, path):
    try:
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
    except FileNotFoundError:
        logger.error('File not found: %s' % path)

    logging.info('Accessing /%s with showAssets matched nothing.' % path)
    return HttpResponse(None)


def showImages(request, path):
    try:
        suf2typ = {
            'jpg': 'image/jpeg',
            'jpe': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif', 
            'ico': 'image/x-icon',
            'tiff': 'image/tiff',
            'tif': 'image/tiff',
            'net': 'image/pnetvue',
            'png': 'image/png',
            'wbmp': 'image/vnd.wap.wbmp',
            'pdf': 'application/pdf',
            'mpeg': 'video/mpeg',
            'mpg': 'video/mpeg',
            'mp4': 'video/mpeg4',
            'mp3': 'audio/mp3'
        }
        for suffix in suf2typ.keys():
            if path.endswith(suffix):
                with open('./images/'+path, mode="rb") as f:
                    html = f.read()
                return HttpResponse(html, content_type=suf2typ[suffix])
    except FileNotFoundError:
        logger.error('File not found: %s' % path)

    logging.info('Accessing /%s with showImages matched nothing.' % path)
    return HttpResponse(None)


def showSource(request, path):
    try:
        if path.endswith('cpp'):
            with open('./source/'+path, mode="r", encoding='UTF-8') as f:
                html = f.read()
            return HttpResponse(html)
    except FileNotFoundError:
        logger.error('File not found: %s' % path)

    logging.info('Accessing /%s with showSource matched nothing.' % path)
    return HttpResponse(None)

def showBin(request, path):
    try:
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

        if path.endswith('svg'):
            with open('./bin/' + path, mode="rb") as f:
                html = f.read()
            return HttpResponse(html, content_type="text/xml")
    except FileNotFoundError:
        logger.error('File not found: %s' % path)

    logging.info('Accessing /%s with showBin matched nothing.' % path)
    return HttpResponse(None)

def showStatic(request, path):
    try:
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
    except FileNotFoundError:
        logger.error('File not found: %s' % path)

    logging.info('Accessing /%s with showBin matched nothing.' % path)
    return HttpResponse(None)

def showFont(request, path):
    try:
        if path.endswith('woff') or path.endswith('woff2'):
            with open('./fonts/' + path, mode="rb") as f:
                html = f.read()
            return HttpResponse(html, content_type="application/x-font-woff")

        if path.endswith('ttf'):
            with open('./fonts/' + path, mode="rb") as f:
                html = f.read()
            return HttpResponse(html, content_type="application/x-font-ttf")
    except FileNotFoundError:
        logger.error('File not found: %s' % path)

    logging.info('Accessing /%s with showFont matched nothing.' % path)
    return HttpResponse(None)