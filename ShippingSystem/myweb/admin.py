from django.contrib import admin
from myweb.models import UserInfo, OrderList, Product, OrderDetail

# Register your models here.
admin.site.register(UserInfo)
class PostProduct(admin.ModelAdmin):
    list_display = ("product_id", "product_name", "product_type", "product_inventory", "product_position")
admin.site.register(Product, PostProduct)

class PostOrderList(admin.ModelAdmin):
    list_display = ("order_id", "year", "month", "region", "client", "status")
admin.site.register(OrderList, PostOrderList)

class PostOrderDetail(admin.ModelAdmin):
    list_display = ("product_id", "quantity", "package", "order_id")
admin.site.register(OrderDetail, PostOrderDetail)
