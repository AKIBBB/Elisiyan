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
    path('admin/manage-products/', views.AdminManageProducts.as_view(), name='admin_manage_products'),
    path('admin/delete-product/<int:product_id>/', views.AdminDeleteProduct.as_view(), name='admin_delete_product'),
]
