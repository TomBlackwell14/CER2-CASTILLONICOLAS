from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    path('informacion/', views.informacion, name='informacion'),


]
