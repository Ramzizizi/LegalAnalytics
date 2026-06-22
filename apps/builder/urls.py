from django.urls import path
from . import views

app_name = 'builder'

urlpatterns = [
    path('', views.builder_home, name='home'),
    path('basket/add/<str:model_type>/<int:pk>/', views.basket_add, name='basket_add'),
    path('basket/remove/<str:model_type>/<int:pk>/', views.basket_remove, name='basket_remove'),
    path('basket/clear/', views.basket_clear, name='basket_clear'),
    path('export/', views.export_docx, name='export'),
]
