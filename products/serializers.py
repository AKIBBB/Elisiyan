from rest_framework import serializers
from .models import Category, ClothingItem, Review, Wishlist
from rest_framework import serializers
from .models import Review

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class ClothingItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = ClothingItem
        fields = [
            'id', 
            'name', 
            'description', 
            'price', 
            'image', 
            'category', 
            'size', 
            'color', 
            'average_rating',
            'popularity'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'clothing_item', 'rating', 'comment', 'reviewer_name', 'created_at']
        read_only_fields = ['reviewer_name', 'created_at']




class WishlistSerializer(serializers.ModelSerializer):
    clothing_item = ClothingItemSerializer(read_only=True)  
    user = serializers.StringRelatedField(read_only=True)  

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'clothing_item', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingItem
        fields = '__all__'