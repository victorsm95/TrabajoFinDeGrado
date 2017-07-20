# -*- coding: utf-8 -*-
'''
Definicion
---
VISTA
Modulo python que define las funciones vistas que gestionan la aplicacion y sirven las plantillas 
necesarias para el uso de las funcionalidades ofrecidas por la misma.
'''
# Renderizar vistas
from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.template import Context
# Enviar e-mal
from django.core.mail import send_mail
# Tratamiento de ficheros
import os
# Configuracion del proyecto
from GeneticServer import settings
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
# Decoradores de Django para el manejo de metodos http
from django.views.decorators.http import require_http_methods
# Señales de django allauth
from allauth.account.signals import password_changed
# Recibir señales
from django.dispatch import receiver

# DEVUELVE LA PAGINA DE INICIO DE CADA USUARIO CON SUS BOARDS O BIEN EL INDEX DE LA APLICACION
@require_http_methods(['GET'])
def home(request):
	# Si el usuario esta autenticado se devuelve la pagina home con los boards del usuario
	if request.user.is_authenticated() and request.user.profile.account_verified():
		board = Board.objects.filter(owner=request.user, confirmed = True)
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
	return render(request, 'home/readMore.html')

# CONTACTO PARA LOS USUARIOS
@require_http_methods(['GET'])
def contact(request):
	return render(request, 'home/contact.html')

# RETORNA LA PAGINA CON LOS BOARDS QUE HAN COMPARTIDO CON EL USUARIO
@login_required
@require_http_methods(['GET'])
def home_shared(request):
	# Obtencion de los boards compartidos con el usuario
		boardShared = BoardShared.objects.filter(user=request.user, confirmation=True)
		context = Context({'board': boardShared})
		return render(request, 'home/home_shared.html', context)

# PAGINA CON LOS DATOS DEL USUARIO  Y UN BREVE RESUMEN ESTADISTICO DE SUS RECURSOS
@login_required
@require_http_methods(['GET','POST'])
def profile(request):
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
			request.user.username = userForm.cleaned_data["username"]
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
		userForm = UserForm(initial={'first_name': request.user.first_name, 'last_name': request.user.last_name, 'username':request.user.username})
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
	if request.user.profile.image:
		profiles = Profile.objects.filter(user = request.user)
		if len(profiles):
			profiles = Profile.objects.get(user = request.user)
			profiles.image.delete()
	return HttpResponseRedirect('/profile')

# ESTA FUNCION A LA ESCUCHA DE LA SEÑAL password_changed ENVIA UN CORREO AL USUARIO INFORMANDOLE DE QUE SU CONTRASEÑA HA SIDO CAMBIADA
@receiver(password_changed)
def notificationChangePassword(sender, **kwargs):
	# Se envia un email infromativo al usuario
	mensaje = "The password has been successfully changed to account" + kwargs['request'].user.username
	send_mail('Password changed', mensaje, settings.EMAIL_HOST_USER, [kwargs['request'].user.email], fail_silently=False)
