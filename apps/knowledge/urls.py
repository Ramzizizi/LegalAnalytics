from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('norm/<int:pk>/', views.norm_detail, name='norm_detail'),
    path('case/<int:pk>/', views.case_detail, name='case_detail'),
    path('opinion/<int:pk>/', views.opinion_detail, name='opinion_detail'),
]
