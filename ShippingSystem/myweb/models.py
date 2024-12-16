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
    建立所有Order清單的資料庫table
    """
    order_id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    month = models.IntegerField( 
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12)
        ]
    )
    region = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="start")

    def __str__(self):
        return f"order_id:{self.order_id}, year:{self.year}, month:{self.month}, region:{self.region}, client:{self.client}, status:{self.status}"
        #一旦views.py呼叫資料庫並載入資料時不會出現 <OrderList: OrderList object (1)>這種阻礙系統讀取重要資料的資訊
        #有點像用一般for迴圈輸出二維串列中的每一個一維串列元素，若直接print二維串列中的某一個一維串列，一定會有[]

class Product(models.Model):
    """
    儲存所有Product資訊的table
    """
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=100)
    product_inventory = models.IntegerField()
    product_position = models.CharField(max_length=100)

    def __str__(self):
        return f"product_id:{self.product_id}, product_name:{self.product_name}, product_type:{self.product_type}, product_inventory:{self.product_inventory}, product_position:{self.product_position}"

class OrderDetail(models.Model):
    """
    建立某一張Order的內容品項清單 之 資料庫table
    """
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orderdetail_product_id")
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    package = models.CharField(max_length=255)
    order_id = models.ForeignKey(OrderList, on_delete=models.CASCADE, related_name="orderlist_order_id")

    def __str__(self):
        return f"product_id:{self.product_id.product_id}, product_name:{self.product_id.product_name}, product_type:{self.product_id.product_type} quantity:{self.quantity}, package:{self.package}, order_id:{self.order_id.order_id}"

class ProcessTime(models.Model):
    """
    紀錄每張order_id的的每個處理開始的時間點與持續時間，與最後該訂單完成所有處理的時間點
    """
    order_id = models.ForeignKey(OrderList, on_delete=models.CASCADE, related_name="order_process_time")
    process_A = models.DateTimeField(null=True, blank=True)
    process_B = models.DateTimeField(null=True, blank=True)
    process_C = models.DateTimeField(null=True, blank=True)
    complete = models.DateTimeField(null=True, blank=True)

    duration_A = models.FloatField(null=True, blank=True)
    duration_B = models.FloatField(null=True, blank=True)
    duration_C = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"order_id:{self.order_id.order_id}, process_A:{self.process_A}, process_B:{self.process_B}, process_C:{self.process_C}, complete:{self.complete}, duration_A:{self.duration_A}, duration_B:{self.duration_B}, duration_C:{self.duration_C}"
