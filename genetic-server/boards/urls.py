# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

CONTROLLER

Python module that defines the particular urls of the application 
and that will then be imported In the url module of the project to 
handle the different resources published in the platform.
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
	url(r'^refilterBoard$', views.refilterBoard)
	]
