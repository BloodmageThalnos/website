import os
import sys
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'Website.settings'
django.setup()

from mainApp.models import *

articles = ArticleModel.objects.all()
for article in articles:
    pic_path = './images/upload'+article.cover_img[article.cover_img.rfind('/'):]
    print(pic_path)
    if os.path.isfile(pic_path):
        if not os.path.isfile(article.cover_img_thumb[1:]):
            thumb_from_cover_img(pic_path,pic_path+'_thumb'+pic_path[-6:])
            article.cover_img_thumb = '.'+pic_path+'_thumb'+pic_path[-6:]
            print('ok '+article.title)
    article.cover_img = '.'+pic_path
    article.save()
