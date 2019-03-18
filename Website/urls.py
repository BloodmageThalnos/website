"""Website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from mainApp import views as mainViews
from staticApp import views as staticViews
from TexasAPP import views as texasViews
from captchaApp import views as captViews
from siteApp import views as siteViews
from mainApp import views as mainViews

urlpatterns = [
    path('admin/', admin.site.urls),

    # old static pages, some of them are taken over by nginx
    path('s/<path:path>', staticViews.showPage),
    path('assets/<path:path>', staticViews.showAssets),
    path('images/<path:path>', staticViews.showImages),
    path('source/<path:path>', staticViews.showSource),
    path('bin/<path:path>', staticViews.showBin),
    path('fonts/<path:path>', staticViews.showFont),

    # texas calculator function
    path('texas/<slug:path>', texasViews.showPages),

    # captcha function
    path('captcha/index', captViews.showIndex),
    path('captcha/get', captViews.getCaptcha),
    path('captcha/check', captViews.checkCaptcha),
    path('captcha/upload', captViews.upload),
    path('captcha/uploadit', captViews.showUpload),
    path('captcha/img/<slug:path>', captViews.showCaptcha),
    # path('captcha/', captViews.),

    # new website
    path('home/', mainViews.showMainPage),
    re_path(r'^article-(?P<id>[0-9]+)/$',mainViews.showArticle),
    path('action/', mainViews.action),
    path('uploadArticle/', siteViews.showUploadArticle),

    # showlog
    path('__debug__/<slug:path>', mainViews.showDebug),
    path('test/', mainViews.showTestPage),
    path('cv', siteViews.showCv),

    # main page
    path('', siteViews.showRoot),
]
