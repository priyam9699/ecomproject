from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_view, name='search'),  # Root URL
    path('homepage/', views.homepage_view, name='homepage'),  # Set the root path to call the add_user view
    path('search/', views.search_view, name='search'),
    path('products/', views.products_view, name='products'),
    path('addproduct/', views.addproduct_view, name='addproducts'),
    path('edit/<int:id>/', views.editproduct_view, name='editproduct'),
    path('deleteproduct/<int:id>/', views.deleteproduct_view, name='deleteproduct'),
    path('add_user/', views.add_user, name='add_user'),  # Add path for /add_user/

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
