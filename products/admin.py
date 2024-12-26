from django.contrib import admin
from django.contrib import admin
from .models import Category, ClothingItem,Review
# Register your models here.

from django.contrib import admin
from .models import Category, ClothingItem

admin.site.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent']
    search_fields = ['name']
    list_filter = ['parent']

admin.site.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'category', 'price', 'popularity']
    search_fields = ['name', 'category__name']
    list_filter = ['category']
    
admin.site.register(Review)



