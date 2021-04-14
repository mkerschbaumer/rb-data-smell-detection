# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_protect

import os
import sys
from app.models import File, Column, DetectedSmell

cwd = os.getcwd()
sys.path.append("/home/loryg/Documents/Gitlab/bachelor-thesis/data_smell_detection/")
from datasmelldetection.detectors.great_expectations.dataset import GreatExpectationsDatasetManager

from datasmelldetection.core.detector import DetectionStatistics, DetectionResult
from datasmelldetection.core.datasmells import DataSmellType

def index(request):
    
    context = {}
    context['segment'] = 'index'

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))


def upload(request):
    context = {}
    if request.method == 'POST' and 'upload' in request.FILES:
        uploaded_file = request.FILES['upload']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)   
        context['size'] = fs.size(name) / 1000000
    else:
        context['message'] = 'no file selected'
    return render(request, 'index.html', context)


def smells(request):
    context = {}
    if request.method == 'POST':
      some_var = request.POST.getlist('smells')  
      context['list'] = some_var
    return render(request, 'customize.html', context)

def result(request):
    context = {}
    outer = os.path.join(os.getcwd(), '../')
    manager = GreatExpectationsDatasetManager(
        context_root_dir = os.path.join(outer, '../great_expectations'),
        data_directory = os.path.join(cwd, 'app/test_sets')
    )
    dataset = manager.get_dataset('Titanic.csv')
    column_names = precheck_columns(dataset.get_column_names())
    context['column_names'] = sorted(column_names)
    uploaded_file = os.path.join(cwd, 'app/test_sets')
    uploaded_file = File(path_to_file = os.path.join(uploaded_file, 'Titanic.csv'))
    
    statistic = DetectionStatistics(total_element_count = 50,faulty_element_count = 10)
    smell_results = [DetectionResult(data_smell_type = 'DummyValueSmell', column_name = 'Name', statistics = statistic, faulty_elements = list()), DetectionResult(data_smell_type = 'DummyValueSmell', column_name = 'Survived', statistics = statistic, faulty_elements = list()), DetectionResult(data_smell_type = 'DummyValueSmell', column_name = 'Age', statistics = statistic, faulty_elements = list()), DetectionResult(data_smell_type = 'MissingValueSmell', column_name = 'Name', statistics = statistic, faulty_elements = list())]
    sorted_results = sort_results(smell_results, column_names)
    context['results'] = sorted_results
    return render(request, 'results.html', context)


def sort_results(results, columns):
    sorted_results = {}
    for c in columns:
        sorted_results[c] = []
        for s in results:
            if s.column_name == c:
                sorted_results[c].append(s)
    return sorted_results

def precheck_columns(columns):
    if 'Unnamed: 0' in columns:
        columns.remove('Unnamed: 0')
    return columns

