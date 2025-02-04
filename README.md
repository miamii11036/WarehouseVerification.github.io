<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>首頁</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    <style>
        /*#01070A  #46656F  #8FABB7 #D8DFE5 #FBFBFB*/
        body {
            margin: 0;
            height: 100vh; /* 確保高度覆蓋整個視窗 */
            display: flex;
            flex-direction: column;
            justify-content: center; /* 水平置中 */
            align-items: center; /* 垂直置中 */
            background-color: #8FABB7; /* 可選，設置背景色 */
        }

        fieldset{
            padding: 30px;
            border: 1px solid #ccc;
            border-radius: 8px;
            background-color: #FBFBFB;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 增加陰影 */
            text-align: center; /* 將表單內容置中 */
            display: flex;
            flex-direction: column;
        }

        .submit{
            margin-top: 10px; /* 按鈕與輸入框的間距 */
            padding: 10px 20px;
            background-color: #46656F; /* 按鈕背景色 */
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 20px;
        }
        .title{
            font-size: 70px;
            margin-bottom: 150px;
            color: #01070A;
        }
        a{
            margin-top: 10px;
            margin-bottom: 255px
        }
        
    </style>
{% load static %} 
</head>
<body>
        <div class="title">Welcome to Shipping System</div>
        <fieldset>
            <form action="{% url 'login' %}" method="post">
                {% csrf_token %}
                <!-- 帳號輸入 -->
                <div class="input-group mb-3">
                    <span class="input-group-text"><img src="{% static 'image/3.png' %}" style="height: 35px; width: 35px;"></span>
                    <input type="text" class="form-control" placeholder="Account" aria-label="Account" name="account">
                </div>
                <!-- 密碼輸入 -->
                <div class="input-group mb-3" style="margin-bottom: 0px !important;">
                    <span class="input-group-text"><img src="{% static 'image/2.png' %}" style="height: 35px; width: 35px;" ></span>
                    <input type="password" class="form-control" placeholder="Password" aria-label="Password" name="password">
                </div>
                <!--帳號與密碼輸入錯誤時顯示-->
                {% if messages %}
                    {% for message in messages %}
                        <div style="font-size: 16px; color: red;">{{message}}</div> 
                    {% endfor %}
                {% endif %}
                <!-- 登入按鈕 -->
                <input class="submit" type="submit" value="sign in">
            </form>
        </fieldset>
    <a class="link-offset-2 link-offset-3-hover link-underline link-underline-opacity-0 link-underline-opacity-75-hover" href="/enroll">register</a>
</body>
</html>
