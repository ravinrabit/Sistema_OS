# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Clientes
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/novo/', views.cliente_criar, name='cliente_criar'),
    path('clientes/<int:pk>/', views.cliente_detalhe, name='cliente_detalhe'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    
    # Ordens de Serviço
    path('ordens/', views.ordem_lista, name='ordem_lista'),
    path('ordens/nova/', views.ordem_criar, name='ordem_criar'),
    path('ordens/<int:pk>/', views.ordem_detalhe, name='ordem_detalhe'),
    path('ordens/<int:pk>/editar/', views.ordem_editar, name='ordem_editar'),
    path('ordens/<int:pk>/excluir/', views.ordem_excluir, name='ordem_excluir'),  # ← NOVA LINHA
    path('ordens/<int:pk>/status/<str:novo_status>/', views.ordem_mudar_status, name='ordem_mudar_status'),
    
    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
    
    # Notificações
    path('notificacoes/', views.notificacao_lista, name='notificacao_lista'),
    path('notificacoes/<int:pk>/lida/', views.notificacao_marcar_lida, name='notificacao_marcar_lida'),
    path('notificacoes/marcar-todas/', views.notificacao_marcar_todas, name='notificacao_marcar_todas'),
]