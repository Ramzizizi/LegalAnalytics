from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    # Списки
    path('norms/', views.norm_list, name='norm_list'),
    path('cases/', views.case_list, name='case_list'),
    path('opinions/', views.opinion_list, name='opinion_list'),
    # Карточки
    path('norm/<int:pk>/', views.norm_detail, name='norm_detail'),
    path('case/<int:pk>/', views.case_detail, name='case_detail'),
    path('opinion/<int:pk>/', views.opinion_detail, name='opinion_detail'),
    # Граф (JSON API)
    path('graph/<str:record_type>/<int:pk>/', views.graph_data, name='graph_data'),
]
