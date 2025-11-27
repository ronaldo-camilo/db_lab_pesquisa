from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('pacientes/<int:pk>/', views.detalhe_paciente, name='detalhe_paciente'),
    path('pacientes/novo/', views.criar_paciente, name='criar_paciente'),
    path('pacientes/<int:pk>/editar/', views.editar_paciente, name='editar_paciente'),
    path('pacientes/<int:pk>/deletar/', views.deletar_paciente, name='deletar_paciente'),
    path('upload/', views.upload_planilha, name='upload_planilha'),
    path('conflitos/', views.resolver_conflitos, name='resolver_conflitos'),
    path('exportar/', views.exportar_dados, name='exportar_dados'),
]

