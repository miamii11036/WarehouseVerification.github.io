 //*檢查密碼一致性*//
 const Form = document.getElementById("registrationForm");
 const Password = document.getElementById("password");
 const Confirm_password = document.getElementById("confirm_password");
 const Error_message = document.getElementById("error-message");

 Form.addEventListener("submit", function(){
     ConfirmPassword(Password, Confirm_password, Error_message, event);
 });

//*顯示密碼*//
const ShowPasswordCheckBox = document.getElementById("showpassword");

ShowPasswordCheckBox.addEventListener("change", function(){
 displaypassword(ShowPasswordCheckBox, Password, Confirm_password);
});