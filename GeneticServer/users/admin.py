# -*- coding: utf-8 -*-
'''
Definicion
---
Modulo python encargado de administrar los modelos definidos para acceder a ellos y poder
gestionarlos desde el sitio de administracion de django
'''
from django.contrib import admin
from models import Profile

# Registro del modelos Profile
admin.site.register(Profile)
