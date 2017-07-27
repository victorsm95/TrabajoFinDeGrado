# -*- coding: utf-8 -*-
'''
Definicion
---
Modulo python encargado de administrar los modelos definidos para acceder a ellos y poder
gestionarlos desde el sitio de administracion de django
'''
from django.contrib import admin
from models import Board, BoardShared

# Registro de los modelos Board y BoardShared en el sitio de administración, para poder gestionarlos
admin.site.register(Board)
admin.site.register(BoardShared)