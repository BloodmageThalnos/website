from urllib.parse import quote

from django.db.models import Count
from django.http import HttpResponse
from django.template import loader

from mainApp.models import ArticleModel

ARTICLE_NUM_PER_PAGE = 8

def showArticlesPage(request):
    context = {}
    pageno = request.GET.get('page')
    try:
        pageno = int(pageno)
    except:
        pageno = 1
    context['hasnextpage'] = (pageno != 1)
    context['nextpage'] = pageno - 1
    context['lastpage'] = pageno + 1

    categories=ArticleModel.objects.filter(type__lt=3).values('category').annotate(dcount=Count('category')).order_by(
        '-dcount')
    sections = []
    for category in categories:
        sections.append({
            'name': category['category'] if category['category']!='' else '无分类',
            'count': category['dcount'],
            'url': '/articles?page=1&category='+quote(category['category']),
            'highlight': False,
        })
    context['sections']=sections

    indstart = (pageno-1)*ARTICLE_NUM_PER_PAGE
    indend = pageno*ARTICLE_NUM_PER_PAGE
    articles = ArticleModel.objects.order_by('-edit_date')
    a_cnt = articles.count()
    if indstart >= a_cnt:
        indstart = indend = 0
    elif indend > a_cnt:
        indend = a_cnt
    articles = articles[indstart:indend]
    arts = []
    for article in articles:
        excerpt = article.excerpt
        if len(excerpt)>30: excerpt = excerpt[:30]+'...'
        arts.append({
            'title':article.title,
            'context':excerpt,
            'time':article.edit_date,
            'img':article.get_thumb(),
            'url':'/article-'+str(article.id),
        })
    context['articles']=arts

    template = loader.get_template('articles.html')
    return HttpResponse(template.render(context, request))


# 显示单篇文章
# /article-(?P<id>[0-9]+)
def showArticle(request, id_):
    articleId = int(id_)
    article = ArticleModel.objects.get(id=articleId)

    template = loader.get_template('readarticle.html')
    context = {
        'author': article.author_name,
        'title': article.title,
        'excerpt': article.excerpt,
        'content': article.content,
    }
    return HttpResponse(template.render(context, request))