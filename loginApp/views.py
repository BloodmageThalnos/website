from django.http import *
from django.contrib.auth import *
from django.template import loader
from django.contrib.auth.models import User
from django.shortcuts import render

# Create your views here.


def showLoginPage(request):
    template=loader.get_template('login.html')
    nextpage = request.GET.get('next')
    context={}
    if nextpage is not None:
        context['next']=nextpage
    return HttpResponse(template.render(context,request))


def doLogout(request):
    logout(request)
    nextpage = request.GET.get('next')
    return HttpResponseRedirect(nextpage if nextpage else '/home')



def doLogin(request):
    name = request.POST.get('name')
    password = request.POST.get('password')
    if name is None or password is None:
        return HttpResponseRedirect('/login')
    nextpage = request.POST.get('next')
    user=authenticate(request,username=name,password=password)
    if user is not None:
        login(request,user)
        return HttpResponseRedirect(nextpage if nextpage else '/home')
    else:
        template=loader.get_template('login.html')
        context={'logerror':True, 'logerrormsg':'登录失败，用户名或密码错误。'}
        if nextpage is not None:
            context['next']=nextpage
        return HttpResponse(template.render(context,request))

def doRegister(request):
    name = request.POST.get('name')
    password = request.POST.get('password')
    if name is None or password is None:
        return HttpResponseRedirect('/login')
    nextpage = request.POST.get('next')
    if User.objects.filter(username__exact=name).count() > 0:
        template=loader.get_template('login.html')
        context={'regerror':True, 'regerrormsg':'注册失败，用户已存在。'}
        if nextpage is not None:
            context['next']=nextpage
        return HttpResponse(template.render(context,request))
    else:
        User.objects.create_user(username=name, password=password, email='')
        user=authenticate(request,username=name,password=password)
        login(request,user)
        return HttpResponseRedirect(nextpage if nextpage else '/home')
