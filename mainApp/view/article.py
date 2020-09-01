from urllib.parse import quote

from django.db.models import Count
from django.http import HttpResponse, Http404
from django.template import loader

from mainApp.models import ArticleModel

ARTICLE_NUM_PER_PAGE = 8

# 显示文章列表（首页More articles进入）
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
    articles = ArticleModel.objects.filter(type__exact=1).order_by('-edit_date')
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
            'time':article.edit_date.strftime('%b %d, %Y'),
            'img':article.get_thumb(),
            'url':'/article-'+str(article.id),
        })
    context['articles']=arts

    template = loader.get_template('articles.html')
    return HttpResponse(template.render(context, request))


# 显示单篇文章
# /article-(?P<id>[0-9]+)
def showArticle(request, id_):
    try:
        articleId = int(id_)
        article = ArticleModel.objects.get(id=articleId)
    except:
        raise Http404('文章不存在，请联系dva处理。')
    if article.type != 1:
        raise Http404('文章待审核或已删除。')

    create_date = article.create_date
    create_date_str = create_date.strftime("%b %d, %Y")
    recomm = getRecommArticle(articleId)

    template = loader.get_template('readarticle.html')
    context = {
        'author': article.author_name,
        'title': article.title,
        'excerpt': article.excerpt,
        'content': article.content,
        'create_date': create_date_str,
        'recomm': recomm,
    }
    return HttpResponse(template.render(context, request))

# 文章内底部推荐阅读
# 目前策略：固定种子的随机三篇，除自身
# 返回 list of {'id', 'author', 'cover_img_thumb', 'excerpt', 'title', 'url'}
def getRecommArticle(aid, userid=0, count=3):
    import random
    random.seed(aid*37)
    articles = ArticleModel.objects.filter(type__exact=1)
    chosen = random.choices(articles, k=3)

    chosen_formatted = []
    for c in chosen:
        category = c.category
        if len(category)>30:
            category = category[:29] + '...'
        chosen_formatted.append({
            'id': c.id,
            'author': c.author_name,
            'img': c.get_thumb(),
            'excerpt': c.excerpt,
            'category': category,
            'title': c.title,
            'url':'/article-'+str(c.id),
        })
    return chosen_formatted
