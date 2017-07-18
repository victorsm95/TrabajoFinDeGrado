# -*- coding: utf-8 -*-
'''
Definicion
---
Modulo python que consta de las señales definidas para el uso de notificaciones en la aplicación
'''
import django.dispatch
# Señal de comparticion de board, enviada al compartir un board para enviar un e-mail 
# de notificacion al usuario correspondiente
board_signal_shared = django.dispatch.Signal(providing_args=["board"])
# Señal de guardado de board, enviada despues de realizar los filtrados para confirmar el board 
# y guardarlo en este estado en la base de datos
board_signal_save = django.dispatch.Signal(providing_args=["board"])