from django import forms
from myweb.models import UserInfo

class UserInfoForm(forms.ModelForm):
    """
    取得models.py中UserInfo 類別的資料，並製作成表格形式
    """
    class Meta:
        model = UserInfo
        fields = ["username", "account", "password", "email"] #此為表格的columns