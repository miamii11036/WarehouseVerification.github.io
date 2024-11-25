from django.shortcuts import render, redirect
from myweb.form import UserInfoForm 
from myweb.models import UserInfo

# Create your views here.
def index(request):
    return render(request, "index.html")

def enroll(request):
    """
    確認註冊資料是否存在於資料庫中
    """
    userinfo = UserInfo.objects.all() #從資料庫中取得資料
    form = UserInfoForm(request.POST) #從form.py取得表格columns與其資料
    if request.method=="POST": 
        if form.is_valid(): #驗證資料是否成功
            try:
                form.save()
                email = form.cleaned_data["email"] #整理表單中的email columns資料
                campare_user = UserInfo.objects.get(email=email)
                #以下這段用session儲存來自資料庫的資料，並在enrollok讀取session儲存的資料
                #session用[]中的內容作為標籤，儲存等號後方的資料，當需要使用session儲存的資料時，用.get()呼叫[]中的內容
                request.session['is_login'] = True
                request.session["email"] = campare_user.email 
                request.session["username"] = campare_user.username
                request.session["account"] = campare_user.account
                request.session["password"] = campare_user.password
                return redirect("/enrollok") 
            except:
                pass
                return redirect("/enroll")
    else:
        form = UserInfoForm()
    return render(request, "enroll&login/enroll.html", locals())

def enrollok(request):
    """
    註冊成功時，網頁要呈現的資料
    """
    status = request.session.get("is_login")
    if not status:
        return redirect("/enroll")
    email = request.session.get("email")
    account = request.session.get("account")
    password = request.session.get("password")
    username = request.session.get("username")
    return render(request, "enroll&login/enrollok.html", locals())
