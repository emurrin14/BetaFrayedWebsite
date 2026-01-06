from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index, name='index'),
  path('product/<slug:slug>/', views.Product_View, name='product'),
]