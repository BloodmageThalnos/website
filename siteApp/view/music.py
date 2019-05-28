import os
import random

from django.http import HttpResponse
from django.template import loader


def showMusic(request, path):
    template = loader.get_template('music.html')
    context = {}
    musics = []
    dirs = os.listdir('./music')
    mfs = []
    if os.path.isdir('./music/'+path):
        mfs = os.listdir('./music/'+path)
        random.shuffle(mfs)
    for mf in mfs:
        musics.append({
            'url': '/getmusic/'+path+'/'+mf,
            'title': mf.split('.')[0],
            'artist': 'LITTLEDVA'
        })
    context['musics']=musics
    context['lists']=dirs
    return HttpResponse(template.render(context, request))