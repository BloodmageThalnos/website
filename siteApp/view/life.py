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

from siteApp.models import VisitModel, LifeModel

logger = logging.getLogger(__name__)

# TODO: 操作不安全，应当设置随机token并存数据库
def createSaveId(request):
    return sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]

def checkSaveId(request, saveid):
    return saveid != sha256((request.user.username+str(request.user.id)).encode()).hexdigest()[16:48]

# 页面密码
def setPassword(userid, pageid, pwd):
    pwd_hash = sha256(pwd.encode()).hexdigest()[:32]
    try:
        life_model = LifeModel.objects.get(user_id=userid, page_id=pageid)
    except Exception as e:
        return False
    life_model.password = pwd_hash
    try:
        life_model.save()
    except Exception as e:
        logger.error("Set password error: "+e.__str__())
    return True

def checkPassword(userid, pageid, pwd):
    pwd_hash = sha256(pwd.encode()).hexdigest()[:32]
    life_model = LifeModel.objects.get(user_id=userid, page_id=pageid)
    if life_model is None:
        return False
    if life_model.password == pwd_hash:
        return True
    else:
        logger.info("Check password failed, userid:"+str(userid)+"pageid:"+str(pageid)+"pwd:"+pwd)
        return False

# /life/xx 页面的显示
def showLife(request, path):
    if not User.objects.filter(username__exact=path).count():
        # 用户不存在，自动跳转到from_user的主页
        return HttpResponseRedirect('/life/'+request.user.username)

    # 用户未登录，返回到登录界面
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login?next=/life/'+path)

    from_user = request.user
    to_user = User.objects.get(username=path)
    to_user_name = to_user.username
    dirname = to_user_name

    page = request.GET.get('page')

    if not page: # 未指定页面，（暂时）自动进入最新的那页
        latest_id = LifeModel.objects.filter(user_id=to_user.id).order_by('-page_id').first()
        if latest_id is None: # 说明用户的life页面第一次被打开，在这里进行初始化操作
            # auto 文件夹，用于存放自动保存的文件
            os.makedirs('./life/'+dirname+'/auto',exist_ok=True)  # exist_ok = true 防止多线程crash
            # example.html，最初打开的模板文件
            shutil.copyfile('./life/example.html','./life/'+dirname+'/example.html')
            # 初始化数据库
            life_model=LifeModel(user_id=to_user.id,page_id=1,p_alias="default page")
            life_model.save()
            page = '1'
        else:
            page = str(latest_id)

    if page != '1':
        dirname = dirname + '_p' + page
    if not os.path.exists('./life/'+dirname): # 页面不存在，跳转回to_user的主页
        logger.info('[life showLife] page not exist %s'%dirname)

        return HttpResponseRedirect('/life/'+path)

    try:
        pageid = int(page)
    except:
        return None # 错误：pageid 不是数字，直接返回

    try:
        life_model = LifeModel.objects.get(user_id=to_user.id, page_id=pageid)
    except:
        return None # 页面不存在

    # 访问记录
    try:
        ip = request.META['HTTP_X_FORWARDED_FOR'] if request.META.__contains__('HTTP_X_FORWARDED_FOR') else request.META[
            'REMOTE_ADDR']
        vm = VisitModel(user_id=request.user.id, user_ip=ip, b_id=request.user.username, url='/life/'+path, duration=0)
        vm.save()
    except Exception as e:
        logger.error("Error logging user in showLife："+e.__str__())

    template=loader.get_template('life.html')
    # 查看历史保存
    use = request.GET.get('use_saved')
    context = {}
    if use is not None:
        context['use_saved'] = True
        context['saved_filename'] = use
        if use.startswith("."):# 防 hack，开头不应有.
            return None
        if from_user.username != to_user_name: # 暂时写死一个权限控制：只有自己能看自己的历史记录
            return None
        if not os.path.exists('./life/'+dirname+'/'+use):
            return HttpResponse('use saved file not exists.')
        gzip_content = open('./life/'+dirname+'/'+use, mode="rb").read()
        content = gzip.decompress(gzip_content).decode('gbk')
    else:
        # 打开手动保存和自动保存中最近的一个。这个可以直接通过对比文件名比较，不过现在没有性能问题，先暴力比较文件最近修改时间
        # 每个用户只保存几个auto和几个手动保存记录，按修改时间倒序，超过的删掉。TODO: SHOULD UPDATE MINUTELY
        life=sorted([x for x in os.listdir('./life/'+dirname) ],
                    key=lambda x: os.path.getmtime('./life/'+dirname+'/'+x),reverse=True)
        lifeauto=sorted([x for x in os.listdir('./life/'+dirname+'/auto') ],
                    key=lambda x: os.path.getmtime('./life/'+dirname+'/auto/'+x),reverse=True)
        life.remove('auto') # 文件夹

        # 对于自动保存的，路径前面加上auto/，这样到时候直接'life/'+path就可以访问两种，避免到处判断
        for i in range(min(AUTO_SAVE_MAX,len(lifeauto))):
            lifeauto[i] = 'auto/'+lifeauto[i]

        life_max = max(life[:SAVE_MAX]+lifeauto[:AUTO_SAVE_MAX], key=lambda x: os.path.getmtime('./life/'+dirname+'/'+x))
        logger.info("lifes of "+to_user_name+": "+str(life[:SAVE_MAX]+lifeauto[:AUTO_SAVE_MAX]))
        logger.info("life_max = "+life_max)

        gzip_content = open('./life/'+dirname+"/"+life_max, mode="rb").read()
        content = gzip.decompress(gzip_content).decode('gbk')

    context['content']=content
    context['page']=page
    context['user']=to_user_name

    # 当前用户访问自己的主页，才能获得saveid(编辑权限)
    if from_user.username == to_user_name:
        context['saveid']=createSaveId(request)

    return HttpResponse(template.render(context,request))

def lifeAction(request):
    action = request.POST.get('action')
    if action is None:
        return None
    elif action == 'save':
        return saveLife(request)
    elif action == 'rollback':
        return showLifeList(request)
    elif action == 'listpage':
        return showPageList(request)
    elif action == 'addpage':
        return addPage(request)

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
    username = request.POST.get('user')
    userpage = username
    page = request.POST.get('page')
    if not page: # 无page参数，或为空
        page = '1'
    if page != '1':
        userpage = userpage + '_p' + page
        if not os.path.exists('./life/'+userpage):
            logger.info('[life showLife] page not exist %s'%userpage)
            return HttpResponseRedirect('/life/'+username) # 页面不存在，跳转回该用户主页
    os.makedirs('./life/'+userpage+'/auto', exist_ok=True) # exist_ok = true 防止多线程crash

    life=sorted([x for x in os.listdir('./life/'+userpage) ],
                key=lambda x: os.path.getmtime('./life/'+userpage+'/'+x),reverse=True)
    lifeauto=sorted([x for x in os.listdir('./life/'+userpage+'/auto') ],
                key=lambda x: os.path.getmtime('./life/'+userpage+'/auto/'+x),reverse=True)
    life.remove('auto') # 文件夹

    # 对于自动保存的，路径前面加上auto/，这样到时候直接'life/'+path就可以访问两种，避免到处判断
    for i in range(min(AUTO_SAVE_MAX,len(lifeauto))):
        lifeauto[i] = 'auto/'+lifeauto[i]

    lifemerge = sorted(life[:SAVE_MAX]+lifeauto[:AUTO_SAVE_MAX], key=lambda x: os.path.getmtime('./life/'+userpage+'/'+x), reverse=True)
    ret['success']='true'
    ret['length']=len(lifemerge)
    for i in range(len(lifemerge)):
        ret[str(i)]=lifemerge[i]
        ret['_'+str(i)]='/life/'+username+'?use_saved='+lifemerge[i]+'&page='+page
    return HttpResponse(json.dumps(ret))

def showPageList(request):
    ret = {}
    username = request.POST.get('user')
    try:
        userid = User.objects.get(username=username).id
        if userid is None: raise LookupError
    except:
        return None
    lifemodel = LifeModel.objects.filter(user_id=userid)
    ret['success']='true'
    ret['length']=lifemodel.count()
    i = 0
    for page in lifemodel:
        i += 1
        ret[str(i)]=page.page_id
        ret['_'+str(i)]=page.p_alias
    return HttpResponse(json.dumps(ret))

def addPage(request):
    ret = {}
    saveid = request.POST.get('saveid')
    if not checkSaveId(request, saveid):
        ret={'success':'false','msg':'没有权限查看。'}
        return HttpResponse(json.dumps(ret))
    username = request.user.username

    latest_id=LifeModel.objects.filter(user_id=request.user.id).order_by('-page_id').first()
    if latest_id is None:
        return None
    index = latest_id + 1
    dirname = username + "_p" + str(index)

    life_model = LifeModel(user_id=request.user.id,page_id=index,p_alias="default page "+str(index))
    life_model.save()

    os.makedirs('./life/' + dirname + '/auto', exist_ok=True)

    ret['success']='true'
    ret['url']='/life/' + username + '?page='+str(index)
    return HttpResponse(json.dumps(ret))

def delPage(request):
    pass