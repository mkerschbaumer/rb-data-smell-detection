# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class File(models.Model):
    file_name = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_time = models.DateTimeField(auto_now_add=True)

class SmellType(models.Model):
    smell_type = models.CharField(max_length=255, primary_key=True)
    belonging_file = models.ManyToManyField(File)

class Column(models.Model):
    column_name = models.CharField(max_length=100)
    belonging_file = models.ForeignKey(File, on_delete=models.CASCADE)

class DetectedSmell(models.Model):
    data_smell_type = models.ForeignKey(SmellType, on_delete=models.CASCADE)    
    total_element_count = models.IntegerField()
    faulty_element_count = models.IntegerField()
    faulty_list = models.CharField(max_length=1024)
    belonging_column = models.ForeignKey(Column, on_delete=models.CASCADE)

class Parameter(models.Model):
    name = models.CharField(max_length=255)
    value = models.FloatField()
    data_type = models.CharField(max_length=255)
    belonging_smell = models.ForeignKey(SmellType, on_delete=models.CASCADE)
    belonging_file = models.ForeignKey(File, on_delete=models.CASCADE)

