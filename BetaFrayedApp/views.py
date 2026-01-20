from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.utils.timezone import localtime
from .models import Product, Product_Variant, Cart, CartItem
import json
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from taggit.models import Tag

stripe.api_key = settings.STRIPE_SECRET_KEY

#create your views here
def Index(request):
    return render(request, 'index.html')



def Shop_view(request):
    new_products = Product.objects.filter(tags__name__iexact="New").distinct()
    denim_products = Product.objects.filter(tags__name__iexact="Denim").distinct()
    context = {
        'new_products': new_products,
        'denim_products': denim_products,
    }
    return render(request, 'shop.html', context)



def Product_View(request, slug):
   product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants__color'), 
        slug=slug
   )
   context = {
        'product': product,
   }
   return render(request, 'product.html', context)



def cart_view(request):
    cart = get_cart(request)
    items = cart.items.all()
    total = cart.total_price()

    context = {
        "cart": cart,
        "items":items,
        "total":total,
    }
    return render(request, "cart.html", context)



def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart



@require_POST
def add_to_cart(request, product_id):
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)

    variant_id = request.POST.get("variant_id")
    if not variant_id:
        return HttpResponseBadRequest("Variant must be selected.")

    variant = get_object_or_404(Product_Variant, id=variant_id)

    # Read quantity from the form
    quantity = int(request.POST.get("quantity", 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={"quantity": quantity},
    )
    if not created:
        # Increase by the submitted quantity
        cart_item.quantity += quantity
        cart_item.save()

    return JsonResponse({
        "success": True,
        "quantity": cart_item.quantity,
    })



def subtract_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    
    else:
        cart_item.delete()
    
    return redirect("cart")



def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect("cart")


def coming_soon_view(request):
    return render(request, 'comingsoon.html') 