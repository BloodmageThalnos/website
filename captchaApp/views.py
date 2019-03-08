from django.shortcuts import render
import os
import random
import logging
import json
from django.http import *
from django.template import loader
from django.db.models import *
from hashlib import sha256

from .models import *

logger = logging.getLogger(__name__)
captchaList = os.listdir("./captcha")

# Create your views here.
def showIndex(request):
    # with open('templates/captcha.html', encoding="UTF-8") as f:
    #    html = f.read()
    #    return HttpResponse(html)

    # 提交记录，选择所有成功了且输入了用户名的用户
    records = CaptchaRecord.objects.filter(correct__exact=1).exclude(user__exact='')
    ret = []
    for record in records:
        ret.append({
            'user': record.user,
            'pic': './img/'+record.hash,
            'wrong_time': record.wrong_times+1,
        })

    # 大侠榜，对所有有成功提交记录的用户，
    heroes = CaptchaRecord.objects.filter(correct__exact=1).exclude(user__exact='')\
        .values('user','pic').distinct().values('user').annotate(dcount=Count('user')).order_by('-dcount')
    # logger.info(heroes)
    het = []
    for hero in heroes:
        het.append({
            'user': hero['user'],
            'count': hero['dcount'],
            'caption': ('大侠' if hero['dcount']>=5 else('小侠' if hero['dcount']>=2 else '游客'))
        })

    template = loader.get_template('captcha.html')
    context = {
        'records': ret,
        'heroes': het,
    }
    return HttpResponse(template.render(context,request))

# get {id, username}
# return {success, id, ans_hash, pic_url}
def getCaptcha(request):
    _hash = request.POST.get('id')
    # logger.info(_hash)
    if _hash is None:
        ret = {'success':'false'}
        return HttpResponse(json.dumps(ret))
    try:
        CaptchaRecord.objects.get(hash=_hash)
    except:
        pass
    else:
        ret = {'success':'false'}
        return HttpResponse(json.dumps(ret))
    user = request.POST.get('user')
    pic, ans = randomCaptcha()
    cr = CaptchaRecord(hash=_hash, answer=ans, pic=pic, user=(user if user is not None else ''))
    ans_sha = sha256(ans.encode('utf-8')).hexdigest()
    cr.save()
    ret = {'success':'true', 'id':_hash, 'ans_hash':ans_sha, 'pic_url':'./img/'+_hash}
    return HttpResponse(json.dumps(ret))

def showCaptcha(request, path):
    try:
        record = CaptchaRecord.objects.get(hash=path)
    except:
        return HttpResponse(None)
    else:
        return HttpResponse(open(record.pic,mode="rb"), content_type="image-jpeg")

# get {id, ans}
# return {success}
def checkCaptcha(request):
    _hash = request.POST.get('id')
    ans = request.POST.get('ans')
    user = request.POST.get('user')
    if _hash is None:
        ret = {'success':'false'}
        return HttpResponse(json.dumps(ret))
    try:
        record = CaptchaRecord.objects.get(hash=_hash)
        if record.user == '' and user is not None:
            record.user = user
            record.save()
        if record.answer == ans:
            record.correct = 1
            record.save()
            ret = {'success': 'true'}
            return HttpResponse(json.dumps(ret))
        else:
            record.wrong_times += 1
            record.save()
            ret = {'success': 'false'}
            return HttpResponse(json.dumps(ret))
    except:
        ret = {'success':'false'}
        return HttpResponse(json.dumps(ret))

# return pic_url, answer
def randomCaptcha():
    it = random.choice(captchaList)
    ans = it[:-4]
    return './captcha/'+it, ans