from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import generics, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg
from django.http import Http404
import django_filters
from rest_framework.views import APIView
from django_filters import rest_framework as filters 
from rest_framework.permissions import IsAuthenticated
from .models import ClothingItem, Review, Category, Wishlist
from .serializers import ClothingItemSerializer



from .serializers import (
    ClothingItemSerializer,
    CategorySerializer,
    ReviewSerializer,
    WishlistSerializer,
)
from rest_framework.permissions import IsAdminUser

class ClothingItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    size = django_filters.ChoiceFilter(choices=ClothingItem.SIZE_CHOICES)
    color = django_filters.ChoiceFilter(choices=ClothingItem.COLOR_CHOICES)
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    price_min = filters.NumberFilter(field_name="price", lookup_expr='gte', label="Minimum Price")
    price_max = filters.NumberFilter(field_name="price", lookup_expr='lte', label="Maximum Price")
    class Meta:
        model = ClothingItem
        fields = ["name", "size", "color", "category","popularity",'price_min', 'price_max']


# Clothing Item ViewSet



class ClothingItemViewSet(ModelViewSet):  
    queryset = ClothingItem.objects.all()
    serializer_class = ClothingItemSerializer
    filterset_class = ClothingItemFilter
    permission_classes = [IsAdminUser]  

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        name = params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        size = params.get("size")
        if size:
            queryset = queryset.filter(size=size)

        color = params.get("color")
        if color:
            queryset = queryset.filter(color=color)

        category = params.get("category")
        if category:
            queryset = queryset.filter(category__name__iexact=category)

        sort_by = params.get("sort_by", "price")
        if sort_by == "price":
            queryset = queryset.order_by("price")
        elif sort_by == "popularity":
            queryset = queryset.order_by("-popularity")

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No products available"}, status=status.HTTP_404_NOT_FOUND)

        # Calculate average rating
        for clothing_item in queryset:
            avg_rating = clothing_item.reviews.aggregate(Avg("rating"))["rating__avg"]
            clothing_item.average_rating = avg_rating if avg_rating else 0

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        for i, item in enumerate(data):
            item["average_rating"] = queryset[i].average_rating

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        clothing_item = get_object_or_404(self.queryset, pk=pk)

        avg_rating = clothing_item.reviews.aggregate(Avg("rating"))["rating__avg"]
        clothing_item.average_rating = avg_rating if avg_rating else 0

        serializer = self.get_serializer(clothing_item)
        data = serializer.data
        data["average_rating"] = clothing_item.average_rating

        return Response(data)


# Category ViewSet
class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.filter()
    serializer_class = CategorySerializer


# Review Create View
class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        user = self.request.user
        clothing_item = serializer.validated_data["clothing_item"]
        if Review.objects.filter(clothing_item=clothing_item, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this item.")
        
        serializer.save(user=user)

# Review ViewSet

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        """
        Retrieve all reviews for a specific clothing item.
        """
        clothing_item = get_object_or_404(ClothingItem, pk=pk)
        reviews = clothing_item.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Create a review. Only logged-in users are allowed to submit reviews.
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required to create a review."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        clothing_item = serializer.validated_data["clothing_item"]
        if Review.objects.filter(clothing_item=clothing_item, user=request.user).exists():
            return Response(
                {"detail": "You have already reviewed this item."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Wishlist ViewSet

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]  

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Wishlist.objects.none() 
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def add_to_wishlist(self, request):

        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        clothing_item_id = request.data.get("clothing_item")
        clothing_item = get_object_or_404(ClothingItem, id=clothing_item_id)

        if Wishlist.objects.filter(user=request.user, clothing_item=clothing_item).exists():
            return Response(
                {"message": "Item already in wishlist"}, status=status.HTTP_400_BAD_REQUEST
            )

        wishlist_item = Wishlist.objects.create(user=request.user, clothing_item=clothing_item)
        serializer = self.get_serializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def remove_from_wishlist(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        clothing_item_id = request.data.get("clothing_item")
        clothing_item = get_object_or_404(ClothingItem, id=clothing_item_id)

        wishlist_item = Wishlist.objects.filter(user=request.user, clothing_item=clothing_item)
        if wishlist_item.exists():
            wishlist_item.delete()
            return Response({"message": "Item removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"error": "Item not found in wishlist"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["get"])
    def view_wishlist(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        wishlist_items = self.get_queryset()
        serializer = self.get_serializer(wishlist_items, many=True)
        return Response(serializer.data)



class AdminManageProducts(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        products =ClothingItem.objects.all()
        serializer =ClothingItemSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer =ClothingItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class AdminDeleteProduct(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, product_id):
        try:
            return ClothingItem.objects.get(id=product_id)
        except ClothingItem.DoesNotExist:
            raise Http404("Product not found")

    def delete(self, request, product_id):
        product = self.get_object(product_id)
        product.delete()
        return Response({"message": "Product deleted successfully."}, status=200)