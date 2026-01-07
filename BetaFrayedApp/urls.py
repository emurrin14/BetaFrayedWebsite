from django.urls import path
from . import views

urlpatterns = [
  path('', views.Index, name='index'),
  path('shop', views.Shop_view, name="shop"),
  path('product/<slug:slug>/', views.Product_View, name='product'),
  
]