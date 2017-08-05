# -*- coding: utf-8 -*-
"""
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

Python module responsible for configuring the middleware to prevent 
the browser from saving data in its cache while browsing the platform 

"""
# -*- coding: utf-8 -*-
from django.utils.cache import add_never_cache_headers
from django.utils.deprecation import MiddlewareMixin

# Evitar la caché del navegador mientras se usa la plataforma 
class DisableClientSideCachingMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response
