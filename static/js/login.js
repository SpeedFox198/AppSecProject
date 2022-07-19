import {DOMAIN_NAME, retrieveGetValue} from "./package.js"

/* Post credentials to API */
async function post_login(username, password, csrf_token) {
    const url = "/api/login";
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

const failMessage = document.getElementById("loginFailed");
const errorMessage = document.getElementById("loginError");
const loginButton = document.getElementById("loginSubmitButton");

/* Login function */
async function login(username, password, csrf_token) {
    loginButton.classList.add("disabled");
    failMessage.classList.add("d-none");
    errorMessage.classList.add("d-none");
    try {
        const {status} = await post_login(username, password, csrf_token);
        if (status) {
            // Display login failed message
            failMessage.classList.remove("d-none");
        }
        else {
            // Login success, redirect to prev page
            let nextPage = retrieveGetValue("from");
            if (nextPage && nextPage.substring(0, DOMAIN_NAME.length) === DOMAIN_NAME) {
                location.replace(nextPage);
            }
            else {  // next page link has been modified, redirect to home
                console.error("⁽⁽(੭ꐦ •̀Д•́ )੭*⁾⁾ ᑦᵒᔿᵉ ᵒᐢᵎᵎ");
                location.replace("/");
            }
        }
    }
    catch (err) {
        // Display login failed message
        errorMessage.classList.remove("d-none");
        console.error(err);
    }
    loginButton.classList.remove("disabled");
}

const form = document.getElementById("loginForm");

function checkEntered() {
    if (form.username.value && form.password.value) {
        loginButton.classList.remove("disabled");
    }
    else {
        loginButton.classList.add("disabled");
    }
}

form.username.addEventListener("blur", checkEntered);
form.username.addEventListener("input", checkEntered);
form.password.addEventListener("blur", checkEntered);
form.password.addEventListener("input", checkEntered);

form.addEventListener("submit", event => {
    event.preventDefault();
    event.stopPropagation();
    if (form.checkValidity()) {
        login(form.username.value, form.password.value, form.csrf_token.value);
    }
});
