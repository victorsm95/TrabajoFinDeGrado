# -*- coding: utf-8 -*-
'''
Definicion
---
CONTROLADOR
Modulo python que define las urls particulares de la aplicacion y que despues seran importadas
en el modulo url del proyecto para manejar los diferentes recursos publicados en la plataforma
'''
from django.conf.urls import url

from boards import views 

urlpatterns = [
	url(r'^addBoard$', views.add_board),
	url(r'^deleteBoard$', views.delete_board),
	url(r'^deleteBoardShared$', views.delete_board_shared),
	url(r'^analysis$', views.analysis),
	url(r'^analysisSearch$', views.filt),
	url(r'^analysisAdd$', views.addGen),
	url(r'^analysisRequestAdd$', views.requestAddGen),
	url(r'^analysisDelete$', views.delGen),	
	url(r'^analysisShare$', views.share),
	url(r'^confirmShare$', views.confirm),
	url(r'^analysisSave$', views.saveState),
	url(r'^infoBoard$', views.infoBoard),
	url(r'^searchUser$', views.searchUser),
	url(r'^proccesShared$', views.proccesShared),
	url(r'^renderEmail$', views.resend),
	url(r'^refilterBoard$', views.refilterBoard)
	]