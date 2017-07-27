# -*- coding: utf-8 -*-
'''
Definicion
---
Modulo python encargado de hacer los tres filtrados al subir el board, 
guardando los datos en un base de de datos mongo no sql, con un documento 
para cada gen, y uno para cada filtrado.
'''
from pymongo import MongoClient

import numpy as np

from models import Board

# Filtrados 
from mannWhitney import Prefilter
from gbr import GBRT_CBR
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier

import operator

from django.core.files import File
import os
import csv

# Señales
from signals import board_signal_save

# GUARDAR EL DATASET EN LA BASE DE DATOS MONGO (NO SQL)
def saveDataSet(board, data):

	samples = data[0,1:]
	X = data[2:,1:].astype(np.float32)
	y = data[1,1:].astype(np.int)

	gene_names = data[2:,0]
	gene_names_unicos = []
	expresion = []
	Xcorregido = np.empty((len(list(set(gene_names))),len(y.tolist())))

	#Almacenamiento en la base de datos de los genes sin replicar, nos quedamos con el primer gen encontrado en el dataset, 
	#media comentada (mucho menos eficiente)
	client = MongoClient()
	db = client.geneticserverdb
	coll = db["" + board.id_board]
	coll.delete_many({})

	j = 0
	i = 0
	for name in gene_names.tolist():
		if gene_names_unicos.count(name) == 0:
			gene_names_unicos.append(name)
			Xcorregido[j,:] = X[i,:]
			#Xcorregido[j,:] = np.mean(X[gene_names == name,:], axis=0) ---> Media aritmetica (Muy inefciente)
			coll.insert_one(
 				{
					'gene_name': name,
					'expression': Xcorregido[j,:].tolist(),
       			}
			)
			j = j + 1
		i = i + 1

		
	#####  FILTRADO MANN-WHITNEY  #####
	pref = Prefilter(n_components=board.n_genes_initial)
	Xfiltered = pref.fit_transform(Xcorregido.T, y).T
	gene_names_filtered = np.asarray(gene_names_unicos)[pref.selectedGenesIndexes]

	# Escritura del fichero con los datos geneticos procesados para su posterior visualizacion a traves de javascript
	fileFiltered = open("media/boardCSV/" + board.id_board + "FilteredMN" + ".csv", 'w')
	fileFiltered.write('Histology,' + ','.join(gene_names_filtered) + '\n')

	for i in range(len(samples.tolist())):
		fileFiltered.write(y[i].astype(np.str) + ',' + ','.join(Xfiltered[:,i].astype(np.str)) + '\n')
		
	# Vector con las varianzas ordenadas de mayor a menor
	variance = pref.varianza[pref.selectedGenesIndexesPrefilter]
	variance = np.sort(variance)[::-1]

	# Almacenamiento en la base de datos mongo de los resultados del filtrado Mann-Whitney
	coll.insert_one(
  		{
			'name': "SpecificationsMN",
			'samples': samples.tolist(),
			'histology': y.tolist(),
			'n_genes_selected': board.n_genes_initial,
			'gene_names': gene_names_unicos,
			'gene_names_filtered': gene_names_filtered.tolist(),
			'graphic': variance.tolist(),
			'filter': 'Wilcoxon-Mann-Whitney'
        })

	#####  FILTRADO GBRT_CBR #####
	filtGBR_CBR = GBRT_CBR()
	filtGBR_CBR.fit(X =pref.X_filt,y = y)

	# Diccionario con clave (indice del gen) y valor (rawweight del gen)
	index_rawweights = {}
	for i in range(len(filtGBR_CBR.rawweights.tolist())):
		index_rawweights[pref.selectedGenesIndexesPrefilter[i]] = filtGBR_CBR.rawweights[i]

	# Ordenacion d los indices segun el rawweight
	result = sorted(index_rawweights.items(), key=operator.itemgetter(1))

	# Index con los indices de los num_genes con mayor rawweight
	indexes = []
	for i in range(board.n_genes_initial):
		indexes.append((result[len(result) - 1 - i])[0])

	XfilteredGBR = Xcorregido[indexes, :]
	gene_names_filtered = np.asarray(gene_names_unicos)[indexes]

	# Escritura del fichero con los datos geneticos procesados para su posterior visualizacion a traves de javascript
	fileFiltered = open("media/boardCSV/" + board.id_board + "FilteredGBR" + ".csv", 'w')
	fileFiltered.write('Histology,' + ','.join(gene_names_filtered) + '\n')

	for i in range(len(samples.tolist())):
		fileFiltered.write(y[i].astype(np.str) + ',' + ','.join(XfilteredGBR[:,i].astype(np.str)) + '\n')

	# Vector con los rawweights ordenado de mayor a menor
	rawweights = np.sort(filtGBR_CBR.rawweights)[::-1]

	# Almacenamiento en la base de datos mongo de los resultados del filtrado
	coll.insert_one(
  		{
			'name': "SpecificationsGBR",
			'samples': samples.tolist(),
			'histology': y.tolist(),
			'n_genes_selected': board.n_genes_initial,
			'gene_names': gene_names_unicos,
			'gene_names_filtered': gene_names_filtered.tolist(),
			'graphic': rawweights.tolist(),
			'filter': 'CBR-GBR'
        }
	)

	##### FILTRADO BORUTA #####
	## Estimador de aprendizaje supervisado Random Forest Clasifier
	rf = RandomForestClassifier(n_jobs=-1, class_weight='auto', max_depth=5)
	## Filtrado Boruta
	filtBoruta = BorutaPy(rf, n_estimators='auto', verbose=2, random_state=1, max_iter=40)
	filtBoruta.fit(pref.X_filt, y)
	
	# Obtencion de los indices de los n_genes mejor clasificados
	selectedGenesIndexesBoruta = []
	for i in range(len(pref.selectedGenesIndexesPrefilter.tolist())):
		if (filtBoruta.ranking_[i] == 1) and (len(selectedGenesIndexesBoruta) < board.n_genes_initial):
			selectedGenesIndexesBoruta.append(pref.selectedGenesIndexesPrefilter[i])
	if (len(selectedGenesIndexesBoruta) < board.n_genes_initial):
		for i in range(len(pref.selectedGenesIndexesPrefilter.tolist())):
			if (filtBoruta.ranking_[i] == 2) and (len(selectedGenesIndexesBoruta) < board.n_genes_initial):
				selectedGenesIndexesBoruta.append(pref.selectedGenesIndexesPrefilter[i])
	if (len(selectedGenesIndexesBoruta) < board.n_genes_initial):
		for i in range(len(pref.selectedGenesIndexesPrefilter.tolist())):
			if (filtBoruta.ranking_[i] > 2) and (len(selectedGenesIndexesBoruta) < board.n_genes_initial):
				selectedGenesIndexesBoruta.append(pref.selectedGenesIndexesPrefilter[i])

	XfilteredBoruta = Xcorregido[selectedGenesIndexesBoruta, :]
	gene_names_filtered = np.asarray(gene_names_unicos)[selectedGenesIndexesBoruta]

	# Escritura del fichero con los datos geneticos procesados para su posterior visualizacion a traves de javascript
	fileFiltered = open("media/boardCSV/" + board.id_board + "FilteredBoruta" + ".csv", 'w')
	fileFiltered.write('Histology,' + ','.join(gene_names_filtered) + '\n')

	for i in range(len(samples.tolist())):
		fileFiltered.write(y[i].astype(np.str) + ',' + ','.join(XfilteredBoruta[:,i].astype(np.str)) + '\n')

	# Vector con el ranking de genes ordenado
	ranking = np.sort(filtBoruta.ranking_)

	# Almacenamiento en la base de datos mongo
	coll.insert_one(
  		{
			'name': "SpecificationsBoruta",
			'samples': samples.tolist(),
			'histology': y.tolist(),
			'n_genes_selected': board.n_genes_initial,
			'gene_names': gene_names_unicos,
			'gene_names_filtered': gene_names_filtered.tolist(),
			'graphic': ranking.tolist(),
			'filter': 'Boruta'
       	}
	)

	# Documento para guardar el estado de las coordenadas paralelas en cuanto a muestras seleccionadas, en cada uno de
	# los filtrados disponibles

	coll.insert_one(
		{
			'name': 'DatasetStateMN',
			'value': 'false',
		}
	)

	coll.insert_one(
		{
			'name': 'DatasetStateGBR',
			'value': 'false',
		}
	)

	coll.insert_one(
		{
			'name': 'DatasetStateBoruta',
			'value': 'false',
		}
	)

	# Cuando los filtrados concluyan enviamos una señal para cambiar el estado del board a confirmado,
	# y asi el usuario pueda trabajar con el
	board_signal_save.send(sender = Board, board=board)
	


# ELIMINAR EL DATASET DE LA BASE DE DATOS MONGO
def deleteDataSet(idBoard):
	# Borramos todas las colecciones mongo asociadas al board a eliminar
	client = MongoClient()
	db = client.geneticserverdb
	result = db["" + idBoard].delete_many({})
