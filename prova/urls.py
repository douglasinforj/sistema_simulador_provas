from django.urls import path
from . import views

urlpatterns = [
    path('', views.iniciar_prova, name='iniciar_prova'),
    path('prova/<uuid:prova_uuid>', views.realizar_prova, name='realizar_prova'),
    path('resultado/<uuid:prova_uuid>/', views.resultado_prova, name='resultado_prova'),
    path('ranking/', views.ranking, name='ranking'),
    path('certificado/<uuid:prova_uuid>/', views.emitir_certificado, name='emitir_certificado'),
    path('administrador/', views.administrador, name='administrador'),
    
]
