"""
URL configuration for rose_and_roots project.

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import *
from masters.views import *

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),

    # Template views
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    
    # API endpoints
    path('logout/', logout, name='logout'),
    
    # masters
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/', dashboard, name='dashboard'),
    path('bouquet/add/', add_bouquet, name='add_bouquet'),
    
    # Vendor Management
    path('vendors/', vendor_list, name='vendor_list'),
    path('vendors/add/', add_vendor, name='add_vendor'),
    path('view_vendor/', view_vendor, name='view_vendor'),  # Changed to str
    path('edit_vendor/', edit_vendor, name='edit_vendor'),  # Changed to str
    path('delete_vendor/', delete_vendor, name='delete_vendor'),

    # Add these to your urls.py

    path('occasions/', occasion_list, name='occasion_list'),
    path('occasions/add/', add_occasion, name='add_occasion'),
    path('view_occasion/', view_occasion, name='view_occasion'),
    path('edit_occasion/', edit_occasion, name='edit_occasion'),
    path('delete_occasion/', delete_occasion, name='delete_occasion'),
]
