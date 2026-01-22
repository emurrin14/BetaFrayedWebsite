from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.utils.timezone import localtime
from .models import Product, Product_Variant, Cart, CartItem, Order, OrderItem
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
        "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY,
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



def increment_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart")



def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect("cart")


# CUSTOM STRIPE CHECKOUT VIEW
@csrf_exempt
def create_checkout_session(request):
    cart = get_cart(request)

    if cart.items.count() == 0:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    line_items = []

    for item in cart.items.select_related(
        "product", "variant__size", "variant__color"
    ):

        product = item.product
        variant = item.variant

        #product name with variant info
        name = product.name
        details = []
        if variant:
            if variant.size:
                details.append(f"Size: {variant.size.name}")
            if variant.color:
                details.append(f"Color: {variant.color.name}")
        if details :
            name += f" ({', '.join(details)})"

        #product image (first image)
        image_url = None
        if product.image0:
            image_url = product.image0.url
            if not image_url.startswith("http"):
                image_url = request.build_absolute_uri(image_url)

        #stripe line item
        line_item = {
            "price_data": {
                "currency": "usd",
                "unit_amount": product.price,
                "product_data": {
                    "name": name,
                    "images": [image_url] if image_url else [],
                },
            },
            "quantity": item.quantity,
        }

        line_items.append(line_item)

    #optional discount code (stripe promotion code id)
    promo_code = request.GET.get("promo_code")
    discounts = []
    if promo_code:
        discounts.append({"promotion_code": promo_code})

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=line_items,
            discounts=discounts if discounts else None,

            metadata={
                "cart_id": cart.id,
                "user_id":request.user.id if request.user.is_authenticated else None
            },

            success_url=request.build_absolute_uri(reverse("success")),
            cancel_url=request.build_absolute_uri(reverse("cancel")),
        )

        return JsonResponse({"id": session.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


#stripe webhook view
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # 1. Get the cart ID from the metadata we sent earlier
        cart_id = session['metadata'].get('cart_id')
        
        # 2. Get customer info from Stripe Session
        customer_details = session.get('customer_details') or {}
        email = customer_details.get('email', '')
        name = customer_details.get('name', '')
        address_data = customer_details.get('address') or {}

        # Format address for storage
        address_str = f"{address_data.get('line1', '')}, {address_data.get('line2', '')}"
        city = address_data.get('city', '')
        
        try:
            cart = Cart.objects.get(id=cart_id)
            
            # 3. Create the Order
            order = Order.objects.create(
                user=cart.user, # This might be None if guest, which is fine
                full_name=name,
                email=email,
                address=address_str,
                city=city,
                stripe_payment_intent=session.get('payment_intent'),
                amount_paid=cart.total_price(), # Or session['amount_total'] / 100
                paid=True
            )

            # 4. Move Cart Items to Order Items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # 5. Clear the Cart (Delete it)
            cart.delete()
            
            print(f"Order {order.id} created and Cart {cart_id} deleted.")

        except Cart.DoesNotExist:
            print("Cart not found (already processed?)")

    return HttpResponse(status=200)



def success_view(request):
   return render(request, 'success.html')



def cancel_view(request):
   return render(request, 'cancel.html')



def coming_soon_view(request):
    return render(request, 'comingsoon.html') 