//檢查註冊時，password欄位與confirm password欄位是否一致
function ConfirmPassword(Password, Confirm_password, Error_message) {
    confirm = Confirm_password.value;
    Error_message.textContent="";
    if (Password != confirm) {
        Error_message.textContent="密碼不一致";
    }
}   