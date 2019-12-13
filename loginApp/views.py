# coding=utf-8
from django.http import *
from django.contrib.auth import *
from django.template import loader
from django.contrib.auth.models import User

# /login 显示登录页面
def showLoginPage(request, error=''):
    template=loader.get_template('login.html')
    next_page = request.GET.get('next')
    context = {}
    if next_page is not None:
        # 有时为了方便做“需要登录才能下一步”的页面，会写成跳转到 /login?next=/[REAL_PAGE] ，所以这里加一个判断，如果已登录就直接跳转
        if request.user.is_authenticated:
            return HttpResponseRedirect(next_page)

        context['next'] = next_page
    # 没有 next_page 时访问页面，会返回 Logout 页面（也写在 login.html 里了）
    return HttpResponse(template.render(context, request))


def doLogout(request):
    logout(request)
    next_page = request.GET.get('next')
    return HttpResponseRedirect(next_page if next_page else '/home')

# /dologin 登录动作
def doLogin(request):
    name = request.POST.get('name')
    password = request.POST.get('password')

    if name is None or password is None:
        return showLoginPage(request)

    next_page = request.POST.get('next')
    user = authenticate(request, username=name, password=password)
    if user is not None:
        login(request, user)

        # 登陆成功，跳转到 nextpage 或主页
        resp = HttpResponseRedirect(next_page if next_page else '/home')

        return resp
    else:
        template = loader.get_template('login.html')
        context = {'logerror':True, 'logerrormsg':'登录失败，用户名或密码错误。'}
        if next_page is not None:
            context['next'] = next_page
        return HttpResponse(template.render(context, request))


def doRegister(request):
    name = request.POST.get('name')
    password = request.POST.get('password')
    if name is None or password is None:
        return HttpResponseRedirect('/login')
    next_page = request.POST.get('next')
    if User.objects.filter(username__exact=name).count():  # != 0
        template=loader.get_template('login.html')
        context={'regerror': True, 'regerrormsg': '注册失败，用户已存在。'}
        if next_page is not None:
            context['next'] = next_page
        return HttpResponse(template.render(context, request))
    else:
        User.objects.create_user(username=name, password=password, email='')
        user=authenticate(request,username=name,password=password)
        login(request,user)
        return HttpResponseRedirect(next_page if next_page else '/home')
