# -*- coding: utf-8 -*-
'''
Definicion
---
Modulo python encargado de dos tareas fundamentales:
    1. Realizar un prefiltrado de los genes que pasesn un valor de varianza por encima del punto medio de la misma
    2. Realizar un filtrado independiente para presentar al usuario, utilizando el punto de corte adecuado para el 
       numero de gene introducido.
'''

from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin

from scipy.stats import mannwhitneyu

import operator

import numpy as np

# Funcion para la obtencion del p-valor de cada uno de los genes
def mw(X, Y):
    pvalues = []    
    for i in range(X.shape[0]):
        try:
            pvalues.append(mannwhitneyu(X[i],Y[i])[1])
        except:
            pvalues.append(1.)
    return np.asarray(pvalues)

# Prefiltrado que servirá además como entrada al resto de filtrados (GBR y Boruta)
class Prefilter(BaseEstimator, TransformerMixin):

    selectedGenesIndexes = None
    selectedGenesIndexesPrefilter = None
    X_filt = None
    varianza = None
    
    
    def __init__(self, n_components=-1):
        
        self.n_components = n_components

    # Filtrado de los genes 
    def fit(self, X, y=None):
        # Obtencion del p-valor de cada uno de los genes
        pvalues = mw(X[y==0].T, X[y==1].T)
       
        # Indices de los genes cuyo p-valor sea menor que 0.05
        indexes = np.asarray(range(X.shape[1]))[pvalues < 0.05]

        # Matriz con la expresion genetica de los genes con p-valor < 0.05
        X1 = X[:, pvalues < 0.05]

        # Si no se especificado un numero de genes se retornan los que hayan superado este primer paso 
        if self.n_components == -1:
            self.selectedGenesIndexes = indexes
            return self

        # En otro caso, se utilizará la varianza de los genes para seguir con la seleccion
        var = np.var(X1, axis=0)
        adapthr = np.sort(var)

        # Punto de corte por encima del cual estan los n_genes con mayor varianza
        punto_de_corte = adapthr[-self.n_components-1]
        # Punto medio de los valores de la varianza, para usar Mann-Whitney como prefiltrado
        punto_medio = ((adapthr[0] + adapthr[adapthr.shape[0] - 1]) / 2) + adapthr[0]
        
        # Matriz de prefiltrado utilizada como entrada en los siguientes filtrados y los indices de sus genes
        self.X_filt = X1[:, var>punto_medio]
        self.selectedGenesIndexesPrefilter = indexes[var>punto_medio]
        # Indices de los n_gnes con mayor varianza para usar Mann-Whitney como filtrado independiente
        self.selectedGenesIndexes = indexes[var>punto_de_corte]
        self.varianza = np.var(X, axis = 0)
      
        return self
    
    def transform(self, X, y=None):
        X = np.asarray(X)
        return X[:, self.selectedGenesIndexes]

    def fit_transform(self, X, y=None):
        self.fit(X,y)
        return self.transform(X,y)