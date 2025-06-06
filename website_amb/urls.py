from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('resultado', views.resultado, name='resultado'),
    path('sobre', views.sobre, name='sobre'),
    path('contato', views.contato, name='contato'),
    path('termos', views.termos, name='termos'),
    path('politica_privacidade', views.politica_privacidade, name='politica_privacidade'),
    path('politica_afiliados', views.politica_afiliados, name='politica_afiliados'),
]
