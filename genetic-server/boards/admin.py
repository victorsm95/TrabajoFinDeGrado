# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

Python module responsible for managing the defined 
models to access them and manage them from the django 
administration site.
'''
from django.contrib import admin
from models import Board, BoardShared

# Registro de los modelos Board y BoardShared en el sitio de administración, para poder gestionarlos
admin.site.register(Board)
admin.site.register(BoardShared)
