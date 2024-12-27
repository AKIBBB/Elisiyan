from rest_framework import serializers
from .models import Category, ClothingItem, Review, Wishlist


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name']


class ClothingItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nesting category serializer
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
            'average_rating'
        ]


from rest_framework import serializers
from .models import Review

from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    # Include reviewer's username in the response
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'clothing_item', 'user', 'user_name', 'comment', 'rating', 'created_at']



class WishlistSerializer(serializers.ModelSerializer):
    clothing_item = ClothingItemSerializer(read_only=True)  # Show clothing item details
    user = serializers.StringRelatedField(read_only=True)  # Display user's string representation

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'clothing_item', 'created_at']
