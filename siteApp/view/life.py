import gzip
import logging
import json
import os
import shutil

from django.contrib.auth.models import User
from django.http import *
from django.template import loader
from hashlib import sha256
import datetime

logger = logging.getLogger(__name__)

def showLife(request, path):
    if not User.objects.filter(username__exact=path).count():
        return HttpResponseNotFound('用户不存在！')
    if request.user.is_authenticated:
        template=loader.get_template('life.html')
        use = request.GET.get('use_saved')
        context = {}
        username = path
        page = request.GET.get('page')
        if not page:
            page = '1'
        if page != '1':
            username = username + '_p' + page
        if use is not None:
            # 查看历史保存
            context['use_saved'] = True
            context['saved_filename'] = use
            # 安全性验证：use的开头不应有../这种
            if use.startswith("."): return None
            if not os.path.exists('./life/'+username+'/'+use):
                return HttpResponse('use saved file not exists.')
            gzip_content = open('./life/'+username+'/'+use, mode="rb").read()
            content = gzip.decompress(gzip_content).decode('gbk')
        else:
            if not os.path.exists('./life/'+username):
                os.makedirs('./life/'+username+'/auto', exist_ok=True) # exist_ok = true 防止多线程crash
                shutil.copyfile('./life/example.html','./life/'+username+'/example.html')

            # 打开手动保存和自动保存中最近的一个。这个可以直接通过对比文件名比较，不过现在没有性能问题，先暴力比较文件最近修改时间
            # 每个用户只保存几个auto和几个手动保存记录，按修改时间倒序，超过的删掉。TODO: SHOULD UPDATE MINUTELY
            life=sorted([x for x in os.listdir('./life/'+username) ],
                        key=lambda x: os.path.getmtime('./life/'+username+'/'+x),reverse=True)
            lifeauto=sorted([x for x in os.listdir('./life/'+username+'/auto') ],
                        key=lambda x: os.path.getmtime('./life/'+username+'/auto/'+x),reverse=True)
            life.remove('auto') # 文件夹
            if len(life)>SAVE_MAX:
                for i in range(SAVE_MAX,len(life)):
                    os.remove('./life/'+username+'/'+life[i])
            if len(lifeauto)>AUTO_SAVE_MAX:
                for i in range(AUTO_SAVE_MAX,len(lifeauto)):
                    os.remove('./life/'+username+'/auto/'+lifeauto[i])

            # 对于自动保存的，路径前面加上auto/，这样到时候直接'life/'+path就可以访问两种，避免到处判断
            for i in range(min(AUTO_SAVE_MAX,len(lifeauto))):
                lifeauto[i] = 'auto/'+lifeauto[i]

            life_max = max(life[:SAVE_MAX]+lifeauto[:AUTO_SAVE_MAX], key=lambda x: os.path.getmtime('./life/'+username+'/'+x))
            logger.info("lifes of "+username+": "+str(life[:SAVE_MAX]+lifeauto[:AUTO_SAVE_MAX]))
            logger.info("life_max = "+life_max)

            gzip_content = open('./life/'+username+"/"+life_max, mode="rb").read()
            content = gzip.decompress(gzip_content).decode('gbk')

        context['content']=content
        context['page']=page
        context['user']=username
        # 当前用户访问自己的主页，才能获得编辑权限
        if request.user.username == username:
            context['saveid']=sha256((username+str(request.user.id)).encode()).hexdigest()[16:48]
        return HttpResponse(template.render(context,request))
    else:
        return HttpResponseRedirect('/login?next=/life/'+path)

def lifeAction(request):
    action = request.POST.get('action')
    if action is None:
        return HttpResponse('请求失败！')
    elif action == 'save':
        return saveLife(request)
    elif action == 'rollback':
        return showLifeList(request)
    elif action == 'listpage':
        return showPageList(request)

AUTO_SAVE_MAX = 5
SAVE_MAX = 5

def saveLife(request):
    saveid = request.POST.get('saveid')
    content = request.POST.get('content')
    auto = request.POST.get('autosave')
    username = request.user.username
    if saveid != sha256((username+str(request.user.id)).encode()).hexdigest()[16:48]:
        return HttpResponse('保存失败，登录状态出现问题，或没有权限。')

    page = request.POST.get('page')
    if page is None:
        page = '1'
    if page != '1':
        username = username + '_p' + page
    os.makedirs('./life/' + username + '/auto', exist_ok=True)  # exist_ok = true 防止多线程crash

    # gzip压缩内容后保存
    gzip_content = gzip.compress(content.encode('gbk'))
    logger.info('Before zip: %d bytes, After zip, %d bytes', len(content.encode('gbk')), len(gzip_content))

    # 每个用户只保存几个auto和几个手动保存记录，按修改时间倒序，超过的删掉。
    # TODO: SHOULD UPDATE MINUTELY
    life=sorted([x for x in os.listdir('./life/'+username) ],
                key=lambda x: os.path.getmtime('./life/'+username+'/'+x),reverse=True)
    lifeauto=sorted([x for x in os.listdir('./life/'+username+'/auto') ],
                        key=lambda x: os.path.getmtime('./life/'+username+'/auto/'+x),reverse=True)
    life.remove('auto') # 文件夹
    if len(life)>SAVE_MAX:
        for i in range(SAVE_MAX,len(life)):
            os.remove('./life/'+username+'/'+life[i])
    if len(lifeauto)>AUTO_SAVE_MAX:
        for i in range(AUTO_SAVE_MAX,len(lifeauto)):
            os.remove('./life/'+username+'/auto/'+lifeauto[i])

    if auto == '1':
        os.makedirs('./life/'+username+'/auto', exist_ok=True)
        with open(datetime.datetime.now().strftime('./life/'+username+'/auto/%y%m%d_%H%M%S.html'), mode="wb") as f:
            f.write(gzip_content)
    else:
        os.makedirs('./life/'+username, exist_ok=True)
        with open(datetime.datetime.now().strftime('./life/'+username+'/%y%m%d_%H%M%S.html'), mode="wb") as f:
            f.write(gzip_content)
    return HttpResponse('保存成功。')

def showLifeList(request):
    ret = {}
    saveid = request.POST.get('saveid')
    if saveid != sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]:
        ret={'success':'false','msg':'没有权限查看。'}
        return HttpResponse(json.dumps(ret))
    username = request.user.username
    page = request.POST.get('page')
    if not page: # 无page参数，或为空
        page = '1'
    if page != '1':
        username = username + '_p' + page
    os.makedirs('./life/'+username+'/auto', exist_ok=True) # exist_ok = true 防止多线程crash

    # 每个用户只保存几个auto和几个手动保存记录，按修改时间倒序，超过的删掉。
    # TODO: SHOULD UPDATE MINUTELY
    life=sorted([x for x in os.listdir('./life/'+username) ],
                key=lambda x: os.path.getmtime('./life/'+username+'/'+x),reverse=True)
    lifeauto=sorted([x for x in os.listdir('./life/'+username+'/auto') ],
                key=lambda x: os.path.getmtime('./life/'+username+'/auto/'+x),reverse=True)
    life.remove('auto') # 文件夹
    if len(life)>SAVE_MAX:
        for i in range(SAVE_MAX,len(life)):
            os.remove('./life/'+username+'/'+life[i])
    if len(lifeauto)>AUTO_SAVE_MAX:
        for i in range(AUTO_SAVE_MAX,len(lifeauto)):
            os.remove('./life/'+username+'/auto/'+lifeauto[i])

    # 对于自动保存的，路径前面加上auto/，这样到时候直接'life/'+path就可以访问两种，避免到处判断
    for i in range(min(AUTO_SAVE_MAX,len(lifeauto))):
        lifeauto[i] = 'auto/'+lifeauto[i]

    lifemerge = sorted(life[:SAVE_MAX]+lifeauto[:AUTO_SAVE_MAX], key=lambda x: os.path.getmtime('./life/'+username+'/'+x), reverse=True)
    ret['success']='true'
    ret['length']=len(lifemerge)
    for i in range(len(lifemerge)):
        ret[str(i)]=lifemerge[i]
    return HttpResponse(json.dumps(ret))

def showPageList(request):
    ret = {}
    username = request.POST.get('user')

    # 每个用户只保存几个auto和几个手动保存记录，按修改时间倒序，超过的删掉。
    # TODO: SHOULD UPDATE MINUTELY
    life=[x for x in os.listdir('./life/') if x.startswith(username) ]
    ret['success']='true'
    ret['length']=len(life)
    for i in range(1, len(life)+1):
        ret[str(i)]=str(i)
        ret['_'+str(i)]=life[i-1] # TODO: 添加数据库，改为页名
    return HttpResponse(json.dumps(ret))
