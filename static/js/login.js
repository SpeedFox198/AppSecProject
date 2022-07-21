import {DOMAIN_NAME, retrieveGetValue} from "./package.js"

const failMessage = document.getElementById("loginFailed");
const errorMessage = document.getElementById("loginError");
const loginButton = document.getElementById("loginSubmitButton");
const form = document.getElementById("loginForm");

/* Post credentials to API */
async function post_login(username, password, csrf_token) {
    const url = "/api/user/login";
    const response = await fetch(url, {
        "method": "POST",
        "headers": {
            "Accept": "application.json",
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": csrf_token
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

/* Login function */
async function login(username, password, csrf_token) {
    loginButton.classList.add("disabled");
    failMessage.classList.add("d-none");
    errorMessage.classList.add("d-none");
    try {
        const {status, enable_2FA} = await post_login(username, password, csrf_token);
        form.password.value = "";  // Clear password field
        form.classList.remove("was-validated");
        if (status) {
            // Display login failed message
            failMessage.classList.remove("d-none");
        }
        else { // Login success
            let nextPage = retrieveGetValue("from");
            if (!enable_2FA) {  // 2FA is not enabled
                // Redirect to prev page
                if (nextPage && nextPage.substring(0, DOMAIN_NAME.length) === DOMAIN_NAME) {
                    location.replace(nextPage);
                }
                else {  // Next page link has been modified, redirect to home
                    console.error("⁽⁽(੭ꐦ •̀Д•́ )੭*⁾⁾ ᑦᵒᔿᵉ ᵒᐢᵎᵎ");
                    location.replace("/");
                }
            }
            else {  // 2FA is enabled
                location.replace(`/user/login/twoFA?from=${encodeURIComponent(nextPage)}`);
            }
        }
    }
    catch (err) {
        // Display login failed message
        form.password.value = "";  // Clear password field
        form.classList.remove("was-validated");
        errorMessage.classList.remove("d-none");
        console.error(err);
    }
}

// Disable button if fields not filled
function checkEntered() {
    if (form.username.value && form.password.value) {
        loginButton.classList.remove("disabled");
    }
    else {
        loginButton.classList.add("disabled");
    }
}

form.username.addEventListener("input", checkEntered);
form.password.addEventListener("input", checkEntered);

// Submit login form
form.addEventListener("submit", event => {
    event.preventDefault();
    event.stopPropagation();
    if (form.checkValidity()) {
        login(form.username.value, form.password.value, form.csrf_token.value);
    }
});
