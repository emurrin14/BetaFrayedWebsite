from django.urls import path
from . import views

urlpatterns = [
  path('', views.Index, name='index'),
  path('shop', views.Shop_view, name="shop"),
  path('product/<slug:slug>/', views.Product_View, name='product'),
  path('cart', views.cart_view, name='cart'),
  path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
  path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
  path('cart/increment/<int:item_id>/', views.increment_cart_item, name='increment_cart_item'),
  path('cart/subtract/<int:item_id>/', views.subtract_from_cart, name='subtract_from_cart'),
  path('create-checkout-session/', views.create_checkout_session, name='create-checkout-session'),
  path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
  path('success/', views.success_view, name='success'),
  path('cancel/', views.cancel_view, name='cancel'),
]