from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from myweb.form import UserInfoForm, ModifyUserInfo, DeleteUser
from myweb.models import UserInfo, OrderList, OrderDetail
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password


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
                user = form.save(commit=False)
                user.password = make_password(form.cleaned_data['password'])
                user.save()
                email = form.cleaned_data["email"] #整理表單中的email columns資料
                campare_user = UserInfo.objects.get(email=email)
                #以下這段用session儲存來自資料庫的資料，並在enrollok讀取session儲存的資料
                #session用[]中的內容作為標籤，儲存等號後方的資料，當需要使用session儲存的資料時，用.get()呼叫[]中的內容
                request.session['is_login'] = True
                request.session["username"] = campare_user.username
                return redirect("/enrollok") 
            except IntegrityError as e:
                #如果信箱與帳號已存在於資料庫中
                print(f"IntegrityError: {e}")
                messages.add_message(request, messages.ERROR, "account or email has existed")
                return redirect("/enroll")
            
            except Exception as e:
                print(f"Error during saving user: {e}")
                error_message = "註冊失敗，請稍後再試"
        return render(request, "enroll&login/enroll.html", {"error":error_message})
    else:
        form = UserInfoForm()
    return render(request, "enroll&login/enroll.html")

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
        compare_user = UserInfo.objects.filter(account=account).first()
        if not compare_user: #先比對account是否存在
            messages.error(request, "Invalid account or password")
            return redirect("/") 
        if not check_password(password, compare_user.password): #在比對密碼是否一致
            messages.error(request, "Invalid account or password")
            return redirect("/") 
        else:
            request.session["is_login"] = True
            #request.session["username"] = compare_user.username
            #request.session["account"] = compare_user.account
            request.session["email"] = compare_user.email
            return redirect("member_data")
    return render(request, "index.html")

def member_data(request):
    """
    登入成功時要檢查狀態is_login是否為True，才能進此頁面，並呈現使用者資料
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
            "email": user_info.email,
        }
        return render(request, 'enroll&login/member.html', User_Info)
    else:
        return redirect('/')
    
def modify_data(request, email):
    """
    顯示會員的資料並讓使用者修改資料後上傳資料庫更改原本的資料，成功時則跳轉至會員資料頁面
    """
    status = request.session.get("is_login")
    email = request.session.get("email")
    if status:
        user = UserInfo.objects.get(email=email)
        form = ModifyUserInfo(instance=user)
        if request.method == "POST":
            form = ModifyUserInfo(request.POST, instance=user)
            if form.is_valid():
                oldpassword = form.cleaned_data.get("oldpassword")
                newpassword = form.cleaned_data.get("newpassword")
                try:
                    if not check_password(oldpassword, user.password):
                        messages.add_message(request, messages.ERROR, "Incorrect password")
                        return redirect("modify_data", email=email)
                    else:
                        user.password = make_password(newpassword)
                        user.save()
                        request.session["is_login"] = True
                        return redirect("member_data")                      
                except Exception as e:
                    return HttpResponse(f"沒有儲存到資料庫:{str(e)}")
            else:
                return HttpResponse("沒通過驗證")
        return render(request, "enroll&login/modify.html", {"form":form, "user":user, "email":email})
    else:
        return redirect("/")
    
def delete_member(request):
    """
    刪除畫面，當使用者按下Yes，會跳出輸入帳號、密碼、信箱的警示窗，並比對使用者輸入的資料是否與資料庫一致，
    成功時返回首頁並刪除資料庫中的使用者資料
    """
    status = request.session.get("is_login")
    email = request.session.get("email")
    form = DeleteUser(request.POST)
    if status:
        if request.method == "POST":
            if form.is_valid():
                email = form.cleaned_data.get("email")
                password = form.cleaned_data.get("password")
                account = form.cleaned_data.get("account")
                try:
                    user = UserInfo.objects.get(email=email, account=account)
                    if not check_password(password, user.password):
                        messages.add_message(request, messages.WARNING, "Incorrect password")
                        return redirect("delete_member")
                    else:
                        user.delete()
                        logout(request)
                        return redirect("/")
                except UserInfo.DoesNotExist:
                    messages.add_message(request, messages.ERROR, "Incorrect account or email")
                    return redirect("delete_member")
            else:
                return HttpResponse("form驗證不成功")
        return render(request, "enroll&login/delete.html", {"email":email})
    else:
        return redirect("/")

def logout(request):
    """
    執行時返回至首頁，並消除所有的session
    """
    request.session.flush()
    return render(request, "index.html")

def search(request):
    """
    把資料庫中名為OderList的table資料丟過去網頁中
    """
    orders = OrderList.objects.all()
    return render(request, "execute/search.html", {"orders":orders})

def order_detail(request, order_id):
    """
    取得order_id後，在資料庫中名為OrderDetail的table中，尋找對應order_id的所有資料
    因為一張訂單通常會有很多筆品項，所以order變數會儲存很多不同的product_id的相關資料，然後把他們全部丟掉網頁上
    """
    order = OrderDetail.objects.filter(order_id=order_id)
    orderdetail = [
        {
            "product_id":order.product_id,
            "product_name":order.product_name,
            "quantity":float(order.quantity),
            "package":order.package
        }
        for good in order
    ]
    return JsonResponse({"orderdetail":orderdetail})