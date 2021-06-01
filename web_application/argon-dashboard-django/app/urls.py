# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.upload, name='upload'),

    re_path('customize.html', views.customize, name='customize'),

    re_path('results.html', views.result, name='result'),

    re_path('saved.html', views.saved, name='saved'),
    
    re_path(r'^.*\.*', views.pages, name='pages'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)