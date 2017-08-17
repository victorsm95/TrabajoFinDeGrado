# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

VIEW

Python module that defines the view functions that manage 
the application and serve the templates necessary for the use 
of the functionalities offered by it.
'''

# Renderizar vistas
from django.shortcuts import render, HttpResponseRedirect
from django.template import Context
# Recibir señales
from django.dispatch import receiver
from signals import board_signal_shared, board_signal_save
# Modelos de datos a manejar
from models import Board, BoardShared
from django.contrib.auth.models import User
# Formularios a presentar y manejar
from forms import DeleteBoardForm, AddBoardForm, SearchGenForm, AddGenForm, DeleteGenForm, SharedBoardForm, ShareBoardForm, SharedBoardConfirmForm, SaveStateForm, SearchUserForm, ProccesSharedForm, RefilterForm
# Envio de emails
from django.core.mail import send_mail
# Tratamiento de ficheros
from django.core.files import File
# Configuracion del proyecto
from biogen import settings
from biogen.settings import IP_ADDRESS
# Filtrados estadisticos y manejo de datos genéticos (matrices)
import numpy as np
from filters.dataSetMongo import saveDataSet, deleteDataSet
# Base de datos no sql (MongoDB)
from pymongo import MongoClient
import pymongo
# Decoradores de Django-alluth para verificar ciertas caracteristicas de usuarios y sesiones
# En este caso, verificar que el usuario esta logueado para realizar ciertas funciones
from allauth.account.decorators import login_required 
# Decoradores de Django para el manejo de metodos http
from django.views.decorators.http import require_http_methods
# Hilos para realizar los filtrados en un hilo secundario
import threading
# Tratamiento de los datos de ficheros csv
import csv
# Tiempo: hora y fecha actual del servidor en milisegundos
import time
# Modulo del sistema
import os
# Excepcion Http404 para capturar errores
from django.http import Http404
# Funcion para obtener los milisegundos de la hora actual del servidor para que el navegador lea los cambios
# del fichero de filtrado cada vez que la pagina de anlasis genetico carga
current_milli_time = lambda: int(round(time.time() * 1000))

#### FUNCIONES VISTA ####

# AÑADIR UN NUEVO BOARD 
@login_required
@require_http_methods(['POST', 'GET'])
def add_board(request):
	"""
	Function view in charge of adding a new board to the platform.

	Http Methods:
	   * GET
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Tratamiento para el metodo POST (Añadir un board con los datos del formulario)
	if request.method == 'POST':
		addBoardForm = AddBoardForm(request.POST, request.FILES)
		context = Context(
			{
				'addBoardForm': addBoardForm
			})
		# Si los datos on válidos
		if addBoardForm.is_valid():
			# Generacion del id del board a partir del nombre del username y del nombre del board
			idBoard = request.user.username + addBoardForm.cleaned_data["title"].capitalize().replace(' ','_')
			# Comprobacion de que no existan mas boards con ese id, y si es asi se indica al usuario
			error = Board.objects.filter(id_board = idBoard)
			if len(error):
				warning = """
				It was not possible to add the board, since you already have one with the same name. 
				Delete existing board or choose another name"""
				context = Context(
					{
						'addBoardForm': addBoardForm, 
						'warning': warning
					})
				return render(request, 'addBoards.html', context)
			# Generacion del objeto board a guardar en la base de datos
			board = Board(id_board = idBoard, owner = request.user, title = addBoardForm.cleaned_data["title"].capitalize(), dataFile = addBoardForm.cleaned_data["dataFile"], 
					delimiter = addBoardForm.cleaned_data["delimiter"], n_genes_initial = addBoardForm.cleaned_data["n_genes_initial"])
			# Cambio de nombre el fichero csv que representa el board
			board.dataFile.name = '' + idBoard
			# Lectura del dataset y cargado del mismo en una matriz numpy para su uso
			if board.delimiter == 'COMA':
				separator = ','
			elif board.delimiter == 'TABULACION':
				separator = '	'
			elif board.delimiter == 'PUNTO Y COMA':
				separator = ';'
			elif board.delimiter == 'ESPACIO':
				separator = ' '
			elif board.delimiter == 'OTRO':
				dialect = csv.Sniffer().sniff(board.dataFile.read(10000))
				separator = dialect.delimiter

			data = np.loadtxt(board.dataFile, delimiter=separator, dtype=np.str)
			# Obtencion de todos los tipos de las muestras (histologia del dataset)
			board.types = ",".join(data[1,1:])
			# Obtencion del numero de muestras y el numero de genes del dataset
			board.n_samples = data[1,1:].shape[0]
			board.n_genes = data[2:,1:].shape[0]
			# Obtencion del numero de tipos de clases de muestras diferentes
			num_types = []
			for item in data[1,1:].tolist():
				if num_types.count(item) == 0:
					num_types.append(item)

			board.n_types = len(num_types)
			# Guardado del board en la base de datos sin confirmar
			board.save()

			# Guardado del dataset del board en la base de datos mongo y realizacion de los filtrados en un hilo a parte
			tr = threading.Timer(0,function=saveDataSet, args=(board,data))
			tr.start()
			# Redireccion al sitio home del usuario, mientras el servidor trabaja en los filtrados
			return HttpResponseRedirect('/')

	# Si el metodo es GET se presenta el formulario al usuario para que introduzca los datos
	else:
		addBoardForm = AddBoardForm()
		context = Context(
			{
				'addBoardForm': addBoardForm
			})
	
	return render(request, 'addBoards.html', context)

# ELIMINAR UN BOARD
@login_required
@require_http_methods(['POST'])
def delete_board(request):
	"""
	Function view in charge of deleting a new board to the platform.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	deleteBoard = DeleteBoardForm(request.POST)
	if deleteBoard.is_valid():
		# Obtencion del board a eliminar de la base de datos
		idBoard = deleteBoard.cleaned_data["id_board_delete"]
		board_delete = Board.objects.get(id_board = idBoard)
		board_delete.dataFile.delete()
		board_delete.dataFilteredMN.delete()
		board_delete.dataFilteredGBR.delete()
		board_delete.dataFilteredBoruta.delete()
		board_delete.delete()
		# Eliminacion del dataset del board de la base de datos mongo
		deleteDataSet(idBoard)

	return HttpResponseRedirect('/')

# ELIMINAR UN BOARD COMPARTIDO 
@login_required
@require_http_methods(['POST'])
def delete_board_shared(request):
	"""
	Function view in charge of deleting a board shared to the platform.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	deleteBoard = DeleteBoardForm(request.POST)
	if deleteBoard.is_valid():
		# Obtencion del board a eliminar de la base de datos
		idBoard = deleteBoard.cleaned_data["id_board_delete"]
		board_delete = BoardShared.objects.get(id_board = idBoard)
		board_delete.delete()
	return HttpResponseRedirect('/')

# ACCESO AL BOARD Y SU VISUALIZACION PARA EL ANÁLISIS GENÉTICO
@login_required
@require_http_methods(['GET'])
def analysis(request):
	"""
	Function view in charge of presenting the information contained in a board of visual form to allow the genetic analysis.

	Http Methods:
	   * GET

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formularios a presentar
	searchForm = SearchGenForm()
	addGenForm = AddGenForm()
	deleteGenForm = DeleteGenForm()
	shareForm = ShareBoardForm()
	# Obtención del board solicitado para presentar sus datos al usuario y del filtrado solicitado
	idBoard = request.GET['id_board_analysis']
	board_analysis = Board.objects.get(id_board = idBoard)
	n_genes_initial = board_analysis.n_genes_initial
	filt = request.GET["filt"]
	# Participantes del board
	board_shared = BoardShared.objects.filter(board = board_analysis)
	participants = []
	for board in board_shared:
		participants.append(board.user.username)
	# Seguridad
	if ((request.user != board_analysis.owner) and (participants.count(request.user) == 0)):
		raise Http404
	# Obtencion de la informacion a visualizar de la base de datos mongo	
	client = MongoClient()
	db = client.geneticserverdb
	cursor = db["" + idBoard].find({'name' : "DatasetState" + filt})
	for document in cursor:
		brushed = document['value']	
						
	cursor = db["" + idBoard].find({'name' : "Specifications" + filt})
	for document in cursor:
		gene_names_filtered = document['gene_names_filtered']
		n_genes = document['n_genes_selected']
		y = document['histology']

	# Visualizacion gráfica del grafo de importancia
	cursor = db["" + idBoard].find({'name' : "SpecificationsMN"})
	for document in cursor:
		variance = document['graphic']

	cursor = db["" + idBoard].find({'name' : "SpecificationsGBR"})
	for document in cursor:
		rawweights = document['graphic'] 

	cursor = db["" + idBoard].find({'name' : "SpecificationsBoruta"})
	for document in cursor:
		ranking = document['graphic'] 

	# Hora y fecha del servidor en milisegundos
	instant = current_milli_time()
	# Generacion del contexto para la pagina y sretono de la misma
	context = Context(
		{	
			'board_analysis':board_analysis, 
			'deleteForm':deleteGenForm,
			'shareForm':shareForm, 
			'namesDel':gene_names_filtered, 
			'participants':participants, 
			'n_genes': n_genes, 
			'max_domain': max(y),
			'min_domain': min(y), 
			'brushed': brushed,
			'filt': filt,
			'variance': variance,
			'rawweights': rawweights, 
			'ranking': ranking,
			'n_genes_initial': n_genes_initial,
			'instant': instant
		}
	)
	return render(request, 'genExpression.html',context)

# FUNCION ENCARGADA DE HACER UN NUEVO FILTRADO CON EL NUMERO DE GENES INDICADO
@login_required
@require_http_methods(['POST', 'GET'])
def refilterBoard(request):
	"""
	Function view responsible for performing a new filtering with the number of genes indicated.

	Http Methods:
	   * GET
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Si el metodo es POST se procesan los datos del formulario
	if request.method == 'POST':
		# Formulario a procesar
		refilterForm = RefilterForm(request.POST)
		# Si el formulario es valido se realiza el refiltrado
		if refilterForm.is_valid():
			idBoard = refilterForm.cleaned_data['id_board_refilter']
			n_genes_refilter = refilterForm.cleaned_data['n_genes_refilter']
			board_refilter = Board.objects.get(id_board = idBoard)

			# Lectura del dataset y cargado del mismo en una matriz numpy para su uso
			if board_refilter.delimiter == 'COMA':
				separator = ','
			elif board_refilter.delimiter == 'TABULACION':
				separator = '	'
			elif board_refilter.delimiter == 'PUNTO Y COMA':
				separator = ';'
			elif board_refilter.delimiter == 'ESPACIO':
				separator = ' '
			elif board_refilter.delimiter == 'OTRO':
				dialect = csv.Sniffer().sniff(board_refilter.dataFile.read(10000))
				separator = dialect.delimiter

			data = np.loadtxt(board_refilter.dataFile, delimiter=separator, dtype=np.str)

			board_refilter.n_genes_initial = n_genes_refilter
			board_refilter.confirmed = False

			# Guardado del board en la base de datos sin confirmar
			board_refilter.save()

			# Guardado del dataset del board en la base de datos mongo y realizacion de los filtrados en un hilo a parte
			tr = threading.Timer(0,function=saveDataSet, args=(board_refilter,data))
			tr.start()
			# Redireccion al sitio home del usuario, mientras el servidor trabaja en los filtrados
			return HttpResponseRedirect('/')

		# Si el formulario no es válido, se muestran los errores al usuario
		else:
			idBoard = refilterForm.cleaned_data["id_board_refilter"]
			board_refilter = Board.objects.get(id_board = idBoard)
			if (request.user != board_refilter.owner):
				raise Http404
			context = Context({'refilterForm':refilterForm})
			return render(request, 'refilter.html', context)
	# Si el metodo es GET se presenta el formulario al usuario
	elif request.method == 'GET':
		# Formulario a resentar
		refilterForm = RefilterForm()
		idBoard = request.GET["id_board_refilter"]
		board_refilter = Board.objects.get(id_board = idBoard)
		# Seguridad
		if (request.user != board_refilter.owner):
			raise Http404
		context = Context({'refilterForm':refilterForm, 'board_refilter':board_refilter})
		return render(request, 'refilter.html', context)



# ACCESO A LA PAGINA DE ADICCION DE GENES Y FILTRADO POR NOMBRE DE LOS MISMOS
@login_required
@require_http_methods(['GET'])
def requestAddGen(request):
	"""
	Function view responsible for giving access to the page of adding genes and
	filtered by name of the same.

	Http Methods:
	   * GET

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formularios a presentar 
	searchForm = SearchGenForm()
	addGenForm = AddGenForm()
	idBoard = request.GET["id_board_requestAdd"]
	board_analysis = Board.objects.get(id_board = idBoard)
	# Seguridad
	if (request.user != board_analysis.owner):
				raise Http404
	filt = request.GET["filt"]
	context = Context(
		{
			'id_board': idBoard,
			'searchForm':searchForm,
			'addForm':addGenForm,
			'filt': filt	
		}
	)
	return render(request, 'addGen.html', context)

# FILTRADO DE LOS GENES POR SU NOMBRE PREVIAMENTE A AÑADIR
@login_required
@require_http_methods(['POST'])
def filt(request):
	"""
	Function view charged to filter the genes by their name before the gene is added.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formulario a procesar
	searchForm = SearchGenForm(request.POST)
	# Formulario a presentar
	addGenForm = AddGenForm()
	# Si el formulario es valido se muestran los nombres filtrados
	if searchForm.is_valid():
		# Obtencion del board al que añadir un gen
		idBoard = searchForm.cleaned_data["id_board_searchGen"]
		filt = searchForm.cleaned_data["filt"]
		nameGen = searchForm.cleaned_data["name_gen"]
		# Obtencion de los datos para la visualizacion de la base de datos MONGO
		client = MongoClient()
		db = client.geneticserverdb
		cursor = db["" + idBoard].find({'name' : "Specifications" + filt})
		for document in cursor:
			gene_names_filtered = document['gene_names_filtered']
			gene_names = document['gene_names']
		lista = gene_names[:]
		# Eliminacion de los genes ya añadidos en la visualizacion
		for name in gene_names_filtered:
			gene_names.remove(name)
			lista.remove(name)
		# Filtrado de los nombre de genes a mostrar 
		for name in lista:
			if not (name.startswith(nameGen)):
				gene_names.remove(name)
		# Generacion del contexto para la pagina
		context = Context(
			{
				'id_board': idBoard, 
				'gene_names':gene_names,
				'searchForm':searchForm,
				'addForm':addGenForm,
				'filt': filt	
			}
		)

	else:
		# Si se ha introducido un filtro incorrecto se muestran los errores al usuario
		idBoard = searchForm.cleaned_data["id_board_searchGen"]
		especificaciones = searchForm.cleaned_data["filt"]
		context = Context(
			{
				'id_board': idBoard,
				'searchForm':searchForm,
				'addForm':addGenForm,
				'filt':Specifications		
			}
		)
			
	return render(request, 'addGen.html', context)

# ADICCION DE LOS GENES ESPECIFICADOS
@login_required
@require_http_methods(['POST'])
def addGen(request):
	"""
	Function responsible for adding the specified gene to the board's filtering.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formulario a procesar
	addGenForm = AddGenForm(request.POST)
	# Formularios a presentar en la vista
	searchForm = SearchGenForm()
	deleteGenForm = DeleteGenForm()
	shareForm = ShareBoardForm()
	# Si los datos del formulario son correctos adicción del gen a la visualizacion del filtrado 
	if addGenForm.is_valid():
		# Obtencion del board al que añadir el gen introducido
		idBoard = addGenForm.cleaned_data["id_board_addGen"]
		nameGen = addGenForm.cleaned_data["name_gen"]
		filt = addGenForm.cleaned_data["filt"]
		board_add = Board.objects.get(id_board = idBoard)
		# Participantes del board
		board_shared = BoardShared.objects.filter(board = board_add)
		participants = []
		for board in board_shared:
			participants.append(board.user.username)
		# Obtencion de los datos para la visualizacion de la base de datos MONGO
		client = MongoClient()
		db = client.geneticserverdb
		cursor = db["" + idBoard].find({'name' : "Specifications" + filt})
		for document in cursor:
			n_genes = document['n_genes_selected']
			gene_names_filtered = document['gene_names_filtered']
			histology = document['histology']
			n_columnasFiltered = len(document['histology'])
			samples = document['samples']
		y = np.asarray(histology)
		gene_names_filtered.append(nameGen)
		# Escritura en fichero csv
		expression = []
		n_genes = n_genes + 1	
		for name in gene_names_filtered:
			cursor = db["" + idBoard].find({'gene_name' : name})
			for document in cursor:
				expression = expression + document['expression']
							
		Xfiltered = np.asarray(expression).reshape(n_genes, n_columnasFiltered)

		pathFiltered = "media/boardCSV/" + idBoard + "Filtered" + filt + ".csv"
		fileFiltered = open(pathFiltered, 'w')
		fileFiltered.write('Histology,' + ','.join(gene_names_filtered) + '\n')

		for i in range(len(samples)):
			fileFiltered.write(y[i].astype(np.str) + ',' + ','.join(Xfiltered[:,i].astype(np.str)).replace('"','') + '\n')
		# Actualizacion de la base de datos mongo
		db["" + idBoard].update_one(
    		{"name": "Specifications" + filt},
   		 	{
        		"$set": {
           			"n_genes_selected": n_genes,
				 	"gene_names_filtered": gene_names_filtered
        		}
    		}
    	)
		db["" + idBoard].update_one(
    		{"name": "DatasetState" + filt},
   		 	{
        		"$set": {
           			 "value":"false"
        		}
    		}
    	)

		return HttpResponseRedirect('/boards/analysis?filt=' + filt + '&id_board_analysis=' + idBoard)
	
	# Si los datos son inválidos se muestran los errores al usuario
	else:
		idBoard = addGenForm.cleaned_data["id_board_addGen"]
		filt = addGenForm.cleaned_data["filt"]
		context = Context(
			{
				'id_board': idBoard,
				'searchForm':searchForm,
				'addForm':addGenForm,
				'filt': filt		
			}
		)
		return render(request, 'addGen.html', context)

# ELIMINACION DEL GEN SELECCIONADO
@login_required
@require_http_methods(['POST'])
def delGen(request):
	"""
	Function responsible for deleting the selected gene to the board's filtering.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formulario a procesar
	deleteGenForm = DeleteGenForm(request.POST)
	# Formularios a presentar en la vista
	shareForm = ShareBoardForm()
	# Si el gen es valido se elimina de la visualizacion del filtrado
	if deleteGenForm.is_valid():
		# Obtencion del board al que eliminar el gen introducido
		idBoard = deleteGenForm.cleaned_data["id_board_deleteGen"]
		nameGen = deleteGenForm.cleaned_data["name_gen"]
		filt = deleteGenForm.cleaned_data["filt"]
		board_delete = Board.objects.get(id_board = idBoard)
		# Participantes del board
		board_shared = BoardShared.objects.filter(board = board_delete)
		participants = []
		for board in board_shared:
			participants.append(board.user.username)
		# Obtencion de los datos para la visualizacion, de la base de datos MONGO
		client = MongoClient()
		db = client.geneticserverdb
		cursor = db["" + idBoard].find({'name' : "Specifications" + filt})
		for document in cursor:
			n_genes = document['n_genes_selected']
			gene_names_filtered = document['gene_names_filtered']
			histology = document['histology']
			n_columnasFiltered = len(document['histology'])
			samples = document['samples']
		y = np.asarray(histology)
		gene_names_filtered.remove(nameGen)
		# Escritura en fichero csv
		expression = []
		n_genes = n_genes - 1
		print(gene_names_filtered)	
		for name in gene_names_filtered:
			cursor = db["" + idBoard].find({'gene_name' : name})
			for document in cursor:
				expression = expression + document['expression']
		Xfiltered = np.asarray(expression).reshape(n_genes, n_columnasFiltered)

		pathFiltered = "media/boardCSV/" + idBoard + "Filtered" + filt + ".csv"
		fileFiltered = open(pathFiltered, 'w')
		fileFiltered.write('Histology,' + ','.join(gene_names_filtered) + '\n')
			
		for i in range(len(samples)):
			fileFiltered.write(y[i].astype(np.str) + ',' + ','.join(Xfiltered[:,i].astype(np.str)).replace('"','') + '\n')
				
		# Actualizacion de la base de datos Mongo
		result = db["" + idBoard].update_one(
    			{"name": "Specifications" + filt},
   		 		{
        			"$set": {
           				 "n_genes_selected": n_genes,
					 	 "gene_names_filtered": gene_names_filtered
        			}
    			}
    		)

		result = db["" + idBoard].update_one(
    			{"name": "DatasetState" + filt},
   		 		{
        			"$set": {
           				 "value":"false"
        			}
    			}
    		)
	
	return HttpResponseRedirect('/boards/analysis?filt=' + filt + '&id_board_analysis=' + idBoard)

# COMPARTICION DEL BOARD
@login_required
@require_http_methods(['POST'])
def share(request):
	"""
	Function responsible for sharing the specified board.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Fromularios a procesar
	shareForm = ShareBoardForm(request.POST)
	sharedForm = SharedBoardForm(request.POST)
	# Formularios a presentar
	sharedConfirmForm = SharedBoardConfirmForm()
	searchUser = SearchUserForm()
	# Si el formulario de solicitud de comparticion es valido se presenta el formulario de busqueda de usuario
	# al que compartir dicho board
	if shareForm.is_valid():
		idBoard = shareForm.cleaned_data["id_board_share"]
		board_share = Board.objects.get(id_board = idBoard)
		context = Context({'board_share': board_share, 'searchForm': searchUser})
		return render(request, 'shareBoard.html', context)
	# Si el formulario de peticion de comparticion a un determinado usuario ya introducido es válido se presenta al usuario
	# el formulario de confirmacion
	elif sharedForm.is_valid():
		idBoard = sharedForm.cleaned_data["id_board_shared"]
		user = sharedForm.cleaned_data["user"]
		board_shared = Board.objects.get(id_board = idBoard)
		context = Context({'username': user, 'board_shared': board_shared, 'form':sharedConfirmForm})
		return render(request, 'shareConfirm.html', context)
	# Si se ha introducido un usuario vacio o invalido se presentan los errores al usuario 
	else:
		idBoard = sharedForm.cleaned_data["id_board_shared"]
		board_share = Board.objects.get(id_board = idBoard)
		context = Context({'board_share': board_share, 'searchForm': searchUser, 'sharedForm': sharedForm})
		return render(request, 'shareBoard.html', context)

# FILTRAMOS LOS NOMBRES DE USUARIO PARA COMPARTIR EL BOARD
@login_required
@require_http_methods(['POST'])
def searchUser(request):
	"""
	Function in charge of filtering users by the name entered before sharing the board.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formulario a procesar
	searchUser = SearchUserForm(request.POST)
	# Si el filtro introducido es correcto se muestra al usuario los nombres filtrados
	if searchUser.is_valid():
		# Obtencion del board y el nombre filtrado
		idBoard = searchUser.cleaned_data["id_board_searchUser"]
		username = searchUser.cleaned_data["username"]
		board_share = Board.objects.get(id_board = idBoard)
		# Obtencion de los usuarios que cumplen el filtrado
		listUsers = User.objects.all()
		listUsernames = []
		for user in listUsers:
			if user.username != 'admin' and user.username != request.user.username:
				listUsernames.append(user.username)

		for name in listUsernames:
			if not (name.startswith(username)):
				listUsernames.remove(name)

		context = Context({'users': listUsernames, 'board_share': board_share, 'searchForm': searchUser})
		return render(request, 'shareBoard.html', context)
	else:
		idBoard = searchUser.cleaned_data["id_board_searchUser"]
		board_share = Board.objects.get(id_board = idBoard)
		context = Context({'board_share': board_share, 'searchForm': searchUser})

# CONFIRMACION DE LA COMPARTICION DEL BOARD
@login_required
@require_http_methods(['POST'])
def confirm(request):
	"""
	Function view responsible for confirming board sharing.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formulario a procesar
	confirmForm = SharedBoardConfirmForm(request.POST)
	# Se confirma la solicitud de comparticion del board con el usuario especificado
	if confirmForm.is_valid():
		# Obtencion del board y del usuario
		idBoard = confirmForm.cleaned_data["id_board_confirmShare"]
		board_confirm = Board.objects.get(id_board = idBoard)

		username = confirmForm.cleaned_data["user"]
		user_confirm = User.objects.get(username = username)
		# Guardado en la base de datos de un nuevo objeto Board Shared con estado de cofirmacion 'False' hasta que el usuario
		# lo acepto desde su email
		board_shared = BoardShared(id_board = idBoard + username, board = board_confirm, user = user_confirm)
		board_shared.save()
		# A traves de una señal se envia un email al usuario, para que este lo acepte o no
		board_signal_shared.send(sender=BoardShared, board=board_shared)
		

	return HttpResponseRedirect('/')

# REENVIO DEL EMAIL AL USUARIO PARA QUE ACEPTE O NO UN BOARD COMPARTIDO SIN CONFIRMAR
@login_required
@require_http_methods(['GET'])
def resend(request):
	"""
	Function responsible for sending the email to the user for acceptance or not
	of an unconfirmed board.

	Http Methods:
	   * GET

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Obtencion del board que aceptar o no
	board = BoardShared.objects.get(id_board = request.GET['id_board'])
	# Seguridad
	if (request.user != board.user):
			raise Http404
	# A traves de una señal se envia un email al usuario, para que este lo acepte o no
	board_signal_shared.send(sender = BoardShared, board=board)
	return HttpResponseRedirect('/profile')

# GUARDADO DEL ESTADO DE LAS COORDENADAS PARALELAS EN MONGO
@login_required
@require_http_methods(['POST'])
def saveState(request):
	"""
	Function responsible for saving of the status of the display of the
 	coordinates for the mongo database.

	Http Methods:
	   * POST

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Formulario a procesar
	saveForm = SaveStateForm(request.POST)
	# Si el formulario es valido se guarda en la base de datos Mongo el estado de las coordenadas paralealas
	if saveForm.is_valid():
		idBoard = saveForm.cleaned_data["id_board_save"]
		brushed = saveForm.cleaned_data["brushed"]
		filt = saveForm.cleaned_data["filt"]
		# Actualizacion de la base de datos
		client = MongoClient()
		db = client.geneticserverdb
		coll = db["" + idBoard]
		result = coll.update_one(
    		{"name": "DatasetState" + filt},
   		 	{
        		"$set": {
           			 "value": brushed
        		}
			}
		)
	return HttpResponseRedirect('/')
			
# MOSTRAMOS LAS ESPECIFICACIONES DEL FORMATO DE LOS DATASET
@login_required
@require_http_methods(['GET'])
def infoBoard(request):
	"""
	Function that is responsible for displaying the format specifications of 
	the datatsets supported by the platform.

	Http Methods:
	   * GET

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	return render(request, 'formato.html')

# TRATAMIENTO DE LA PETICION DE COMPARTICION DEL BOARD
@login_required
@require_http_methods(['POST','GET'])
def proccesShared(request):
	"""
	Function responsible for processing the request to share the board, presenting 
	the user and processing their decision as it is convenient.

	Http Methods:
	   * POS
	   * GET

	Parameters
	----------
	
	request: django.http.request
	    Object request that contains all the information 
	    regarding the HTTP request to be handled in the view function: 
	    method, sessions, parameters, etc.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects

	Return
	------
	response: django.http.response
	    Object through which the response to the http request is 
	    handled by the view function, as well as all the necessary 
	    and own information of the answer of the communication.
	    Django reference:
	    https://docs.djangoproject.com/en/1.11/ref/request-response/#httpresponse-objects
	"""
	# Si el metodo es POST se confirma o elimina el board compartido
	if request.method == 'POST':
		# Fromulario a procesar
		proccessForm = ProccesSharedForm(request.POST)
		# Si el formulario es valido se guarda o no el board
		if proccessForm.is_valid():
			# Obtenccon del board y la opcion elegida
			idBoard = proccessForm.cleaned_data["id_board_proccess"]
			option = proccessForm.cleaned_data["option"]
			boards = BoardShared.objects.filter(id_board = idBoard)
			# Comprobacion previa de si el board no ha sido borrado inesperadamente
			if len(boards) > 0:
				board_confirmShared = BoardShared.objects.get(id_board = idBoard)
				if option == 'accept':
					# Si se acepta se cambia el estado a confirmado
					board_confirmShared.confirmation = True
					board_confirmShared.save()
				elif option == 'refuse':
					# Si se rechaza el board compartido se elimina de la tabla de boards compartidos 
					board_confirmShared.delete()
				return HttpResponseRedirect('/shared')
			else:
				return HttpResponseRedirect('/')
	# Si el metodo es GET se presenta al usuario el formulario para aceptar o no el board
	else:
		# Obtencion del board
		idBoard = request.GET['board']
		boards = BoardShared.objects.filter(id_board = idBoard)
		# Comprobacion previa de si el board no ha sido borrado 
		if len(boards) > 0:
			board_confirmShared = BoardShared.objects.get(id_board = idBoard)
			confirmation = board_confirmShared.confirmation
			# Comprobacion de si es el usuario correcto o no
			if request.user == board_confirmShared.user:
				# Si es correcto se muestra el formulario
				context = Context({'id_board':idBoard, 'confirmation':confirmation})
				return render(request, 'proccesShared.html', context)
			else:
				# Si no se le especifica que de debe loguearse con el usuario correcto
				return render(request, 'errorProccesShared.html') 
		# Si ha sido borrado se indica al usuario
		else:
			context = Context({'borrado':True})
			return render(request,'proccesShared.html', context)

# ESTE METODO A LA ESCUCHA DE LA SEÑAL ENVIADA AL COMPARTIR UN BOARD SE ENCARGA DE NOTIFICAR AL USUARIO POR E-MAIL
@receiver(board_signal_shared)
def notificationBoardShared(sender, **kwargs):
	"""
	This function, listening to the signal sent to accompany a board, is responsible 
	for notifying the user by email.

	Signal reciever
	---------------
	biogen.boards.signals.board_signal_shared

	Parameters
	----------
	
	sender: object 
	    Object sender of the signal
	
	**Kwargs: dict
	    Dictionary with the arguments of the defined signal.  
	"""
	mensaje = "The user '" + kwargs['board'].board.owner.username + "' wants to share the board '" + kwargs['board'].board.title + "' with you.\n" + "Please access the link to confirm the request: http://" + IP_ADDRESS + "/boards/proccesShared?board=" + kwargs['board'].id_board
	send_mail('Share Board', mensaje, settings.EMAIL_HOST_USER, [kwargs['board'].user.email], fail_silently=False)
	
# ESTE METODO A LA ESCUCHA DE LA SEÑAL ENVIADA AL ACABAR LOS FILTRADOS DE UN BOARD, CAMBIA EL ESTADO DEL MISMO A TRUE
@receiver(board_signal_save)
def notificationAddBoard(sender, **kwargs):
	"""
	This function, listening to the signal sent at the end of the filtering of a board, 
	changes the resolution of the same to confirmed to be able to proceed to its
 	visualization.

	Signal reciever
	---------------
	biogen.boards.signals.board_signal_save

	Parameters
	----------
	
	sender: object 
	    Object sender of the signal
	
	**Kwargs: dict
	    Dictionary with the arguments of the defined signal.  
	"""
	board = Board.objects.filter(id_board = kwargs['board'].id_board, confirmed=False)
	if len (board) > 0:
		for board_confirmed in board:
			board_confirmed.confirmed = True
		
			board_confirmed.dataFilteredMN = "boardCSV/" + kwargs['board'].id_board + "FilteredMN" + ".csv"
			board_confirmed.dataFilteredGBR = "boardCSV/" + kwargs['board'].id_board + "FilteredGBR" + ".csv"
			board_confirmed.dataFilteredBoruta = "boardCSV/" + kwargs['board'].id_board + "FilteredBoruta" + ".csv"

			board_confirmed.save()
