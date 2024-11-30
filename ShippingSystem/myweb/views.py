from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from myweb.form import UserInfoForm
from myweb.models import UserInfo
from django.contrib import messages


# Create your views here.
def index(request):
    return render(request, "index.html")

def enroll(request):
    """
    確認註冊資料是否存在於資料庫中
    """
    userinfo = UserInfo.objects.all() #從資料庫中取得資料
    form = UserInfoForm(request.POST) #當html把資料送過來後，用form.py的格式來整理丟過來的資料並做成form.py表格
    if request.method=="POST": 
        if form.is_valid(): #驗證資料是否成功
            try:
                form.save()
                email = form.cleaned_data["email"] #整理表單中的email columns資料
                campare_user = UserInfo.objects.get(email=email)
                #以下這段用session儲存來自資料庫的資料，並在enrollok讀取session儲存的資料
                #session用[]中的內容作為標籤，儲存等號後方的資料，當需要使用session儲存的資料時，用.get()呼叫[]中的內容
                request.session['is_login'] = True
                request.session["username"] = campare_user.username
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
    username = request.session.get("username")
    return render(request, "enroll&login/enrollok.html", locals())

def user_login(request):
    """
    比對登入畫面送過來的資料是否存在於資料庫中
    """
    if request.method=="POST":
        account = request.POST.get("account")
        password = request.POST.get("password")
        compare_user = UserInfo.objects.filter(account=account, password=password).first()
        if not compare_user:
            messages.error(request, "Invalid account or password")
            return redirect("/") 
        else:
            request.session["is_login"] = True
            #request.session["username"] = compare_user.username
            #request.session["password"] = compare_user.password
            #request.session["account"] = compare_user.account
            request.session["email"] = compare_user.email
            return redirect("member_data")
    return render(request, "index.html")

def member_data(request):
    """
    登入成功時要檢查狀態is_login是否為True，才能進此頁面
    """
    status=request.session.get('is_login')
    if not status:
        return redirect('/')
    email = request.session.get("email")
    user_info = UserInfo.objects.filter(email=email).first()
    if user_info:
        User_Info = {
            "username": user_info.username,
            "account": user_info.account,
            "password": user_info.password,
            "email": user_info.email,
        }
        return render(request, 'enroll&login/member.html', User_Info)
    
def modify_data(request, email):
    """
    顯示會員的資料並讓使用者修改資料後上傳資料庫更改原本的資料
    """
    status = request.session.get("is_login")
    if status:
        user = UserInfo.objects.get(email=email)
        form = UserInfoForm(instance=user)
        if request.method == "POST":
            form = UserInfoForm(request.POST, instance=user)
            if form.is_valid():
                try:
                    form.save()
                    request.session["is_login"] = True
                    return redirect("member_data")
                except:
                    return HttpResponse("沒有儲存到資料庫")
            else:
                return HttpResponse("沒通過驗證")
        return render(request, "enroll&login/modify.html", locals())