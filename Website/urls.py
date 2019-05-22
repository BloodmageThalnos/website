from django.contrib import admin
from django.urls import path, re_path
from staticApp import views as staticViews
from TexasAPP import views as texasViews
from captchaApp import views as captViews
from siteApp import views as siteViews
from mainApp import views as mainViews
from loginApp import views as loginViews

urlpatterns = [
    path('admin/', admin.site.urls),

    # old static pages, some of them are taken over by nginx
    path('s/<path:path>', staticViews.showPage),
    path('assets/<path:path>', staticViews.showAssets),
    path('images/<path:path>', staticViews.showImages),
    path('source/<path:path>', staticViews.showSource),
    path('bin/<path:path>', staticViews.showBin),
    path('fonts/<path:path>', staticViews.showFont),
    path('getmusic/<path:path>', staticViews.showMusic),
    path('static/<path:path>', staticViews.showStatic),

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
    re_path('^home/?$', mainViews.showMainPage),
    re_path('^articles/?$', mainViews.showArticlesPage),
    re_path(r'^article-(?P<id>[0-9]+)/$',mainViews.showArticle),
    path('action', mainViews.action),
    path('postDisqus', mainViews.postDisqus),
    re_path('^disqus/?$', mainViews.showDisqus),

    # music
    path('music/<slug:path>', siteViews.showMusic),

    # life app
    path('life/__action', siteViews.lifeAction),
    path('life/<slug:path>', siteViews.showLife),

    # login app
    path('login', loginViews.showLoginPage),
    path('dologin', loginViews.doLogin),
    path('doregister', loginViews.doRegister),
    path('dologout', loginViews.doLogout),

    # site management
    path('__admin__/upload', siteViews.showUploadArticle),
    path('__debug__/<slug:path>', siteViews.showDebug),
    path('__admin__/statics', siteViews.showStatistics),
    path('visit',siteViews.doVisit),

    # main page
    path('', siteViews.showRoot),
]
