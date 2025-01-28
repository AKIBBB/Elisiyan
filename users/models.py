from django.db import models
from django.contrib.auth.models import User

class Users(models.Model):
    user =models.OneToOneField(User,on_delete=models.CASCADE)
    mobile_no=models.CharField(max_length=12)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    buy_history = models.TextField(default="", blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

    
    
    
    
#  {
# "username":"superman",
# "password":"abcd1234%A"
# }