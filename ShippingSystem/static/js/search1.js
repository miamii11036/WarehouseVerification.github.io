$(document).ready(function() { //當網頁載入完成時
    let currentPage = 1; //設定當前頁碼的變數初始值為1
    const orderlist = $("#order-list-table tbody")
    const pagination = $("#pagination");
    $(`.order-detail`).hide(); //隱藏order-detail-table

    function loadOrders(page) {
        /* 載入頁碼對應的資料庫之orderlist table資料 */
        $.get(`/orderlist/?page=${page}`) //取得views.py的orderlist函數丟過來的JsonResponse，並設定參數 - 頁碼
            .done(function(response) { //成功接收資料時執行
            const orders = response.orders; 
            const hasNext = response.has_next
            const totalPages = response.total_pages;

            orderlist.empty(); //清空order-list-table的資料
            orders.forEach(order =>{ //加入views.py丟過來的資料到order-list-table
                orderlist.append(`
                <tr class="order-list" data-order-id="${order.order_id}">
                    <td>${order.order_id}</td>
                    <td>${order.year}</td>
                    <td>${order.month}</td>
                    <td>${order.region}</td>
                    <td>${order.client}</td>
                    <td>${order.status}</td>
                    <td style="max-width: fit-content; padding-top: 8px; padding-left: 0px;">
                        <button class="expand-btn" id="submit">Expand/Hide</button>
                    </td>
                </tr>
                <tr class="order-detail" id="order-detail-${order.order_id}" style="display: none;" >
                    <td colspan="7">
                        <table class="table table-striped">
                            <thead class="table-light">
                                <th>Product ID</th>
                                <th>Product name</th>
                                <th>Product type</th>
                                <th>Quantity</th>
                                <th>Package</th>
                            </thead>
                            <tbody class="order-detail-data">
                                
                            </tbody>
                        </table>
                    </td>
                </tr>
                `);
            });
            //更新分頁按鈕
            updatePagination(page, totalPages, hasNext);

            //當點擊上方的order-list-table中的Expand/Hide按鈕時
            $(".expand-btn").on("click", function(){
                const row = $(this).closest("tr"); //找到離Expand/Hide按鈕最近的tr tag，即是class="order-list"的tr
                const orderid = row.data("order-id"); //獲取該tr的自訂屬性值 data-order-id
                const orderdetail = $(`#order-detail-${orderid}`); //將指定的order_id的order-detail-table儲存成變量

                if (orderdetail.is(":visible")) { 
                    orderdetail.hide(); //假如order-detail-table已經展開則隱藏，讓使用者可以重複展開與隱藏order-detail-table
                } else { //若order-detail-table是隱藏狀態，則檢查是否曾載入過資料庫中orderdetail table的資料
                    if (orderdetail.find(".order-detail-data").children().length === 0) { //如果沒有載入過
                        $.get(`/order_detail/${orderid}/`, function(data) { //接收views.py中order_detail函數丟過來的JsonResponse資料
                            const products = data.orderdetail;
                            const tbody = orderdetail.find(".order-detail-data");

                            tbody.empty(); //清空order-detail-table
                            products.forEach(product =>{ //載入剛丟過來的指定order_id的order-detail-table資料
                                tbody.append(`
                                    <tr>
                                        <td>${product.product_id}</td>
                                        <td>${product.product_name}</td>
                                        <td>${product.product_type}</td>
                                        <td>${product.quantity}</td>
                                        <td>${product.package}</td>
                                    </tr>
                                `);
                            });
                        });
                    }
                    orderdetail.show(); //顯示order-detail-table
                }
            });
        })
        .fail(function(error) { //如果沒有成功接收views.py的orderlist函數丟過來的JsonResponse
            console.error("Error:", error);
            alert("Failed to load data");
        });
    }

    function updatePagination(page, totalPages, hasNext) {
        /*更新分頁按鈕*/
        pagination.find(".page-item").not("#prev-page, #next-page").remove(); //先移除所有 除了前一頁與後一頁按鈕以外的分頁紐
        console.log("Current Page:", page); //輸出丟過來的參數，檢查有資料，結果會呈現在開發者工具的主控台區域
        console.log("Total Pages:", totalPages);
        console.log("Has Next:", hasNext);

        for (let i = 1; i <= totalPages; i++) { //生成新的分頁按鈕，最多只會產生與views.py的orderlist函數丟過來的totalPages的相同值的數量
            const activeClass = i === page ? "active" : ""; //選擇分頁按鈕是否活化(顏色顯亮)
            $(`<li class="page-item ${activeClass}"><a class="page-link" href="#">${i}</a></li>`)
                .insertBefore("#next-page") //插入到 #next-page 按鈕之前
                .on("click", function (e) { //當點擊事件發生時
                    e.preventDefault(); //防止頁面重新加載
                    if (i !== currentPage) { //檢查點擊後的當前頁面是否與 currentPage變數值一致 (預設為1)，若不一致則
                        currentPage = i; //將currentPage的值從1變成當前頁碼
                        loadOrders(currentPage); //呼叫loadOrders載入當前頁面的orderlist 資料
                    }
                });
        }

        if (page == 1) { //如果當前頁面等於1時
            $("#prev-page").addClass("disabled"); //則上一頁按鈕變成不可點擊的狀態
        } else { //若不等於1，則移除不可點擊的狀態(disabled)、重置(off)之前點擊的事件避免重複點擊執行載入資料函數
            $("#prev-page").removeClass("disabled").off("click").on("click", function(e){ //重新綁定(on)一個新的 點擊事件
                e.preventDefault();
                if (currentPage > 1 ) { //如果當前頁碼是第 1 頁，則不允許再往前翻頁，避免頁碼變成小於 1 的情況
                    currentPage--;//如果大於1，則點擊時的頁碼數值-1
                    loadOrders(currentPage);
                }
            });
        }

        if (!hasNext) { //如果hasNext is False (代表沒有下一頁了)
            $("#next-page").addClass("disabled"); //則下一頁按鈕變成不可點擊狀態
        } else { //否則重置並重新綁定點擊事件
            $("#next-page").removeClass("disabled").off("click").on("click", function(e) {
                e.preventDefault();
                currentPage++;
                loadOrders(currentPage);
            });
        }
    }
    
    loadOrders(1); //頁面初使載入時，預設載入第一頁
});