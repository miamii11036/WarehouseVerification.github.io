from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class UserInfo(models.Model):
    """
    建立資料庫中儲存使用者資料的table - myweb_userinfo
    以下變數是設定table的columns之資料型態
    """
    username = models.CharField(max_length=30)
    account = models.CharField(max_length=30)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=64)

class OrderList(models.Model):
    """
    建立Order清單資料庫
    """
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    month = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12)
        ]
    )
    region = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

class OrderDetail(models.Model):
    """
    建立Order內容的詳細品項清單
    """
    order_id = models.ForeignKey(OrderList, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    package = models.CharField()

