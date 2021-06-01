# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from app.models import File, Column, DetectedSmell, SmellType, Parameter
from app import forms
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse 

class TestViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')
        File.objects.create(file_name='TestCSV.csv', user=self.user)
        File.objects.create(file_name='TestCSV2.csv', user=self.user)
        self.client = Client()

    def test_upload_POST(self):
        response = self.client.get(reverse('upload'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    

