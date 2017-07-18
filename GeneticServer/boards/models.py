# -*- coding: utf-8 -*-
'''
Definicion
---
MODELO
Modulo python para definir los modelos de datos que describen los datos manejados por la aplicacion. Modelo
Entidad/Relación que despues sera traducido por Django a una base de datos relacional.
'''
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list

# Clase que describe un board y los ficheros asociados al mismo
class Board(models.Model):

	COMA = 'COMA'
	TABULACION = 'TABULACION'
 	PUNTOYCOMA = 'PUNTO Y COMA'
	ESPACIO = 'ESPACIO'
	OTRO = 'OTRO'
	
	TYPE_OF_DELIMITER = ((COMA, 'Coma (,)'),(TABULACION, 'Tabulated'), (PUNTOYCOMA, 'Point and coma (;)'), (ESPACIO, 'Space'), (OTRO, 'Other'))

	id_board = models.CharField(max_length = 200, primary_key = True)
	owner = models.ForeignKey(User, on_delete = models.CASCADE)
	title = models.CharField(max_length = 30)
	date = models.DateField(auto_now_add = True)
	
	dataFile = models.FileField(upload_to = 'boardCSV')
	dataFilteredMN = models.FileField(upload_to = 'boardCSV', null = True)
	dataFilteredGBR = models.FileField(upload_to = 'boardCSV', null = True)
	dataFilteredBoruta = models.FileField(upload_to = 'boardCSV', null = True)

	delimiter = models.CharField(max_length = 20,choices = TYPE_OF_DELIMITER, default = COMA)

	n_genes_initial = models.IntegerField(default = 8)
	n_samples = models.PositiveIntegerField(default = 0)
	n_genes = models.PositiveIntegerField(default = 0)
	n_types = models.PositiveIntegerField(default = 0)

	types = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1000, null = True)

	confirmed = models.BooleanField(default = False)

	class Meta:
		unique_together = (("owner", "title"),)
		db_table = 'board'

# Clase que describe un board compartido, haciendo referencia a un board existente y a un usuario al cual se comparte.
class BoardShared(models.Model):
	id_board = models.CharField(max_length = 200, primary_key = True)
	board = models.ForeignKey(Board, on_delete = models.CASCADE)
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	confirmation = models.BooleanField(default = False)
	
	class Meta:
		unique_together = (("board", "user"),)
		db_table = 'board_share'