# Aplicaion web para el analisis visual de conjuntos de datos de expresion genética

## Descripción 
Aplicacion web desarrollada en Python junto con el framework web [Django](https://www.djangoproject.com/) que ofrece las siguientes funcionalidades básicas:
1. Cargar y almacenar conjuntos de datos de expresión genética
2. Descargar conjuntos de datos o partes de conjuntos resultantes de la aplicación de filtros
3. Llevar a cabo análisis exploratorios sobre datos a través de visualizaciones interactivas
4. Compartir con otros usuarios los resultados de los análisis, así como los filtros aplicados a los datos

## Estructura del proyecto
```
GeneticServer/
├── boards
│   ├── admin.py
│   ├── apps.py
│   ├── boruta.py
│   ├── dataSetMongo.py
│   ├── forms.py
│   ├── gbr.py
│   ├── __init__.py
│   ├── mannWhitney.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
├── GeneticServer
│   ├── custommiddleware.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── manage.py
├── media
│   ├── boardCSV
│   └── profilePhotos
├── static
│   ├── bootstrap
│   │   ├── css
│   │   │   ├── bootstrap.css
│   │   │   ├── bootstrap.css.map
│   │   │   ├── bootstrap.min.css
│   │   │   ├── bootstrap.min.css.map
│   │   │   ├── bootstrap-theme.css
│   │   │   ├── bootstrap-theme.css.map
│   │   │   ├── bootstrap-theme.min.css
│   │   │   └── bootstrap-theme.min.css.map
│   │   ├── fonts
│   │   │   ├── glyphicons-halflings-regular.eot
│   │   │   ├── glyphicons-halflings-regular.svg
│   │   │   ├── glyphicons-halflings-regular.ttf
│   │   │   ├── glyphicons-halflings-regular.woff
│   │   │   └── glyphicons-halflings-regular.woff2
│   │   └── js
│   │       ├── bootstrap.js
│   │       ├── bootstrap.min.js
│   │       └── npm.js
│   ├── css
│   │   ├── c3.css
│   │   ├── d3.parcoords.css
│   │   ├── home.css
│   │   ├── style.css
│   │   └── w3.css
│   ├── images
│   │   ├── admin.jpg
│   │   ├── añadir.png
│   │   ├── eliminar.jpg
│   │   ├── logotipo.png
│   │   ├── microscopio.jpg
│   │   ├── no_Photo.jpeg
│   │   └── servidorGenes.jpg
│   └── js
│       ├── c3
│       │   └── c3.min.js
│       ├── d3
│       │   ├── API.md
│       │   ├── CHANGES.md
│       │   ├── d3.js
│       │   ├── d3.min.js
│       │   ├── LICENSE
│       │   └── README.md
│       ├── jQuery
│       │   └── jquery.min.js
│       ├── parcoords
│       │   ├── d3.parcoords.js
│       │   └── divgrid.js
│       └── searchDatabase.js
└── users
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── __init__.py
    ├── models.py
    ├── templates
    │   ├── account
    │   │   ├── account_inactive.html
    │   │   ├── base.html
    │   │   ├── email_confirm.html
    │   │   ├── login.html
    │   │   ├── logout.html
    │   │   ├── password_change.html
    │   │   ├── password_reset_done.html
    │   │   ├── password_reset_from_key_done.html
    │   │   ├── password_reset_from_key.html
    │   │   ├── password_reset.html
    │   │   ├── signup.html
    │   │   └── verification_sent.html
    │   ├── base.html
    │   └── home
    │       ├── base.html
    │       ├── contact.html
    │       ├── home.html
    │       ├── home_shared.html
    │       ├── index.html
    │       ├── profile.html
    │       └── readMore.html
    ├── tests.py
    ├── urls.py
    ├── views.py
```
