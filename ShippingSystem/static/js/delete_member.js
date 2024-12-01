document.getElementById("delete_member_button").addEventListener("click", function () {
    const modal = new bootstrap.Modal(document.getElementById("deleteModal"));
    modal.show();
});

/*document.getElementById("confirm-delete-btn").addEventListener("click", function {
    const account = document.getElementById("account").value;
    const password = document.getElementById("password").value;

    if (!account || !password) {
        document.getElementById("error-message").innerText = "Please enter both account and password.";
        document.getElementById("error-message").style.display = "block";
        return;
    }

    fetch("{% url 'delete_member' %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": "{{ csrf_token }}",
        },
        body: JSON.stringify({
            account: account,
            password: password,
            email: email
          }),
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.success) {
            AudioListener("Account deleted successfully!");
            window.location.href = "{% url '/' %}";
        }
        else {
            document.getElementById("error-message").innerHTML = data.error;
            document.getElementById("error-message").style.display = "block";
        }
    })
    .catch((error) => console.error("Error", error));
});*/