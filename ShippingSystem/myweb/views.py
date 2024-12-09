from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from myweb.form import UserInfoForm, ModifyUserInfo, DeleteUser
from myweb.models import UserInfo, OrderList, OrderDetail



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

def orderlist(request):
    """
    把資料庫中名為OderList的table資料丟過去網頁中
    """
    status = request.session.get("is_login")
    if not status:
        return redirect("/")
    else:
        orders = OrderList.objects.all().order_by("-order_id")
        paginator = Paginator(orders, 10) #將orderlist table的資料以每10條資料為一頁整合，並儲存在名為Paginator的物件
        page_number = request.GET.get('page', 1)  #從request的get參數獲取代表當前頁碼的page參數，如果沒有頁碼參數，則默認為第 1 頁。
                                      #page的參數是從js的這裡$.get(`/orderlist/?page=${page}`)丟過來的
        try:  #從 Paginator 物件中獲取指定頁碼的資料，如果頁碼無效或超出範圍，將捕捉例外並返回空的 JSON 回應
            page_obj = paginator.get_page(page_number)  #獲取指定頁碼的資料，返回一個 Page 物件
        except EmptyPage: #當頁碼超出範圍時拋出的異常
            return JsonResponse({"orders": [], "has_next": False, "total_pages": paginator.num_pages})
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': #檢查請求是否為AJAX請求
            data = [
                {
                    "order_id":order.order_id,
                    "year":order.year,
                    "month":order.month,
                    "region":order.region,
                    "client":order.client,
                    "status":order.status
                }
                for order in page_obj
            ]
            return JsonResponse({"orders":data, "has_next":page_obj.has_next(), "total_pages": paginator.num_pages})
        return render(request, "execute/search.html", {"page_obj": page_obj})

def order_detail(request, order_id):
    """
    取得order_id後，在資料庫中名為OrderDetail的table中，尋找對應order_id的所有資料
    因為一張訂單通常會有很多筆品項，所以order變數會儲存很多不同的product_id的相關資料，然後把他們全部丟掉網頁上
    """
    try:
        products = OrderDetail.objects.filter(order_id_id=order_id)
        orderdetail = [
            {
                "product_id":product.product_id.product_id,
                "product_name":product.product_id.product_name,
                "product_type":product.product_id.product_type,
                "quantity":float(product.quantity),
                "package":product.package
            }
            for product in products
        ]
        return JsonResponse({"orderdetail":orderdetail})
    except Exception as e:
        return JsonResponse({'error': 'Internal Server Error'}, status=500)

def IDsearch(request):
    """
    依照使用者輸入的order id 對資料庫進行檢索並傳送結果到表格中
    """
    status = request.session.get("is_login")
    if status:
        try:
            if request.method == "GET":
                order_id = request.GET.get("order_id")
                order_content = OrderList.objects.filter(order_id=order_id).first()
                products = OrderDetail.objects.filter(order_id=order_id)
                if order_content:
                    if products:
                        order = {
                            "order_id":order_content.order_id,
                            "year":order_content.year,
                            "month":order_content.month,
                            "region":order_content.region,
                            "client":order_content.client,
                            "status":order_content.status
                        }
                        orderdetail = [
                            {
                                "product_id":product.product_id.product_id,
                                "product_name":product.product_id.product_name,
                                "product_type":product.product_id.product_type,
                                "quantity":float(product.quantity),
                                "package":product.package
                            }
                            for product in products
                        ]
                        return render(request, "execute/IDsearch.html", {"order":order, "orderdetail":orderdetail})
                    else:
                        messages.add_message(request, messages.ERROR, "There is nothing in this Order_id")
                        return redirect("/orderlist")
                else:
                    messages.add_message(request, messages.ERROR, "Order_id is not exist")
                    return redirect("/orderlist")
        except Exception as e:
            print("有東西怪怪的")
            pass
    else:
        return redirect("/")
    
def FilterSearch(request):
    """
    使用者輸入篩選條件時，系統從資料庫搜尋符合篩選條件的 orders 到網頁中
    """
    status = request.session.get("is_login")
    if not status:
        return redirect("/")

    if request.method == "GET":
        # 接收篩選條件
        try:
            year = request.GET.get("year")
            month = request.GET.get("month")
            region = request.GET.get("region")

            if year and year.isdigit():
                year = int(year)
            if month and month.isdigit():
                month = int(month)
            else:
                month = None
    
        except Exception as e:
            print(f"沒有成功接收到篩選資料:{e}")    

        try:
            orders = OrderList.objects.all().order_by("-order_id")
            if year:
                orders = orders.filter(year=year)
            if month:
                orders = orders.filter(month=month)
            if region:
                orders = orders.filter(region=region)
            if not orders:
                messages.add_message(request, messages.ERROR, "There is nothing in the conditions")
                return redirect("/orderlist")
        except Exception as e:
            print(f"資料庫篩選失敗:{e}")
        
            

        # 初始化 Paginator
        paginator = Paginator(orders, 10)  # 每頁顯示 10 筆資料
        page_number = request.GET.get("page", 1)
        try:
            page_obj = paginator.get_page(page_number)
        except EmptyPage:
            return JsonResponse({"orders": [], "has_next": False, "total_pages": paginator.num_pages})

        # 如果是 AJAX 請求，返回 JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            data = [
                {
                    "order_id": order.order_id,
                    "year": order.year,
                    "month": order.month,
                    "region": order.region,
                    "client": order.client,
                    "status": order.status,
                }
                for order in page_obj
            ]
            return JsonResponse(
                {"orders": data, "has_next": page_obj.has_next(), "total_pages": paginator.num_pages}
            )

        # 非 AJAX 請求，返回渲染頁面
        return render(request,"execute/filtersearch.html", {"page_obj": page_obj, "year": year, "month":month, "region": region})
