# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

CONTROLLER

Python module that defines the particular urls of the application 
and that will then be imported In the url module of the project to 
handle the different resources published in the platform.
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

