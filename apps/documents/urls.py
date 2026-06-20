from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.select_template, name='select_template'),
    path('create/<int:template_id>/', views.create, name='create'),
    path('journal/', views.journal, name='journal'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/download/<str:fmt>/', views.download, name='download'),
]
