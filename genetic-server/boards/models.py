# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

MODEL

Python module to define the data models that describe the data 
handled by the application. Model Entity / Relationship that
will later be translated by Django into a relational database.
'''
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list

# Clase que describe un board y los ficheros asociados al mismo
class Board(models.Model):
	"""
	Python class describing a board and the files associated with it.

	Parameters
	----------

	id_board: object models.CharField: Board identifier
	owner: object django.contrib.auth.models.User: User owner of board
	title: object model.CharField: Title of board
	date: object model.DateField: Add date of board
	dataFile: object model.FileFIeld: Dataset assocciated of board
	dataFilteredMN: object model.FileFIeld: File filtered Mann-Whitney of board
	dataFilteredGBR: object model.FileFIeld: File filtered GBR of board
	dataFilteredBoruta: object model.FileFIeld: File filtered Boruta of board
	delimiter: object model.CharField: Delimiter of dataFile
	n_genes_initial: object models.IntegerField: Number of genes filtered 
	n_samples: object models.IntegerField: Number of shamples 
	n_genes: object models.IntegerField: NUmber of genes total
	n_types: object models.IntegerField: Number of shample types
	types: object models.CharField: Shamples types
	confirmed: object models.BooleanField: Filtered state board
	"""

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

	delimiter = models.CharField(max_length = 20, choices = TYPE_OF_DELIMITER, default = COMA)

	n_genes_initial = models.IntegerField(default = 8)
	n_samples = models.PositiveIntegerField(default = 0)
	n_genes = models.PositiveIntegerField(default = 0)
	n_types = models.PositiveIntegerField(default = 0)

	types = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1000, null = True)

	confirmed = models.BooleanField(default = False)

	class Meta:
		"""
		Python metaclass that describes concepts related to the database.
		"""
		unique_together = (("owner", "title"),)
		db_table = 'board'

# Clase que describe un board compartido, haciendo referencia a un 
# board existente y a un usuario al cual se comparte.
class BoardShared(models.Model):
	"""
	Python class that describes a shared board, referring to an existing 
	board and a user to whom it is shared.

	Parameters
	----------
	id_board: object models.CharField: Board shared identifier
	board: object boards.model.Board: Board shared linked
	user: object django.contrib.auth.models.User: Board participant user
	confirmation: object models.BooleanField: Shared confirmation state of board
	"""
	id_board = models.CharField(max_length = 200, primary_key = True)
	board = models.ForeignKey(Board, on_delete = models.CASCADE)
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	confirmation = models.BooleanField(default = False)
	
	class Meta:
		"""
		Python metaclass that describes concepts related to the database.
		"""
		unique_together = (("board", "user"),)
		db_table = 'board_share'
