from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import activate

router = DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
    path('active/<uid64>/<token>', activate, name='active'),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('login/', views.UserLoginApiView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('admin-interface/', views.AdminInterfaceView.as_view(), name='admin_interface'),
    path('admin/manage-users/', views.AdminManageUsers.as_view(), name='admin_manage_users'),
    # path('admin/delete-user/<int:user_id>/', views.AdminDeleteUser.as_view(), name='admin_delete_user'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),

]
