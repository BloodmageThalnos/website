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
    domain = '/getmusic/'
    if os.path.isfile("./music_cdn.ini"): # use cdn 第一行YES表示使用，第二行为域名
        with open("./music_cdn.ini",mode="r",encoding="utf-8") as f:
            use = f.readline().split("#")[0].strip()
            if use == "YES":
                domain = f.readline()

    if os.path.isdir('./music/'+path):
        mfs = os.listdir('./music/'+path)
        random.shuffle(mfs)
    for mf in mfs:
        musics.append({
            'url': domain+path+'/'+mf,
            'title': mf.split('.')[0],
            'artist': 'LITTLEDVA'
        })
    context['musics']=musics
    context['lists']=dirs
    return HttpResponse(template.render(context, request))
