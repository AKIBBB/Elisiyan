from rest_framework import serializers
from .models import Category, ClothingItem,Review,Wishlist

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'subcategories']

class ClothingItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'description', 'price', 'image', 'category', 'average_rating']




# m

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'created_at', 'clothing_item']




class ClothingItemSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'description', 'price', 'popularity', 'image', 'category', 'reviews']
        
        
        
# pp
class WishlistSerializer(serializers.ModelSerializer):
    clothing_item = serializers.StringRelatedField()  # Display the clothing item's name (or any other field)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'clothing_item', 'created_at']