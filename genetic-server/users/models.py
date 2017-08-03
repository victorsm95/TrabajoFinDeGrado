# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

MODEL

Python module to define the data models that describe the data 
handled by the application. Model Entity / Relationship that
will later be translated by Django into a relational database.
'''
from __future__ import unicode_literals
import os

from django.db import models
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress

# Clase que describe un perfil que es asociado a un usuario a traves de una relacion uno a uno
class Profile(models.Model):
	"""
	Python class describing a profile user.
	Parameters
	----------

	user: object models.OneToOneField: 
	   Field that generates the one-to-one relationship with 
 	   the corresponding user
       
   	bio: object model.TextField:
	   Text field to store information about the user's 
	   biography.

	image: object model.ImageField:
	   Field to save the user profile image.
	"""
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	bio = models.TextField(max_length=500, blank = True)
	image = models.ImageField(upload_to = 'profilePhotos', blank = True) 
	
	class Meta:
		"""
		Python metaclass that describes concepts related to 
		the database.
		"""
		db_table = 'user_profile'

	# Comprobamos si el correo del usuario se ha verificado
	def account_verified(self):
		"""
		Python function that checks if the user's email is verified.
		""" 
		if self.user.is_authenticated:
			result = EmailAddress.objects.filter(email=self.user.email)
			if len(result):
				return result[0].verified
		return False
		
# Al crear un usuario se le asocio un perfil
"""Function that associates a profile with a user 
at the time of creation."""
User.profile = property(lambda u: Profile.objects.get_or_create(user = u)[0])
