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
            'pic': './img/' + record.hash,
            'wrong_time': record.wrong_times + 1,
        })

    # 大侠榜，对所有有成功提交记录的用户，统计其做对的题目数量并排序
    heroes = CaptchaRecord.objects.filter(correct__exact=1).exclude(user__exact='') \
        .values('user', 'pic').distinct().values('user').annotate(dcount=Count('user')).order_by('-dcount')
    # logger.info(heroes)
    het = []
    for hero in heroes:
        het.append({
            'user': hero['user'],
            'count': hero['dcount'],
            'caption': ('大侠' if hero['dcount'] >= 5 else ('小侠' if hero['dcount'] >= 2 else '游客'))
        })

    template = loader.get_template('captcha.html')
    context = {
        'records': ret,
        'heroes': het,
    }
    return HttpResponse(template.render(context, request))


def showUpload(request):
    global captchaList
    captchaList = os.listdir("./captcha")
    random.shuffle(captchaList)
    urls = []
    count = 0
    for captcha in captchaList:
        it = CaptchaRecord.objects.filter(pic__exact="./captcha/"+captcha).first()
        if it is None:
            it = CaptchaRecord.objects.filter(pic__exact="./captcha/"+captcha[:-10]+".jpg").first()
        if it is None:
            CaptchaRecord(hash=str(random.randint(0,1e12)), answer='', pic="./captcha/"+captcha, user='').save()
            it = CaptchaRecord.objects.filter(pic__exact="./captcha/" + captcha).first()
        urls.append({'id':count, 'u':'./img/'+it.hash})
        count+=1
    template = loader.get_template('captchaUpload.html')
    context = {
        'urls': urls,
    }
    return HttpResponse(template.render(context, request))


# get {id, username}
# return {success, id, ans_hash, pic_url}
def getCaptcha(request):
    _hash = request.POST.get('id')
    # logger.info(_hash)
    if _hash is None:
        ret = {'success': 'false'}
        return HttpResponse(json.dumps(ret))
    try:
        CaptchaRecord.objects.get(hash=_hash)
    except:
        pass
    else:
        ret = {'success': 'false'}
        return HttpResponse(json.dumps(ret))
    user = request.POST.get('user')
    pic, ans = randomCaptcha()
    cr = CaptchaRecord(hash=_hash, answer=ans, pic=pic, user=(user if user is not None else ''))
    cr.save()
    ans_sha = sha256(ans.encode('utf-8')).hexdigest()
    ret = {'success': 'true', 'id': _hash, 'ans_hash': ans_sha, 'pic_url': './img/' + _hash}
    return HttpResponse(json.dumps(ret))


def showCaptcha(request, path):
    try:
        record = CaptchaRecord.objects.get(hash=path)
    except:
        return HttpResponse(None)
    else:
        if record.pic[-5] == '_':
            name = record.pic
        else:  # 兼容旧代码
            name = record.pic[:-4] + '_0001_.jpg'
        try:   # 正常返回
            return HttpResponse(open(name, mode="rb"), content_type="image-jpeg")
        except FileNotFoundError: # 兼容已被删除的题目
            return HttpResponseRedirect('/images/deleted.jpg')


# get {id, ans}
# return {success}
def checkCaptcha(request):
    _hash = request.POST.get('id')
    ans = request.POST.get('ans')
    user = request.POST.get('user')
    if _hash is None:
        ret = {'success': 'false'}
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
        ret = {'success': 'false'}
        return HttpResponse(json.dumps(ret))

captchaList = os.listdir("./captcha")
# return pic_url, answer
def randomCaptcha():
    it = random.choice(captchaList)
    ans = it[:-10]
    return './captcha/' + it, ans

def upload(request):
    ans = request.POST.get('ans')
    pic = request.FILES.get('pic')
    if ans is None or pic is None:
        ret = {'success': 'false'}
        return HttpResponse(json.dumps(ret))
    file_name = './captcha/' + ans + '_' + str(random.randint(1000, 9999)) + '_.jpg'
    logger.info(file_name)
    with open(file_name, 'wb') as f:
        for chunk in pic.chunks():
            f.write(chunk)
    ret = {'success': 'true'}
    global captchaList
    captchaList = os.listdir("./captcha")
    return HttpResponse(json.dumps(ret))
