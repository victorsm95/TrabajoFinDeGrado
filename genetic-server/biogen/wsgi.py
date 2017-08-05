# -*- coding: utf-8 -*-
"""
Author: Víctor Sánchez Martín <victorsm156548@usal.es>

WSGI config for biogen project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biogen.settings")

application = get_wsgi_application()
