from django.contrib import admin
from .models import Product, Review, Cart, CartItem

admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
