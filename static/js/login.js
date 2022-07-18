/* Post credentials to API */
async function post_login(username, password) {
    const url = "/api/login";
    const response = await fetch(url, {
        "method": "POST",
        "headers": {
            "Accept": "application.json",
            "Content-Type": "application/json"
        },
        "body": JSON.stringify({
            "username": username,
            "password": password
        })
    });
    if (response.ok) {
        return await response.json();
    }
    else {
        throw new Error("API response not ok.");
    }
}

const failMessage = document.getElementById("loginFailed");

/* Login function */
async function login(username, password) {
    failMessage.classList.add("d-none");
    try {
        const {status} = await post_login(username, password);
        if (status) {
            // Display login failed message
            failMessage.classList.remove("d-none");
        }
        else {
            // Login success, redirect to prev page (prevent DOM XSS)
            location.replace("/");
        }
    }
    catch (err) {
        // Display login failed message
        failMessage.classList.remove("d-none");
        console.error(err);
    }
}

const form = document.getElementById("loginForm");

form.addEventListener("submit", event => {
    event.preventDefault();
    event.stopPropagation();
    if (form.checkValidity()) {
        login(form.username.value, form.password.value);
    }
});
