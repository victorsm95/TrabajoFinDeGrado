# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

Python module in charge of managing the forms to present to 
the user and validate the data entered by it through them. 
'''
from django.forms import ModelForm, ValidationError
from django.contrib.auth.models import User
from models import Profile
import os

# Formulario para poder cambiar el nombre y apellidos del usuario
class UserForm(ModelForm):
	""" Form to change the first name and last name of the user. """
	class Meta:
		model = User
		fields = ['first_name', 'last_name']

# Formulario para poder cambiar la biografia e imagen del usuraio
class ProfileForm(ModelForm):
	""" Form to change the bio name and image of the user profile. """
	class Meta:
		model = Profile
		fields = ['bio', 'image']
