from django.db import models
from taggit.managers import TaggableManager
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils import timezone
from django.conf import settings


# Create your models here.
class Product(models.Model):
  name = models.CharField(max_length=50)
  slug = models.SlugField(unique=True, blank=True)
  description = models.TextField()
  sku = models.CharField(max_length=50, unique=True)
  price = models.IntegerField(default=0)
  stock = models.PositiveIntegerField(default=0)
  isinstock = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  tags = TaggableManager()

  @property
  def image0(self):
    """ returns first image associated w product, if not image, none """
    first_image = self.images.first()
    return first_image.image if first_image else None

  @property
  def price_display(self):
    return f"{self.price / 100:.2f}"

  def save(self, *args, **kwargs):
      if not self.slug:
          self.slug = slugify(self.name)
      
      self.isinstock = self.stock > 0
      super().save(*args, **kwargs)

  def __str__(self):
      return self.name



class ProductImage(models.Model):
  product = models.ForeignKey(
     Product,
     on_delete=models.CASCADE,
     related_name="images"
  )
  image = models.ImageField (upload_to="products/")
  order = models.PositiveIntegerField(default=0, help_text="Set display order, 0 is primary image")

  def __str__(self):
    return f"Image For {self.product.name}"
  
  class Meta:
     """ Defines default ordering for image queries. """
     ordering = ['order']



class Size(models.Model):
  name = models.CharField(max_length=10)
  def __str__(self):
    return self.name
  


class Color(models.Model):
  name = models.CharField(max_length=10)
  def __str__(self):
    return self.name



class Product_Variant(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
  size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
  color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
  stock = models.PositiveIntegerField(default=0)
  image = models.ImageField (upload_to="products/", null=True, blank=True)
  order = models.PositiveIntegerField(default=0, help_text="Set display order, 0 is primary image")



class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart {self.pk} for {self.user}"
        return f"Cart {self.pk} for session {self.session_key}"

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())
    
    def total_price_display(self):
       return f"{self.total_price() / 100:.2f}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variant, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "variant")

    def subtotal(self):
        if self.variant:
            return self.variant.product.price * self.quantity
        else:
            return self.product.price * self.quantity

    def subtotal_display(self):
        return f"{self.subtotal() / 100:.2f}"

    def __str__(self):
        return f"{self.quantity} x {self.product.title} in Cart {self.cart.pk}"