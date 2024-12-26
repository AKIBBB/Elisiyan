from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ClothingItemViewSet, CategoryViewSet,ReviewViewSet,WishlistViewSet
router = DefaultRouter()
router.register(r'clothing', ClothingItemViewSet, basename='clothing')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'product/clothing', ClothingItemViewSet, basename='clothing-item')

urlpatterns = router.urls
urlpatterns = [
    path('', include(router.urls)),  
]