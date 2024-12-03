from django.contrib import admin
from myweb.models import UserInfo, OrderList, OrderDetail

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(OrderList)
admin.site.register(OrderDetail)