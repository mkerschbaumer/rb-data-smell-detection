# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class File(models.Model):
    path_to_file = models.CharField(max_length=255, primary_key=True)

class Column(models.Model):
    column_name = models.CharField(max_length=100)
    belonging_file = models.ForeignKey(File, on_delete=models.CASCADE)

class DetectedSmell(models.Model):
    data_smell_type = models.CharField(max_length=100)
    total_element_count = models.IntegerField()
    faulty_element_count = models.IntegerField()
    mostly = models.FloatField()
    path_to_file = models.ForeignKey(File, on_delete=models.CASCADE)
    belonging_file = models.ForeignKey(Column, on_delete=models.CASCADE)