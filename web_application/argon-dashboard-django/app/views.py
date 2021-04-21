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
from django.core.cache import cache
import os
import sys
import datetime
from app.models import File, Column, DetectedSmell, SmellType
from django.contrib.auth.models import User

cwd = os.getcwd()
sys.path.append("/home/loryg/Documents/Gitlab/bachelor-thesis/data_smell_detection/")
from datasmelldetection.detectors.great_expectations.dataset import GreatExpectationsDatasetManager
from datasmelldetection.detectors.great_expectations.context import GreatExpectationsContextBuilder
from datasmelldetection.detectors.great_expectations.detector import DetectorBuilder
from datasmelldetection.detectors.great_expectations.detector import GreatExpectationsDetector

from datasmelldetection.core.detector import DetectionStatistics, DetectionResult
from datasmelldetection.core.datasmells import DataSmellType

outer = os.path.join(os.getcwd(), "../")


context_builder = GreatExpectationsContextBuilder(
    os.path.join(outer, "../great_expectations"),
    os.path.join(cwd, "core/media")
)
con = context_builder.build()

manager = GreatExpectationsDatasetManager(context=con)

dataset = None
column_names = None
detector = None
supported_smells = None

dummy_user = User(username="dummy_user")
#dummy_user.save()

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
        actual_name = context['url'].replace('/media/', '')
        if request.user.is_authenticated:
            file1 = File(path_to_file=actual_name, user=request.user)
            file1.save()
        else:
            file1 = File(path_to_file=actual_name, user=dummy_user)
            file1.save()
        
        print(actual_name)
        dataset = manager.get_dataset(actual_name)
        column_names = precheck_columns(dataset.get_column_names())
        detector = DetectorBuilder(context=con, dataset=dataset).build()
        supported_smells = detector.get_supported_data_smell_types()
        for s in supported_smells:
            smell = SmellType(smell_type=s.value)
            smell.save()
            smell.belonging_file.add(file1)
            print(s)
        

    else:
        context['message'] = 'no file selected'
    return render(request, 'index.html', context)


def smells(request):
    

    believability_smells = [DataSmellType.DUMMY_VALUE_SMELL, DataSmellType.DUPLICATED_VALUE_SMELL, DataSmellType.EXTREME_VALUE_SMELL, DataSmellType.MEANINGLESS_VALUE_SMELL, DataSmellType.MISSPELLING_SMELL, DataSmellType.SUSPECT_CLASS_VALUE_SMELL, DataSmellType.SUSPECT_DATE_VALUE_SMELL, DataSmellType.SUSPECT_DATE_TIME_INTERVAL_SMELL, DataSmellType.SUSPECT_SIGN_SMELL, DataSmellType.SUSPECT_DISTRIBUTION_SMELL]
    syntactic_understandability_smells = [DataSmellType.AMBIGUOUS_DATE_TIME_FORMAT_SMELL, DataSmellType.AMBIGUOUS_VALUE_SMELL, DataSmellType.CASING_SMELL, DataSmellType.CONTRACTING_SMELL, DataSmellType.EXTRANEOUS_VALUE_SMELL, DataSmellType.INTERMINGLED_DATA_TYPE_SMELL, DataSmellType.LONG_DATA_VALUE_SMELL, DataSmellType.MISSING_VALUE_SMELL, DataSmellType.SEPARATING_SMELL, DataSmellType.SPACING_SMELL, DataSmellType.SPECIAL_CHARACTER_SMELL, DataSmellType.SYNONYM_SMELL, DataSmellType.TAGGING_SMELL]
    encoding_understandability_smells = [DataSmellType.DATE_AS_DATE_TIME_SMELL, DataSmellType.DATE_AS_STRING_SMELL, DataSmellType.DATE_TIME_AS_STRING_SMELL, DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL, DataSmellType.INTEGER_AS_FLOATING_POINT_NUMBER_SMELL, DataSmellType.INTEGER_AS_STRING_SMELL, DataSmellType.TIME_AS_STRING_SMELL, DataSmellType.SUSPECT_CHARACTER_ENCODING_SMELL]
    consistency_smells = [DataSmellType.ABBREVIATION_INCONSISTENCY_SMELL, DataSmellType.CASING_INCONSISTENCY_SMELL, DataSmellType.CLASS_INCONSISTENCY_SMELL, DataSmellType.DATE_TIME_FORMAT_INCONSISTENCY_SMELL, DataSmellType.MISSING_VALUE_INCONSISTENCY_SMELL, DataSmellType.SEPARATING_INCONSISTENCY_SMELL, DataSmellType.SPACING_INCONSISTENCY_SMELL, DataSmellType.SPECIAL_CHARACTER_INCONSISTENCY_SMELL, DataSmellType.SYNTAX_INCONSISTENCY_SMELL, DataSmellType.UNIT_INCONSISTENCY_SMELL, DataSmellType.TRANSPOSITION_INCONSISTENCY_SMELL]
    all_smells = {'Believability Smells': believability_smells, 'Syntactic Understandability Smells': syntactic_understandability_smells, 'Encoding Understandability Smells': encoding_understandability_smells, 'Consistency Smells': consistency_smells}
    
    if request.user.is_authenticated:
        current_user_id = request.user.id
    else:
        current_user_id = dummy_user.id
    file1 = File.objects.filter(user_id=current_user_id).latest("uploaded_time")
    smells = SmellType.objects.all().filter(belonging_file=file1)#.get().smell_type
    
    new = []
    for l in list(smells):
        new.append(l.smell_type)
    print(new)

    available_smells = {i: [a for a in j if a.value in new] for i,j in all_smells.items()}

    context = {}
    context['smells'] = available_smells
    if request.method == 'POST':
      some_var = request.POST.getlist('smells')  
      context['list'] = some_var
    return render(request, 'customize.html', context)

def result(request):
    context = {}
    if request.user.is_authenticated:
        current_user_id = request.user.id
    else:
        current_user_id = dummy_user.id

    file1 = File.objects.filter(user_id=current_user_id).latest("uploaded_time")

    #print(column_names)


    #dataset = manager.get_dataset("Titanic.csv")
    #available_files = manager.get_available_dataset_identifiers()

    dataset = manager.get_dataset(file1.path_to_file)
    column_names = precheck_columns(dataset.get_column_names())
    detector = DetectorBuilder(context=con, dataset=dataset).build()
    detected_smells = detector.detect()
    sorted_results = sort_results(detected_smells, column_names)
    
    for key, value in sorted_results.items():
        column1 = Column.objects.create(column_name=key, belonging_file=file1)
        for v in value:
            DetectedSmell.objects.create(data_smell_type=v.data_smell_type.value, total_element_count=v.statistics.total_element_count, faulty_element_count=v.statistics.faulty_element_count, belonging_file=file1, belonging_column=column1)
    #column_names = [c.column_name for c in list(Column.objects.all().filter(belonging_file=file1))]
    
    #column_names = precheck_columns(dataset.get_column_names())
    context['column_names'] = column_names
    #detector = DetectorBuilder(context=con, dataset=dataset).build()
    #supported_smells = detector.get_supported_data_smell_types()
    #print(supported_smells)
    #detected_smells = detector.detect()
    #sorted_results = sort_results(detected_smells, column_names)
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
    if "Unnamed: 0" in columns:
        columns.remove("Unnamed: 0")
    return sorted(columns)

