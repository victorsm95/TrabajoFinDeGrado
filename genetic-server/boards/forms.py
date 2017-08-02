# -*- coding: utf-8 -*-
"""
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

Python module responsible for managing the forms to present to the user and validate the data entered by the user through them.
"""
from django.forms import ModelForm, Form, ValidationError
from models import Board, BoardShared
from django import forms
import re

from pymongo import MongoClient
import pymongo

# Formulario para borrar un board
class DeleteBoardForm(Form):
	""" Form to delete a board."""
	id_board_delete = forms.CharField()

# Formulario para añadir un board
class AddBoardForm(ModelForm):
	""" Form to add a board."""
	class Meta:
		model = Board
		fields = ['title', 'dataFile', 'delimiter', 'n_genes_initial']
	# El titulo debe tener al menos tres caracteres
	def clean_title(self):
		title = self.cleaned_data['title']
		if len(title) < 3:
			raise ValidationError("Name must be three characters shorter")	
		return title

	def clean_n_genes_initial(self):
		n_genes = self.cleaned_data['n_genes_initial']
		if n_genes < 1 or n_genes > 15:
			raise ValidationError("The number of genes must be between 1 and 15")
		return n_genes

# Formulario para buscar un gen antes de añadirlo 
class SearchGenForm(Form):
	""" Form to serch a gene before add on the board."""
	id_board_searchGen = forms.CharField()
	name_gen = forms.CharField()
	filt = forms.CharField()

# Formulario para añadir un gen
class AddGenForm(Form):
	""" Form to add a gene on the board."""
	id_board_addGen = forms.CharField()
	filt = forms.CharField()
	name_gen = forms.CharField()
	
	# No puede haber mas de 15 genes en la visualización  
	def clean_name_gen(self):
		idBoard = self.cleaned_data['id_board_addGen']
		name = self.cleaned_data['name_gen']
		filt = self.cleaned_data['filt']
		
		client = MongoClient()
		db = client.geneticserverdb
		cursor = db["" + idBoard].find({'name' : "Specifications" + filt})
		for document in cursor:
			n_genes = document['n_genes_selected']

		if n_genes >= 15:
			raise ValidationError("ERROR: There can be no more than 15 genes selected")

		return name

# Formulario para eliminar un gen	
class DeleteGenForm(Form):
	""" Form to remove a gene from the board."""
	id_board_deleteGen = forms.CharField()
	filt = forms.CharField()
	name_gen = forms.CharField()

	# No puede haber menos de un gen en la visualización
	def clean_name_gen(self):
		idBoard = self.cleaned_data['id_board_deleteGen']
		name = self.cleaned_data['name_gen']
		filt = self.cleaned_data['filt']
		
		client = MongoClient()
		db = client.geneticserverdb
		cursor = db["" + idBoard].find({'name' : "Specifications" + filt})
		for document in cursor:
			n_genes = document['n_genes_selected']

		if n_genes == 1:
			raise ValidationError("ERROR: There can be no less than one selected gene")

		return name

# Formulario para la solicitud de compartición de board
class ShareBoardForm(Form):
	"""Board request application form"""
	id_board_share = forms.CharField()

# Formulario para la solicitud de comparticion de board con el usuario especificado
class SharedBoardForm(Form):
	"""Board request application form with the specified user"""
	id_board_shared = forms.CharField()
	user = forms.CharField()

	def clean_user(self):
		username = self.cleaned_data['user']
		idBoard = self.cleaned_data['id_board_shared']
		# Comporbacion para verificar si ya esta compartido el board con el usuario introducido o si se ha enviado solicitud
		# y no ha sido aceptada por el usuario
		if len(BoardShared.objects.filter(id_board = idBoard + username)) > 0:
			board = BoardShared.objects.get(id_board = idBoard + username)
			if board.confirmation:
				raise ValidationError("ERROR: You already shared the board with " + username)
			else:
				raise ValidationError("ERROR: You have already sent an application to share this board with " + username)

		return username

# Fromulario para confirmacion de la comparticion del board
class SharedBoardConfirmForm(Form):
	"""Form for confirmation of board sharing"""
	id_board_confirmShare = forms.CharField()
	user = forms.CharField()

# Formulario para el procesamiento de la solicitud de la comparticion
class ProccesSharedForm(Form):
	"""Sharing Request Processing Form"""
	id_board_proccess = forms.CharField()
	option = forms.CharField()

# Formulario para la busqueda de usuario a la hora de compartir un board
class SearchUserForm(Form):
	"""Form for user search when sharing a board"""
	id_board_searchUser = forms.CharField()
	username = forms.CharField()

# Fromulario para guardar el estado de las muestras seleccionadas en el filtrado de un board
class SaveStateForm(Form):
	"""Form to save the status of selected samples in the filtering of a board"""
	id_board_save = forms.CharField()
	brushed = forms.CharField()	
	filt = forms.CharField()

# Formulario para el refiltrado, para poder hacer tantos filtros como se desee
class RefilterForm(Form):
	"""Form for filtering, to be able to make as many filters as you want"""
	id_board_refilter = forms.CharField()
	n_genes_refilter= forms.IntegerField()

	def clean_n_genes_refilter(self):
		n_genes = self.cleaned_data['n_genes_refilter']
		if n_genes < 1 or n_genes > 15:
			raise ValidationError("The number of genes must be between 1 and 15")
		return n_genes
