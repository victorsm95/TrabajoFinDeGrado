# -*- coding: utf-8 -*-
'''
Definicion
---
Modulo python encargado de gestionar los formularios para presentar al usuario y validar los
datos introducidos por el mismo a través de ellos 
'''
from django.forms import ModelForm, ValidationError
from django.contrib.auth.models import User
from models import Profile
import os

# Formulario para poder cambiar el nombre y apellidos del usuario
class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name']

# Formulario para poder cambiar la biografia e imagen del usuraio
class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ['bio', 'image']