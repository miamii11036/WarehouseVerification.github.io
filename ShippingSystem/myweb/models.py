from django.db import models

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