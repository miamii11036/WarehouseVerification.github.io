from django.db.models import Avg, F
from myweb.models import ProcessTime
from datetime import timedelta

"""
計算每個process耗費的時數
"""
class ProcessDurationServer:
    PROCESS_ORDER = ["process_A", "process_B", "process_C", "complete"]

    @staticmethod
    def get_last_filled_process(order_id):
        """
        找到該order_id的訂單的最後填入處理時間戳資料的process
        """
        last_filled = None #預設最後處理名稱為None
        for process in ProcessDurationServer.PROCESS_ORDER: 
            if getattr(order_id, process) is not None:
                #查找該訂單的ProcessTime table中，該訂單的所有process(columns)中
                #如果有某個process(column)有資料的話
                last_filled=process #則該process為最後一個填入時間戳資料的process
        return last_filled
    
    @staticmethod
    def get_previous_filled_process(order_id, latest_process):
        """
        找出指定process之前的最後一個有資料的process
        """
        current_process_index = ProcessDurationServer.PROCESS_ORDER.index(latest_process)
        #找出當前處理在PROCESS_ORDER串列容器中的索引位址
        for process in reversed(ProcessDurationServer.PROCESS_ORDER[:current_process_index]):
            #ProcessDurationServer.PROCESS_ORDER[:current_process_index]提取PROCESS_ORDER中，指定索引位址前的所有元素
            if getattr(order_id, process) is not None:
                return process
        return None
    
    @staticmethod
    def get_last_duration(order_id):
        """
        計算最後兩個有資料的 process 之間的耗時，即是紀錄新的process時間戳的前一個process所耗費的時間
        """
        end_process = ProcessDurationServer.get_last_filled_process(order_id)
        #取得最新紀錄的process時間戳的process
        if not end_process:
            return None

        start_process = ProcessDurationServer.get_previous_filled_process(order_id, end_process)
        #取得end_process的前一個有時間戳資料的process
        if not start_process:
            return None
        
        start_time = getattr(order_id, start_process)
        end_time = getattr(order_id, end_process)
        #取得有最新時間戳資料的process之前一個process的開始時間戳(即是最新process的前一個process的時間戳)與結束時間戳(即是最新process的時間戳)

        if start_time and end_time:
            duration = end_time - start_time
            days = duration.total_seconds() / 86400 #轉換成天數
            roundded_day = round(days, 1) #四捨五入取整數
            return roundded_day
        return None #如果這兩個時間戳存在，否則返回none