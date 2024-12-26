from rest_framework import serializers
from .models import Category, ClothingItem, Review, Wishlist

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'subcategories']

class ClothingItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'size', 'color', 'reviews', 'average_rating']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')  

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at', 'clothing_item']

class WishlistSerializer(serializers.ModelSerializer):
    clothing_item = serializers.StringRelatedField()  

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'clothing_item', 'created_at']
