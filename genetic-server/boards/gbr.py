# -*- coding: utf-8 -*-
'''
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

Python module in charge of performing the GBR filtering, taking the result of the Mann-Whitney prefilter as the initiation data.
'''

from sklearn.base import BaseEstimator, TransformerMixin, ClassifierMixin
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from scipy.stats import mannwhitneyu

import operator

import numpy as np

class GBRT_CBR(BaseEstimator, ClassifierMixin):
    """
    Improved Python implementation of the GBRT_CBR filter.

    CBR with GBRT-based feature selection as described in the paper:
          "A CBR framework with gradient boosting based feature selection for lung cancer subtype classification"
          https://doi.org/10.1016/j.compbiomed.2017.05.010

    Parameters
    ----------

    n_estimators: int, default = 400
        Sets the number of estimators in the chosen ensemble method.

    learning_rate: float, default = 0.5
    
    n_neighbors: int, default = 5

    selectedGenesIndexes: list, datasets indexes of genes selected
    """
    n_estimators = None
    learning_rate = None
    rawweights = None
    n_neighbors = None
    kNN = None
    selectedGenesIndexes = None

    
    def __init__(self, n_estimators=400, learning_rate=.5, n_neighbors=5, max_depth=1):
    
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.n_neighbors = n_neighbors
        self.max_depth = max_depth 

        
    def fit(self, X, y=None):
        """
        Fits the GBR feature selection with the provided estimator.

        Parameters
        ----------
        X : array-like, shape = [n_samples, n_genes]
            The training input samples.

        y : array-like, shape = [n_samples]
            The target values.
        """
               
        clf = GradientBoostingClassifier(n_estimators=self.n_estimators, learning_rate=self.learning_rate, criterion="mse", max_depth=self.max_depth).fit(X, y)
        
        self.rawweights = clf.feature_importances_/np.sum(clf.feature_importances_)
        
        X1 = X*self.rawweights 
        self.kNN = KNeighborsClassifier(n_neighbors=self.n_neighbors, weights="distance")
        self.kNN.fit(X1, y)
        self.trainingData = (X1, y)
        
        return self
    
    def retain(self, x,y):
    
        x = x*self.rawweights
        self.kNN = KNeighborsClassifier(n_neighbors=self.n_neighbors, weights="distance")
        newData = (np.concatenate([self.trainingData[0], [x]]), np.concatenate([self.trainingData[1], [y]]))
        self.kNN.fit(newData[0], newData[1])
        self.trainingData = newData
        return
        
    def predict(self, X, y=None):
        
        X1 = X*self.rawweights 
        return self.kNN.predict(X1)
    
    def predict_proba(self, X, y=None):
        
        X1 = X*self.rawweights 
        return self.kNN.predict_proba(X1)
