# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

Python module in charge of managing the defined 
models to access them and power manage them from the django 
admin site.
'''
from django.contrib import admin
from models import Profile

# Registro del modelos Profile
admin.site.register(Profile)
