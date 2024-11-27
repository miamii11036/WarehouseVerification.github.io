//檢查註冊時，password欄位與confirm password欄位是否一致
function ConfirmPassword(Password, Confirm_password, Error_message, event) {
    Word = Password.value;
    Cword = Confirm_password.value;
    Error_message.textContent="";
    if (Word != Cword) {
        event.preventDefault();
        Error_message.textContent="密碼不一致";
    }
}   
//*顯示密碼*//
function displaypassword(ShowPasswordCheckBox, Password, Confirm_password) {
    const type = ShowPasswordCheckBox.checked ? 'text' : 'password';
    /*checked是個布林屬性，用於表示 checkbox 是否被勾選，有選則返回true，沒選則False*/ 
    /*?:是一個條件運算子，其運用方式為   <條件 如checked> ? 如果條件為true的值 : 如果條件為false的值 */
    Password.type = type;
    Confirm_password.type = type;
}

