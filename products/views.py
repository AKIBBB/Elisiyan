from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import generics,serializers
from rest_framework.response import Response
from rest_framework import status
from .models import ClothingItem, Review, Category
from .serializers import ClothingItemSerializer, CategorySerializer, ReviewSerializer
import django_filters
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg
from .models import Wishlist
from .serializers import WishlistSerializer

# Custom filter for clothing items
class ClothingItemFilter(django_filters.FilterSet):
    size = django_filters.ChoiceFilter(choices=ClothingItem.SIZE_CHOICES)
    color = django_filters.ChoiceFilter(choices=ClothingItem.COLOR_CHOICES)
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    
    class Meta:
        model = ClothingItem
        fields = ['size', 'color', 'category']

class ClothingItemViewSet(ReadOnlyModelViewSet):
    queryset = ClothingItem.objects.all()
    serializer_class = ClothingItemSerializer
    filterset_class = ClothingItemFilter  # Add the filter set here

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by size if 'size' is passed in query params
        size = self.request.query_params.get('size', None)
        if size:
            queryset = queryset.filter(size=size)

        # Filter by color if 'color' is passed in query params
        color = self.request.query_params.get('color', None)
        if color:
            queryset = queryset.filter(color=color)

        # Filter by category if 'category' is passed in query params
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__id=category)

        # Sorting functionality (optional)
        sort_by = self.request.query_params.get('sort_by', 'price')  # Default to 'price'
        if sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == 'popularity':
            queryset = queryset.order_by('-popularity')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # If no products are available after applying filters
        if not queryset.exists():
            return Response({"message": "No products available"}, status=status.HTTP_404_NOT_FOUND)

        # Calculate average rating for each clothing item
        for clothing_item in queryset:
            # Calculate the average rating for each product
            avg_rating = clothing_item.reviews.aggregate(Avg('rating'))['rating__avg']
            clothing_item.average_rating = avg_rating if avg_rating is not None else 0

        # Serialize the clothing items with the added average rating
        serializer = self.get_serializer(queryset, many=True)
        # Add the average_rating to each product data in the response
        data = serializer.data
        for i, item in enumerate(data):
            item['average_rating'] = queryset[i].average_rating

        return Response(data)

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter(parent__isnull=True)  
    serializer_class = CategorySerializer


# no
class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        clothing_item = serializer.validated_data['clothing_item']
        user = self.request.user
        # Ensure one review per clothing item per user
        if Review.objects.filter(clothing_item=clothing_item, user=user).exists():
            raise serializers.ValidationError('You have already reviewed this item.')
        serializer.save(user=user)
        
        
class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        # Fetch the specific clothing item by its primary key (pk)
        clothing_item = self.get_object()
        
        # Retrieve all reviews related to the clothing item
        reviews = clothing_item.reviews.all()
        
        # Serialize the reviews
        serializer = ReviewSerializer(reviews, many=True)
        
        # Return the reviews as a response
        return Response(serializer.data)
    
    
    
# [[[]]]

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self):
        # Filter the wishlist by the currently logged-in user
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_to_wishlist(self, request):
        # Get the clothing item ID from the request data
        clothing_item_id = request.data.get('clothing_item')
        try:
            clothing_item = ClothingItem.objects.get(id=clothing_item_id)
        except ClothingItem.DoesNotExist:
            return Response({"error": "Clothing item not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the item is already in the user's wishlist
        if Wishlist.objects.filter(user=request.user, clothing_item=clothing_item).exists():
            return Response({"message": "Item already in wishlist"}, status=status.HTTP_400_BAD_REQUEST)

        # Add the clothing item to the wishlist
        wishlist_item = Wishlist.objects.create(user=request.user, clothing_item=clothing_item)
        serializer = self.get_serializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove_from_wishlist(self, request):
        # Get the clothing item ID from the request data
        clothing_item_id = request.data.get('clothing_item')
        try:
            clothing_item = ClothingItem.objects.get(id=clothing_item_id)
        except ClothingItem.DoesNotExist:
            return Response({"error": "Clothing item not found"}, status=status.HTTP_404_NOT_FOUND)

        # Remove the clothing item from the wishlist
        try:
            wishlist_item = Wishlist.objects.get(user=request.user, clothing_item=clothing_item)
            wishlist_item.delete()
            return Response({"message": "Item removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)
        except Wishlist.DoesNotExist:
            return Response({"error": "Item not found in wishlist"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def view_wishlist(self, request):
        # Get the user's wishlist
        wishlist_items = self.get_queryset()
        serializer = self.get_serializer(wishlist_items, many=True)
        return Response(serializer.data)