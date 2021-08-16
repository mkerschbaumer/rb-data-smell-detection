# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from app.models import File, Column, DetectedSmell, SmellType, Parameter
from app import forms
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse 
from datetime import datetime
from .forms import ParameterForm
import os
import sys
from core.settings import SMELL_FOLDER, BASE_DIR, CORE_DIR, LIBRARY_DIR
cwd = os.getcwd()
sys.path.append(LIBRARY_DIR+"/data_smell_detection/")

from datasmelldetection.core.datasmells import DataSmellType

smells_columns = {"smells":[
                    "DataSmellType.EXTREME_VALUE_SMELL",
                    "DataSmellType.SUSPECT_SIGN_SMELL",
                    "DataSmellType.MISSING_VALUE_SMELL",
                    "DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL",
                    "DataSmellType.INTEGER_AS_STRING_SMELL"
                ], "columns":[
                    "Age",
                    "Name",
                    "PClass",
                    "Sex",
                    "SexCode",
                    "Survived"
                ]}
smells = {"smells":[
            "DataSmellType.EXTREME_VALUE_SMELL",
            "DataSmellType.SUSPECT_SIGN_SMELL",
            "DataSmellType.MISSING_VALUE_SMELL",
            "DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL",
            "DataSmellType.INTEGER_AS_STRING_SMELL"
        ], "columns":[
        ]}
columns = {"smells":[], 
           "columns":[
            "Age",
            "Name",
            "PClass",
            "Sex",
            "SexCode",
            "Survived"
          ]}
empty = {"smells":[], 
         "columns":[]
        }

class ViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Testuser', password='test', first_name='Test', last_name='Test')
        self.client.login(username='Testuser', password='test')
        self.file1 = File(file_name='Titanic.csv', user=self.user, uploaded_time=datetime.now())
        self.file1.save()

        self.column1 = Column(column_name='Age', belonging_file=self.file1)
        self.column1.save()
        self.column2 = Column(column_name='Name', belonging_file=self.file1)
        self.column2.save()

        self.smell_type1 = SmellType.objects.create(smell_type='Missing Value Smell')
        self.smell_type1.save()
        self.smell_type1.belonging_file.add(self.file1)

        self.smell_type2 = SmellType.objects.create(smell_type='Duplicated Value Smell')
        self.smell_type2.save()
        self.smell_type2.belonging_file.add(self.file1)

        self.parameter1 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter1.save()

        self.parameter2 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type2, belonging_file=self.file1)
        self.parameter2.save()

    def test_upload_csv_file(self):
        response = self.client.get(reverse('upload'))
        
        with open(SMELL_FOLDER+'test.csv') as csv_file:
            request = self.client.post(reverse('upload'), {'upload': csv_file})

        self.assertEquals(request.context.get('message'), None)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTemplateUsed(request, 'index.html')

    def test_upload_png_file(self):
        response = self.client.get(reverse('upload'))
        
        with open(SMELL_FOLDER+'test.png') as csv_file:
            request = self.client.post(reverse('upload'), {'upload': csv_file})

        self.assertEquals(request.context['message'], 'Upload a .csv file.')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertTemplateUsed(request, 'index.html')

    def test_customize(self):
        response = self.client.get(reverse('customize'))
        self.assertEquals(response.context['forms']['Believability Smells'][DataSmellType('Duplicated Value Smell')]['checkbox'], 'smell_checked')
        self.assertEquals(response.context['forms']['Believability Smells'][DataSmellType('Duplicated Value Smell')]['mostly'][0], self.parameter2)

        self.assertEquals(response.context['forms']['Encoding Understandability Smells'][DataSmellType('Missing Value Smell')]['checkbox'], 'smell_checked')
        self.assertEquals(response.context['forms']['Encoding Understandability Smells'][DataSmellType('Missing Value Smell')]['mostly'][0], self.parameter1)
        self.assertEquals(response.context['forms']['Syntactic Understandability Smells'], {})
        self.assertEquals(response.context['forms']['Consistency Smells'], {})

        request1 = self.client.post(reverse('customize'), smells_columns)
        self.assertEquals(request1.context.get("message"), None)

        request2 = self.client.post(reverse('customize'), smells)
        self.assertEquals(request2.context.get("message"), 'Select smells AND columns.')

        request3 = self.client.post(reverse('customize'), empty)
        self.assertEquals(request3.context.get("message"), 'Select smells AND columns.')

        request4 = self.client.post(reverse('customize'), columns)
        self.assertEquals(request4.context.get("message"), 'Select smells AND columns.')

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'customize.html')

    def test_result(self):
        response = self.client.get(reverse('result'))
        self.assertEquals(response.context['column_names'], [self.column1.column_name, self.column2.column_name])
        self.assertEquals(response.context['file'], self.file1.file_name)

        request1 = self.client.post(reverse('result'), {'del': [self.file1.file_name]})
        self.assertEquals(request1.context['delete_message'], 'Result deleted and not viewable in Saved Results.')
        self.assertTemplateUsed(response, 'results.html')

    def test_saved_results(self):
        self.detected_smell = DetectedSmell.objects.create(data_smell_type=self.smell_type1, total_element_count=200, faulty_element_count=10, faulty_list=["hi", "jo", "ho"], belonging_column=self.column1)
        response = self.client.get(reverse('saved'))
        self.assertEquals(response.context['results'], {'Titanic.csv': {self.column1: [self.detected_smell], self.column2: []}})
        request1 = self.client.post(reverse('saved'), {'del': [self.file1.file_name]})
        self.assertEquals(request1.context['results'], {})

class ParameterFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Testuser', password='test', first_name='Test', last_name='Test')
        self.client.login(username='Testuser', password='test')
        self.file1 = File(file_name='Test.csv', user=self.user, uploaded_time=datetime.now())
        self.file1.save()
        self.smell_type = SmellType.objects.create(smell_type='Missing Value Smell')
        self.smell_type.save()
        self.smell_type.belonging_file.add(self.file1)

    def test_parameter_form_inside_interval(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=1.0, value=0.5, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertTrue(form.is_valid())

    def test_parameter_form_outside_interval(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=1.0, value=3.0, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertFalse(form.is_valid())

    def test_parameter_form_inside_interval_max_inf(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=-1.0, value=3.0, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertTrue(form.is_valid())

    def test_parameter_form_outside_interval_max_inf(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=-1.0, value=-3.0, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertFalse(form.is_valid())


    

