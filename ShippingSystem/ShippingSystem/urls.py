"""
URL configuration for ShippingSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from myweb.views import index, enroll, enrollok, user_login, member_data, modify_data, delete_member, logout, \
    orderlist, order_detail, IDsearch, FilterSearch

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", index),
    path("enroll/", enroll),
    path("enrollok/", enrollok),
    path("login/", user_login, name="login"),
    path("member/data/", member_data, name="member_data"),
    path("member/modify/<str:email>/", modify_data, name="modify_data"),
    path("member/delete", delete_member, name="delete_member"),
    path("logout/", logout),
    path("orderlist/", orderlist, name="orderlist"),
    path("order_detail/<int:order_id>/", order_detail, name="order_detail"),
    path("IDsearch/", IDsearch, name = "IDsearch"),
    path("Filtersearch/", FilterSearch, name="Filtersearch")
]
