from django.shortcuts import render,redirect
from rest_framework import viewsets
from .import models
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework import status
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.utils.encoding import force_str
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from django.urls import reverse
from .models import Profile
from rest_framework.permissions import IsAdminUser
from datetime import datetime


class UserRegistrationApiView(APIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            User.Profile.objects.create(user=User)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"https://elisiyan.onrender.com/users/active/{uid}/{token}"
            email_subject = "Confirm Your Email"
            email_body = render_to_string('auth_email.html', {'confirm_link': confirm_link})
            email = EmailMultiAlternatives(email_subject, '', to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()

            return Response({"message": "Check your mail for confirmation"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')  
    else:
        return redirect('register')  

    
    
    
class UserLoginApiView(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=self.request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)
                if user.is_staff and user.is_superuser:
                    return redirect('admin_interface') 
                return Response({'token': token.key, 'user_id': user.id})
            else:
                return Response({'error': "Invalid Credential"}, status=200)
        return Response(serializer.errors, status=200)
    
    


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        if not request.auth:
            raise AuthenticationFailed("Authentication token not provided or invalid.")
        request.auth.delete()
        return Response({"message": "Logged out successfully"}, status=200)
    



class AdminInterfaceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            return Response({"message": "Welcome to the admin interface."})
        elif request.user.is_superuser:
            return Response({"message": "Welcome to the superuser interface."})
        else:
            return Response({"error": "Forbidden"}, status=403)
        

    
class AdminManageUsers(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = serializers.AdminSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer = serializers.AdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class AdminDeleteUser(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return Response({"message": "User deleted successfully."}, status=200)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        
        


    
    
class PurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        item = request.data.get("item")
        amount = request.data.get("amount")

        if not item or not amount:
            return Response({"error": "Item and amount are required."}, status=400)
        profile = request.user.profile
        history = f"Purchased {item} for {amount} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if profile.buy_history:
            profile.buy_history += f"\n{history}"
        else:
            profile.buy_history = history
        profile.save()

        return Response({"message": "Purchase recorded successfully."}, status=201)



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile  
        except Profile.DoesNotExist: 
            return Response({"error": "Profile does not exist for this user."}, status=404)
        data = {
            "username": request.user.username,
            "email": request.user.email,
            "buy_history": profile.buy_history,
            "created_at": profile.created_at,
        }
        return Response(data)