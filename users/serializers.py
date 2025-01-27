from rest_framework import serializers
from .import models
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False)
    class Meta:
        model=models.Users
        fields='__all__'
    
    
class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(required=True)
    class Meta:
        model=User
        fields=['username', 'first_name','last_name','email','password','confirm_password']
    
    def save(self):
        username=self.validated_data['username']
        email=self.validated_data['email']
        password=self.validated_data['password']
        password2=self.validated_data['confirm_password']
        
        if password !=password2:
            raise serializers.ValidationError({'error' : "Password didn't match"})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'error' : "Email allready exists"})
        account=User(username=username,email=email)
        account.set_password(password)
        account.is_active=False
        account.save()
        return account
    
    
class UserLoginSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    password=serializers.CharField(required=True)
    
    


class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)

    def validate(self, attrs):
        return attrs


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'buy_history', 'created_at']
        depth = 1  