from django import forms
from myweb.models import UserInfo

class UserInfoForm(forms.ModelForm):
    """
    取得models.py中UserInfo 類別的資料，並製作成表格形式
    """
    class Meta:
        model = UserInfo
        fields = ["username", "account", "password", "email"] #此為表格的columns

class ModifyUserInfo(forms.ModelForm):
    """
    取得修改會員資料頁面的資料
    """
    oldpassword = forms.CharField(max_length=128)
    newpassword = forms.CharField(max_length=128)
    class Meta: 
        model = UserInfo 
        fields = ['username', 'account', 'email', 'oldpassword', 'newpassword']

class DeleteUser(forms.ModelForm):
    """
    刪除會員頁面的表格
    """
    class Meta: 
        model = UserInfo 
        fields = ['account', 'email', 'password']