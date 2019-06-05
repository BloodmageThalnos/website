import os
import random
import subprocess
import urllib

import requests
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

def addMusic(request):
    url = request.POST.get("url")
    folder = request.POST.get("folder")
    name = request.POST.get("name")
    if not url or not folder or not name:
        return HttpResponse("fail to get url.")
    if not name.endswith(".mp3"):
        name = name + ".mp3"
    save_path = "./music/"+folder+"/"+name
    if not os.path.isdir("./music/"+folder):
        os.makedirs("./music/"+folder)

    # test download:
    r = requests.get(url, stream=True)
    MIN_FILE = 200*1024     # 200 KB
    MAX_FILE = 32*1024*1024 # 32 MB
    file_size = 0
    with open(save_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                file_size += 4096
                f.write(chunk)
                if file_size > MAX_FILE:
                    f.close()
                    os.remove(save_path)
                    return HttpResponse("file too big.")
    if not MIN_FILE < file_size:
        os.remove(save_path)
        return HttpResponse("file too small.")

    obj = subprocess.Popen(["coscmd upload "+save_path+" "+save_path[1:]]
                           , shell=True, universal_newlines=True)

    return HttpResponse("download success with upload returns: "+obj.stdout.read())

# unit test
# url: http://other.web.nc01.sycdn.kuwo.cn/resource/n1/7/8/3112388010.mp3
# folder: 19_summer
# name: dva