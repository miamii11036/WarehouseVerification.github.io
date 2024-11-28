/*document.addEventListener("DOMContentLoaded", () => {
    const loadingElement = document.getElementById("loading");
    const userDataElement = document.getElementById("user-data");

    const usernameElement = document.getElementById("username");
    const accountElement = document.getElementById("account");
    const emailElement = document.getElementById("email");
    const passwordElement = document.getElementById("password");

    // 使用 Fetch API 從後端取得資料
    fetch("/member/data/")
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            // 顯示資料到網頁
            usernameElement.textContent = User_info.username;
            accountElement.textContent = User_info.account;
            emailElement.textContent = User_info.email;
            passwordElement.textContent = User_info.password;

            // 更新顯示狀態
            loadingElement.style.display = "none";
            userDataElement.style.display = "block";
        })
        .catch(error => {
            // 處理錯誤
            console.error("Fetch error:", error);
            loadingElement.textContent = "Failed to load user data.";
        });
});*/

/*
document.getElementById("loadMemberData").addEventListener(true , () => {
    const loadingElement = document.getElementById("loading");
    const userDataElement = document.getElementById("user-data");

    const usernameElement = document.getElementById("username");
    const accountElement = document.getElementById("account");
    const emailElement = document.getElementById("email");
    const passwordElement = document.getElementById("password");

    fetch("member/data/")
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then(data =>{
        if (data.error) {
          loadingElement.textContent = data.error;}
        else {
          userDataElement.textContent = data.username;
          accountElement.textContent = data.account;
          emailElement.textContent = data.email;
          passwordElement.textContent = data.password;

          loadingElement.style.display = "none";
          userDataElement.style.display = "block";}
      })
      .catch(error => {
        console.error("Fetch error", error);
        loadingElement.textContent = "Failed to load user data.";
      })
  });
*/