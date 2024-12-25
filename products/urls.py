from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClothingItemViewSet, CategoryViewSet,ReviewViewSet,WishlistViewSet
router = DefaultRouter()
router.register(r'clothing', ClothingItemViewSet, basename='clothing')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = router.urls
