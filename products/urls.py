from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClothingItemViewSet,
    CategoryViewSet,
    ReviewCreateView,
    WishlistViewSet,
    ReviewViewSet,
)

router = DefaultRouter()
router.register(r'clothing', ClothingItemViewSet, basename='clothing')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),  
    path('reviews/create/', ReviewCreateView.as_view(), name='review-create'), 
]
