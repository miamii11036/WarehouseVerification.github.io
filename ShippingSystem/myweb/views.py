from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime
from myweb.form import UserInfoForm, ModifyUserInfo, DeleteUser
from myweb.models import UserInfo, OrderList, OrderDetail, ProcessTime, Product
from myweb.services import ProcessDurationServer



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

def start_process(request):
    """
    當使用者輸入Order ID與選擇Process種類並送出後，系統會紀錄送出時間戳到ProcessTime table儲存，
    並跳轉到對應Process處理頁面。
    當條件滿足時，services.py會計算該處理的耗費天數送到ProcessTime table儲存。
    """
    status = request.session.get("is_login")
    if not status: 
        #如果沒登入，則返回登入畫面
        return redirect("/")
    else:
        if request.method == "GET":
            order_id = request.GET.get("order_id") #接收前端的資料
            process_type = request.GET.get("ProcessType")
            if not order_id or not process_type:
                messages.add_message(request, messages.DEBUG, "沒有送輸入的表單資料過來")
                return render(request, "implement/start.html")
            else:
                try:
                    order_id_databasse = OrderList.objects.get(order_id=order_id) #用order_id搜尋訂單資訊
                except OrderList.DoesNotExist:#如果order_id不存在的話
                    messages.add_message(request, messages.WARNING, "The Order ID is not existence")
                    return redirect("/start_process")
                order_id_detail = OrderDetail.objects.filter(order_id=order_id_databasse) #用order_id搜尋訂單內容
                if not order_id_detail: #如果訂單沒有內容的話
                    messages.add_message(request, messages.WARNING, "The Order is empty")
                    return render(request, "implement/start.html", {"order_id":order_id})
                else:       
                    process_time, created = ProcessTime.objects.get_or_create(order_id=order_id_databasse) 
                    #用order_id搜尋ProcessTime table。created用來紀錄get_or_create函數的操作結果
                    #如果有資料則created=False表示order_id已存在於資料庫並取得此資料
                    #如果沒資料則created=True表示資料庫沒有此order_id，則在資料庫中創建此id資料
                    current_time = timezone.now() #紀錄當下時間戳
                    if process_type == 'A':
                        process_time.process_A = current_time #則在ProcessTime資料庫的process_A column紀錄當下時間戳
                    elif process_type == 'B':
                        process_time.process_B = current_time
                    elif process_type == 'C':
                        process_time.process_C = current_time
                    elif process_type == 'Complete':
                        process_time.complete = current_time
                    order_id_databasse.status = process_type #更改該order的狀態
                    process_time.save() #將變更儲存
                    order_id_databasse.save()

                    duration = ProcessDurationServer.get_last_duration(process_time) #呼叫services.py的get_last_duration函數，取得process的耗時天數
                    if duration is not None: 
                        if process_type == 'B':
                            process_time.duration_A = duration #當process_type為B時代表process_A已結束，則函數計算出來的天數為process_A的耗時天數
                        elif process_type == 'C': #當process_type為C時代表兩種可能，一個是A->C 或 B->C
                            if process_time.process_B is None: #當process_B column沒有時間戳資料，代表跳過流程B，直接從流程A進入流程C
                                process_time.duration_A = duration
                            else:
                                process_time.duration_B = duration
                        elif process_type == "Complete":
                            if (process_time.process_B is None) and (process_time.process_C is None): #A->Complete
                                process_time.duration_A = duration
                            elif (process_time.process_C is None): #A->B->complete
                                process_time.duration_B = duration 
                            elif process_time.duration_C is not None:
                                process_time.duration_C = duration
                    process_time.save()

                    orderdetail = [ #取得該order_id的訂單內容資料
                        {
                            "product_id": product.product_id.product_id,
                            "product_name": product.product_id.product_name,
                            "product_type": product.product_id.product_type,
                            "product_inventory": product.product_id.product_inventory,
                            "product_position": product.product_id.product_position,
                            "quantity": float(product.quantity),
                            "package": product.package
                        }
                        for product in order_id_detail
                    ]
                    if process_type == 'A': #如果使用者選擇流程A則進入流程A的處理畫面
                        return render(request, "implement/process_A.html",
                                    {"order_id": order_id, "orderdetail": orderdetail})
                    if process_type == 'B':
                        return render(request, "implement/process_B.html",
                                    {"order_id": order_id, "orderdetail": orderdetail})
                    if process_type == 'C':
                        return render(request, "implement/process_C.html",
                                    {"order_id": order_id, "orderdetail": orderdetail})
        else:
            print("RRRRRR") #RRRRRR
        return render(request, "implement/start.html")
    
def process_A(request, order_id):
    """
    初庫前檢核，提供使用者該訂單的所有品項清單、該product id的出貨內容、庫存、位置、其他訂單的出貨內容
    """
    status = request.session.get("is_login")
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Please sign in first.'}, status=401)
    if request.method != "GET":
        return JsonResponse({'status': 'error', 'message': '不支援的請求方法'}, status=405)
    
    product_id = request.GET.get("product_id")
    if not product_id:
        return JsonResponse({'status': 'error', 'message': '未提供 Product ID'}, status=400)
    try:
        product_data_in_orderid = OrderDetail.objects.filter(order_id=order_id, product_id=product_id)
        if not product_data_in_orderid.exists():
            return JsonResponse({'status': 'error', 'message': '找不到對應的產品資料'}, status=404)
        product = list(product_data_in_orderid.values(
            'product_id__product_id',
            'product_id__product_name',
            'product_id__product_type',
            'quantity',
            'package'
        ))

        product_detail = Product.objects.filter(product_id=product_id)
        productdetail = list(product_detail.values(
            'product_inventory',
            'product_position'
        ))

        product_other_order = OrderDetail.objects.filter(product_id=product_id) #皆複數
        product_other_content = list(product_other_order.values(
            'order_id__order_id',
            'order_id__status', 
            'quantity'
        ))

        return JsonResponse({
            'status': 'success',
            'data': product,
            'product_detail': productdetail,
            'product_other_order' : product_other_content
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def process_B(request, order_id):
    """
    跟A一樣
    """
    status = request.session.get("is_login")
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Please sign in first.'}, status=401)
    if request.method != "GET":
        return JsonResponse({'status': 'error', 'message': '不支援的請求方法'}, status=405)
    
    product_id = request.GET.get("product_id")
    if not product_id:
        return JsonResponse({'status': 'error', 'message': '未提供 Product ID'}, status=400)
    try:
        product_data_in_orderid = OrderDetail.objects.filter(order_id=order_id, product_id=product_id)
        if not product_data_in_orderid.exists():
            return JsonResponse({'status': 'error', 'message': '找不到對應的產品資料'}, status=404)
        product = list(product_data_in_orderid.values(
            'product_id__product_id',
            'product_id__product_name',
            'product_id__product_type',
            'quantity',
            'package'
        ))

        product_detail = Product.objects.filter(product_id=product_id)
        productdetail = list(product_detail.values(
            'product_inventory',
            'product_position'
        ))

        product_other_order = OrderDetail.objects.filter(product_id=product_id) #皆複數
        product_other_content = list(product_other_order.values(
            'order_id__order_id',
            'order_id__status', 
            'quantity'
        ))

        return JsonResponse({
            'status': 'success',
            'data': product,
            'product_detail': productdetail,
            'product_other_order' : product_other_content
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def process_C(request, order_id):
    """
    跟A一樣
    """
    status = request.session.get("is_login")
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Please sign in first.'}, status=401)
    if request.method != "GET":
        return JsonResponse({'status': 'error', 'message': '不支援的請求方法'}, status=405)
    
    product_id = request.GET.get("product_id")
    if not product_id:
        return JsonResponse({'status': 'error', 'message': '未提供 Product ID'}, status=400)
    try:
        product_data_in_orderid = OrderDetail.objects.filter(order_id=order_id, product_id=product_id)
        if not product_data_in_orderid.exists():
            return JsonResponse({'status': 'error', 'message': '找不到對應的產品資料'}, status=404)
        product = list(product_data_in_orderid.values(
            'product_id__product_id',
            'product_id__product_name',
            'product_id__product_type',
            'quantity',
            'package'
        ))

        product_detail = Product.objects.filter(product_id=product_id)
        productdetail = list(product_detail.values(
            'product_inventory',
            'product_position'
        ))

        product_other_order = OrderDetail.objects.filter(product_id=product_id) #皆複數
        product_other_content = list(product_other_order.values(
            'order_id__order_id',
            'order_id__status', 
            'quantity'
        ))

        return JsonResponse({
            'status': 'success',
            'data': product,
            'product_detail': productdetail,
            'product_other_order' : product_other_content
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def status(request):
    """
    顯示所有經過Process處理的訂單列表，同時顯示每個process預估耗時天數
    """
    status = request.session.get("is_login")
    if not status:
        return redirect("/")
    else:
        existing_order_ids = ProcessTime.objects.values_list('order_id', flat=True)
        orderIDs = OrderList.objects.filter(order_id__in=existing_order_ids).order_by("-order_id")
        paginators = Paginator(orderIDs, 10)
        pag_number = request.GET.get("page", 1)
        try:
            page_obj = paginators.get_page(pag_number)
        except EmptyPage: #當頁碼超出範圍時拋出的異常
            return JsonResponse({"orders": [], "has_next": False, "total_pages": paginators.num_pages})

        if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
            orderID = [
                {
                    "order_id" : order.order_id,
                    "year" : order.year,
                    "month" : order.month,
                    "region" : order.region,
                    "client" : order.client,
                    "status" : order.status
                }
                for order in page_obj
            ]
            return JsonResponse({"orders":orderID, "has_next":page_obj.has_next(), "total_pages": paginators.num_pages})
        duration_A = ProcessTime.objects.values_list("duration_A", flat=True)
        duration_B = ProcessTime.objects.values_list("duration_B", flat=True)
        duration_C = ProcessTime.objects.values_list("duration_C", flat=True)

        print("duration:", type(duration_A))
        filter_A = [x for x in duration_A if x not in (0, None)]
        filter_B = [x for x in duration_B if x not in (0, None)]
        filter_C = [x for x in duration_C if x not in (0, None)]
        print("filter:", type(filter_A))
        print("sum:",type(sum(filter_A)))
        print("len:",type(len(filter_A)))
        averge_A = round(sum(filter_A) / len(filter_A) if filter_A else 0, 2)
        averge_B = round(sum(filter_B) / len(filter_B) if filter_B else 0, 2)
        averge_C = round(sum(filter_C) / len(filter_C) if filter_C else 0, 2)
        return render(request, "execute/status.html", {
            "page_obj" : page_obj,
            "average_A" : averge_A,
            "average_B" : averge_B,
            "average_C" : averge_C
            })

def status_detail(request, order_id):
    """
    點擊訂單的expand/hide按鈕後會顯示該訂單的處理歷史與耗時天數
    """
    try:
        process_data = ProcessTime.objects.filter(order_id = order_id)
        process_detail = [
            {
                "process_A" : "Processing/Not Process" if data.duration_A is None else data.duration_A,
                "process_B" : "Processing/Not Process" if data.duration_B is None else data.duration_B,
                "process_C" : "Processing/Not Process" if data.duration_C is None else data.duration_C,
                "complete":  "Not Complete" if data.complete is None else timezone.localtime(data.complete).strftime("%Y-%m-%d %H:%M"),
                "A_time" : timezone.localtime(data.process_A).strftime("%Y-%m-%d %H:%M"),
                "B_time" : "Not start/deal" if data.process_B is None else timezone.localtime(data.process_B).strftime("%Y-%m-%d %H:%M"),
                "C_time" : "Not start/deal" if data.process_C is None else timezone.localtime(data.process_C).strftime("%Y-%m-%d %H:%M")
            }
            for data in process_data
        ]
        return JsonResponse({"process_detail" : process_detail})
    except ProcessTime.DoesNotExist:
        return JsonResponse({"error": "No process data found"}, status=404)
    except ValueError as e:
        return JsonResponse({"error": f"Date format error: {e}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)