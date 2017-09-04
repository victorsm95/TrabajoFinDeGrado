# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

VIEW

Python module that defines the view functions that manage 
the application and serve the templates necessary for the use 
of the functionalities offered by it.
'''
# Renderizar vistas
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.template import Context
# Enviar e-mal
from django.core.mail import send_mail
# Tratamiento de ficheros
import os
# Configuracion del proyecto
from biogen import settings
# Formularios a presentar y manejar
from forms import UserForm, ProfileForm
# Modelos de datos a manejar
from models import Profile
from boards.models import Board, BoardShared
# Decoradores de Django-alluth para verificar ciertas caracteristicas de usuarios y sesiones
# En este caso, verificar que el usuario esta logueado para realizar ciertas funciones
from allauth.account.decorators import login_required
# Base de datos no sql (MongoDB)
from pymongo import MongoClient
import pymongo
from filters.dataSetMongo import deleteDataSet
# Decoradores de Django para el manejo de metodos http
from django.views.decorators.http import require_http_methods
# Señales de django allauth
from allauth.account.signals import password_changed
# Recibir señales
from django.dispatch import receiver


# DEVUELVE LA PAGINA DE INICIO DE CADA USUARIO CON SUS BOARDS O BIEN EL INDEX DE LA APLICACION
@require_http_methods(['GET'])
def home(request):
	"""
	Function view in charge of returning the home page of each user 
	with their boards or the application index.

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
	# Si el usuario esta autenticado se devuelve la pagina home con los boards del usuario
	if request.user.is_authenticated() and request.user.profile.account_verified():
		board = Board.objects.filter(owner=request.user, confirmed = True)
		board.order_by("date")
		# Si hay algun board procesandose se impide subir otro hmediante el estado igual a false
		if len(Board.objects.filter(owner=request.user, confirmed = False)) > 0:
			state = False
		else:
			state = True
		context = Context({'board': board, 'state':state})
		return render(request, 'home/home.html', context)
	# En caso contrario, se renderiza la pagina de inicio de la plataforma
	else:
		return render(request, 'home/index.html')

# INFORMACION Y ESPECIFICACIONES DE LA APLICACION
@require_http_methods(['GET'])
def info(request):
	"""
	Function view in charge of returning the page with 
	information and specifications of the web application.

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
	return render(request, 'home/readMore.html')

# CONTACTO PARA LOS USUARIOS
@require_http_methods(['GET'])
def contact(request):
	"""
	Function view in charge of returning the page with
	the contact admin platform for the users.

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
	return render(request, 'home/contact.html')

# RETORNA LA PAGINA CON LOS BOARDS QUE HAN COMPARTIDO CON EL USUARIO
@login_required
@require_http_methods(['GET'])
def home_shared(request):
	"""
	Function view in charge of returning the home page with
	the boards shared whit the request user.

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
	# Obtencion de los boards compartidos con el usuario
	boardShared = BoardShared.objects.filter(user=request.user, confirmation=True)
	boardShared.order_by("date")
	context = Context({'board': boardShared})
	return render(request, 'home/home_shared.html', context)

# PAGINA CON LOS DATOS DEL USUARIO Y UN BREVE RESUMEN ESTADISTICO DE SUS RECURSOS
@login_required
@require_http_methods(['GET','POST'])
def profile(request):
	"""
	Function responsible for returning a page with user profile data and 
	a brief statistical description of its use of the platform.
	The user can also change their profile data through this view.

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
	# Si el metodo es POST se procesa el formulario para cambiar los datos del perfil de usuario
	if request.method == 'POST':
		# Formularios a procesar
		userForm = UserForm(request.POST)
		profileForm = ProfileForm(request.POST, request.FILES)
		context = Context({'userForm': userForm, 'profileForm': profileForm})
		# Si los formularios son validos
		if userForm.is_valid() and profileForm.is_valid():
			# Se actualizan los datos del usuario de acuerdo a los datos de los formulario
			request.user.first_name = userForm.cleaned_data["first_name"]
			request.user.last_name = userForm.cleaned_data["last_name"]
			
			# Se actualizan los datos del perfil del usuario de acuerdo a los datos del formulario 
			# Tratamiento de la imagen
			imagen_modificada = profileForm.cleaned_data["image"]
			# Si se ha modificado se actualiza
			if imagen_modificada:
				profile = Profile(user=request.user, bio = profileForm.cleaned_data["bio"], image = profileForm.cleaned_data["image"])
				profile.image.name = request.user.username
				# Se borra la anterior imagen si la hubiera
				delete_image_path = settings.MEDIA_ROOT + '/profilePhotos/' + request.user.username
				if os.path.isfile(delete_image_path):
					os.remove(delete_image_path)
			# Si no se ha modificado
			else:
				# Si el usuario posee una imagne se presenta
				if request.user.profile.image: 
					profile = Profile(user=request.user, bio = profileForm.cleaned_data["bio"], image = request.user.profile.image)
				else:
					profile = Profile(user=request.user, bio = profileForm.cleaned_data["bio"])
			# Se guardan ambos objetos en la base de datos	
			
			profile.save()
			request.user.save()
			return HttpResponseRedirect('/')
		else:
			return render(request, 'home/profile.html', context)

			

	# Si el metodo es GET se presentan al usuario el formulario para cambiar sus datos y las estadisticas de sus recursos
	else:
		# Calculo del numero de boards propios
		ownBoards = Board.objects.filter(owner=request.user)
		# Calculo de los bards compartidos sin confirmar
		boardsSharedUnconfirm = []
		for board in ownBoards:
			boardSharedUnconfirmList = BoardShared.objects.filter(board=board, confirmation=False)
			for board in boardSharedUnconfirmList:
				boardsSharedUnconfirm.append(board)
		# Calculo de los boards compartidos confirmados
		boardsShared = []
		for board in ownBoards:
			boardsSharedList = BoardShared.objects.filter(board=board, confirmation=True)
			for board in boardsSharedList:
				boardsShared.append(board)
		# Calculo de los boards compartidos y confirmados al usuario
		boardsWithMe = BoardShared.objects.filter(user=request.user, confirmation=True)
		# Calculo de los boards compartidos al usuario, pero sin confirmar por el mismo
		unconfirmedBoards = BoardShared.objects.filter(user=request.user, confirmation=False)
		# Presentacion del formulario con los datos correspondientes
		userForm = UserForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name})
		# Aseguracion de la existencia del perfil asociado al usuario
		profile = Profile.objects.filter(user = request.user)
		if len(profile):
			profile = Profile.objects.get(user = request.user)
		else:
			profile = Profile(user = request.user)
			profile.save()

		profileForm = ProfileForm(initial={'bio': profile.bio, 'image': profile.image})

		context = Context({ 
				'userForm': userForm, 
				'profileForm': profileForm,
				'ownBoards': len(ownBoards),
				'boardsShared': len(boardsShared),
				'boardsWithMe': len(boardsWithMe),
				'boardsSharedUnconfirm': boardsSharedUnconfirm,
				'numBoardsSharedUnconfirm': len(boardsSharedUnconfirm),
				'unconfirmedBoards': unconfirmedBoards,
				'numUnconfirmedBoards': len(unconfirmedBoards),
				'numBoardsSharedUnconfirm': len(boardsSharedUnconfirm),
				'boardsSharedUnconfirm': boardsSharedUnconfirm})

		return render(request, 'home/profile.html', context)

# ELIMINACION DE LA IMAGEN DEL PERFIL DE USUARIO
@login_required
@require_http_methods(['GET'])
def image_delete(request):
	"""
	Function responsible for giving the user the possibility to delete 
	his profile photo.

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
	if request.user.profile.image:
		profiles = Profile.objects.filter(user = request.user)
		if len(profiles):
			profiles = Profile.objects.get(user = request.user)
			profiles.image.delete()
	return HttpResponseRedirect('/profile')

# ELIMINACION DE LA CUENTA DE USUARIO
@login_required
@require_http_methods(['GET'])
def user_delete(request):
	"""
	Function responsible for delete the user account.

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
	
	for board_delete in Board.objects.filter(owner = request.user):
		board_delete.dataFile.delete()
		board_delete.dataFilteredMN.delete()
		board_delete.dataFilteredGBR.delete()
		board_delete.dataFilteredBoruta.delete()
		deleteDataSet(board_delete.id_board)
		board_delete.delete()

	request.user.delete()
	return HttpResponseRedirect('/')

# ESTA FUNCION A LA ESCUCHA DE LA SEÑAL password_changed ENVIA UN CORREO AL USUARIO INFORMANDOLE DE QUE SU CONTRASEÑA HA SIDO CAMBIADA
@receiver(password_changed)
def notificationChangePassword(sender, **kwargs):
	"""
	By listening to the signal sent by changing the password of the user account, 
	this function sends an email to the user informing him that his password has been changed.

	Signal reciever
	---------------
	allauth.account.signals.password_changed

	Parameters
	----------
	
	sender: object 
	    Object sender of the signal
	
	**Kwargs: dict
	    Dictionary with the arguments of the defined signal.  
	"""
	# Se envia un email infromativo al usuario
	mensaje = "The password has been successfully changed to account" + kwargs['request'].user.username
	send_mail('Password changed', mensaje, settings.EMAIL_HOST_USER, [kwargs['request'].user.email], fail_silently=False)
