from django.shortcuts import render

def Index(request):
    return render(request, 'index.html')

def Product_View(request, slug):
   product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants__size', 'variants__color'), 
        slug=slug
   )
   context = {
        'product': product,
   }
   return render(request, 'product.html', context)