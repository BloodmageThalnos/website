import logging
from django.http import HttpResponse
from django.template import loader

from .view.article import showArticlesPage, showArticle
from .view.articleAction import action
from .view.disqus import postDisqus, showDisqus
from .view.mainPage import showMainPage
