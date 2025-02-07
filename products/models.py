from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ClothingItem(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double Extra Large'),
    ]
    
    COLOR_CHOICES = [
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Black', 'Black'),
        ('White', 'White'),
        ('Green', 'Green'),
        ('Yellow', 'Yellow'),
    ]
   
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    popularity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/clothing_images/')
    category = models.ForeignKey('Category', related_name='clothing_items', on_delete=models.CASCADE, default=1)
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, default='M')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='Black')

    def average_rating(self):
        ratings = self.reviews.all()
        if ratings:
            return sum([review.rating for review in ratings]) / len(ratings)
        return 0.0

    def __str__(self):
        return self.name


class Review(models.Model):
    clothing_item = models.ForeignKey(ClothingItem, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    comment = models.TextField() 
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} review on {self.clothing_item.name}'

    class Meta:
        unique_together = ('clothing_item', 'user')


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clothing_item = models.ForeignKey(ClothingItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'clothing_item']  

    def __str__(self):
        return f"Wishlist for {self.user.username} - {self.clothing_item.name}"
