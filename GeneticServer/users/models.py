# -*- coding: utf-8 -*-
'''
Definicion
---
MODELO
Modulo python para definir los modelos de datos que describen los datos manejados por la aplicacion. Modelo
Entidad/Relación que despues sera traducido por Django a una base de datos relacional.
'''
from __future__ import unicode_literals
import os

from django.db import models
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

# Clase que describe un perfil que es asociado a un usuario a traves de una relacion uno a uno
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	bio = models.TextField(max_length=500, blank = True)
	image = models.ImageField(upload_to = 'profilePhotos', blank = True) 
	
	class Meta:
		db_table = 'user_profile'

	# Comprobamos si el correo del usuario se ha verificado
	def account_verified(self): 
		if self.user.is_authenticated:
			result = EmailAddress.objects.filter(email=self.user.email)
			if len(result):
				return result[0].verified
		return False
		
# Al crear un usuario se le asocio un perfil
User.profile = property(lambda u: Profile.objects.get_or_create(user = u)[0])