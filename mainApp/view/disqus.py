import datetime
import json
import random
import os
from string import ascii_lowercase, ascii_uppercase
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone

from mainApp.models import DisqusModel

# 从数据库中提取、处理并返回聊天版页面的内容，包括：
#  id：html中div的id
#  nickname：昵称
#  username：用户名
#  content：内容
#  hasimg：布尔，是否有图片
#  picture：如果有图片，图片的url
#  time：消息发送时间
#  color：消息颜色
# 【耦合】此函数在mainPage中复用
def getDisqus(num=0):
    dm = DisqusModel.objects.order_by('-c_time')
    if 0 < num <= dm.count():
        dm = dm[:num]
    ret = []
    for d in dm:
        now = {
            'id': 'disq_'+str(d.id),
            'nickname': d.nickname,
            'username': d.username,
            'content': d.content,
            'hasimg': d.picture!='',
            'picture': '/images/upload/'+d.picture,
            'time': d.c_time.isoformat(' '),
            'color': d.color,
        }
        if d.avatar!='':
            now['avatar']='/images/upload/'+d.avatar
        else:
            avatars = os.listdir('./images/avatar')
            hash = sum(ord(x) for x in d.nickname)
            now['avatar']='/images/avatar/'+avatars[hash%len(avatars)]
            # 从系统中随机选择图片作为头像
        ret.append(now)
    return ret


# 显示留言板详情页面
# /disqus
def showDisqus(request):
    disquses = getDisqus()
    template=loader.get_template('Disqus.html')
    context={
        'disquses': disquses,
    }
    return HttpResponse(template.render(context,request))


# 发表留言
def postDisqus(request):
    if DisqusModel.objects.last().c_time > timezone.now()-datetime.timedelta(seconds=5):
        return HttpResponse(json.dumps({
            'success': 'false',
            'msg': '发送留言间隔太短，请稍后再试！',
        }))

    userid = 0 # TODO: 用户系统上线后修改
    avatar = request.FILES.get('avatar')
    nickname = request.POST.get('nickname')
    color = request.POST.get('color')
    if userid == 0:
        ip=request.META['HTTP_X_FORWARDED_FOR']if request.META.__contains__('HTTP_X_FORWARDED_FOR')else request.META['REMOTE_ADDR']
        username = '游客 from '+ip
    else:
        username = '...'
    content = request.POST.get('content')
    pic = request.FILES.get('pic')
    reply_to = 0
    # TODO: 回复功能待添加
    # TODO: 判断上传的是不是图片、头像大小太大时进行压缩

    if len(nickname)>12:
        return HttpResponse(json.dumps({
            'success': 'false',
            'msg': '昵称太长！',
        }))

    if len(content)<2 or len(nickname)<2:
        return HttpResponse(json.dumps({
            'success': 'false',
            'msg': '字数太少或昵称太短！',
        }))

    if len(content)>50 or sum(1 for x in content if x=='\n')>3:
        return HttpResponse(json.dumps({
            'success': 'false',
            'msg': '字数太长或换行过多！',
        }))

    pic_name = ''
    if pic is not None:
        pic_name='disq'+''.join(random.choice(ascii_lowercase+ascii_uppercase) for _ in range(6))+pic.name[-6:]
        pic_url='./images/upload/'+pic_name
        with open(pic_url,mode='wb') as f:
            for chunk in pic.chunks():
                f.write(chunk)
    ava_name = ''
    if avatar is not None:
        ava_name='disq'+''.join(random.choice(ascii_lowercase+ascii_uppercase) for _ in range(6))+avatar.name[-6:]
        ava_url='./images/upload/'+ava_name
        with open(ava_url,mode='wb') as f:
            for chunk in avatar.chunks():
                f.write(chunk)
    dm = DisqusModel(
        user_id = userid,
        avatar = ava_name,
        nickname = nickname,
        username = username,
        content = content,
        picture = pic_name,
        color = color,
        reply_to = reply_to,
    )
    dm.save()
    return HttpResponse(json.dumps({
        'success': 'true',
    }))
