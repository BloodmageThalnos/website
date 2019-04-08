from django.contrib import admin
from django.urls import path, re_path
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

    # personal cv function
    path('cv', siteViews.showCv),

    # new website
    path('home', mainViews.showMainPage),
    path('home/', mainViews.showMainPage),
    re_path(r'^article-(?P<id>[0-9]+)/$',mainViews.showArticle),
    path('action', mainViews.action),
    path('postDisqus', mainViews.postDisqus),
    path('disqus', mainViews.showDisqus),
    path('disqus/', mainViews.showDisqus),

    # site management
    path('__admin__/upload', siteViews.showUploadArticle),
    path('__debug__/<slug:path>', siteViews.showDebug),
    path('__admin__/statics', siteViews.showStatistics),
    path('visit',siteViews.doVisit),

    # main page
    path('', siteViews.showRoot),
]
