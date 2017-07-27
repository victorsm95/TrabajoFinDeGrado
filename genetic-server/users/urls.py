# -*- coding: utf-8 -*-
'''
Definicion
---
CONTROLADOR
Modulo python que define las urls particulares de la aplicacion y que despues seran importadas
en el modulo url del proyecto para manejar los diferentes recursos publicados en la plataforma
'''
from django.conf.urls import url

from users import views 

urlpatterns = [
	url(r'^$', views.home),
	url(r'^profile$', views.profile),
	url(r'^profile/imageDelete$', views.image_delete),
	url(r'^shared$', views.home_shared),
	url(r'^info$', views.info),
	url(r'^contact$', views.contact)
]

