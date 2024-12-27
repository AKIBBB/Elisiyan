from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import generics, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg
import django_filters
from rest_framework.permissions import IsAuthenticated
from .models import ClothingItem, Review, Category, Wishlist
from .serializers import (
    ClothingItemSerializer,
    CategorySerializer,
    ReviewSerializer,
    WishlistSerializer,
)

# Custom filter for clothing items
class ClothingItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    size = django_filters.ChoiceFilter(choices=ClothingItem.SIZE_CHOICES)
    color = django_filters.ChoiceFilter(choices=ClothingItem.COLOR_CHOICES)
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())

    class Meta:
        model = ClothingItem
        fields = ["name", "size", "color", "category"]


# Clothing Item ViewSet
class ClothingItemViewSet(ReadOnlyModelViewSet):
    queryset = ClothingItem.objects.all()
    serializer_class = ClothingItemSerializer
    filterset_class = ClothingItemFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        # Filtering
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
            queryset = queryset.filter(category__name__iexact=category)  # Filter by category name

        # Sorting
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

        # Annotate with average rating
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
        clothing_item = serializer.validated_data["clothing_item"]
        user = self.request.user
        # Check if the user has already reviewed this item
        if Review.objects.filter(clothing_item=clothing_item, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this item.")
        serializer.save(user=user)

# Review ViewSet
class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # Custom action to retrieve reviews for a specific product (clothing item)
    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        clothing_item = get_object_or_404(ClothingItem, pk=pk)
        reviews = clothing_item.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

# Wishlist ViewSet

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get_queryset(self):
        # Ensure the user is authenticated before filtering the wishlist
        if not self.request.user.is_authenticated:
            return Wishlist.objects.none()  # Return an empty queryset for unauthenticated users
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def add_to_wishlist(self, request):
        # Ensure the user is authenticated
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
        # Ensure the user is authenticated
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
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        wishlist_items = self.get_queryset()
        serializer = self.get_serializer(wishlist_items, many=True)
        return Response(serializer.data)
