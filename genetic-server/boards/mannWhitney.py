# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

Python module in charge of two fundamental tasks:
    1. Carry out a pre-filter of the genes that pass a value of 
       variance above the midpoint of the same
    2. Perform an independent filtering to present to the user, 
       using the appropriate cut-off point for the gene number entered.
'''

from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin

from scipy.stats import mannwhitneyu

import operator

import numpy as np

# Funcion para la obtencion del p-valor de cada uno de los genes
def mw(X, Y):
    """
    Statistical Prefilter Mann Whitney calculates the p-value 
    of all genes to subsequently stay with those with a p-value less than 0.05.
    """
    pvalues = []    
    for i in range(X.shape[0]):
        try:
            pvalues.append(mannwhitneyu(X[i],Y[i])[1])
        except:
            pvalues.append(1.)
    return np.asarray(pvalues)

# Prefiltrado que servirá además como entrada al resto de filtrados (GBR y Boruta)
class Prefilter(BaseEstimator, TransformerMixin):
    """
    Improved Python implementation or the Mann-Whitney filter.

    Parameters
    ----------
    selectedGenesIndexes: list
        List containing the n best genes according 
        to the Mann-Whitney filter combined with variance.

    selectedGenesIndexesPrefilter: list
        List containing the genes with a variance above the 
        midpoint, calculated from the genes that surpass the Mann-Whitney 
        test.

    X_filt: Numpy matrix
        Matrix with the resulting filtering genes.

    varianza: Numpy matrix
        Matrix with the variance of the genes that surpass the 
        test of Mann Whitney.

    """
    selectedGenesIndexes = None
    selectedGenesIndexesPrefilter = None
    X_filt = None
    varianza = None
    
    
    def __init__(self, n_components=-1):
        
        self.n_components = n_components

    # Filtrado de los genes 
    def fit(self, X, y=None):
        """
        Fits the Mann-Whitney genes selection.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_genes]
            The training input samples.

        y : array-like, shape = [n_samples]
            The target values.
        """
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
        """
        Reduces the input X to the genes selected by Mann-Whitney.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_genes]
            The training input samples.


        Returns
        -------
        X : array-like, shape = [n_samples, n_genes_]
            The input matrix X's columns are reduced to the genes which were
            selected by Mann-Whitney.
        """
        X = np.asarray(X)
        return X[:, self.selectedGenesIndexes]

    def fit_transform(self, X, y=None):
        """
        Fits Mann-Whitney, then reduces the input X to the selected genes.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_genes]
            The training input samples.

        y : array-like, shape = [n_samples]
            The target values.

        Returns
        -------
        X : array-like, shape = [n_samples, n_genes_]
            The input matrix X's columns are reduced to the genes which were
            selected by Mann-Whitney.
        """
        self.fit(X,y)
        return self.transform(X,y)
