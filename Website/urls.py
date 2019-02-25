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
from django.urls import path
from mainApp import views as mainViews
from staticApp import views as staticViews

urlpatterns = [
    path('admin/', admin.site.urls),
    # old static pages
    path('s/<path:path>', staticViews.showPage),
    path('assets/<path:path>', staticViews.showAssets),
    path('images/<path:path>', staticViews.showImages),
    path('source/<path:path>', staticViews.showSource),

    path('', mainViews.showMainPage),
]
