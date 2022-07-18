// Our Domain Name ٩(๑`^´๑)۶
const domainName = "https://localhost:5000/"

/* retrieve get parameter value */
function retrieveGetValue(paramName) {
    let result = null;
    let name = null;
    let value = null;
    const items = location.search.substring(1).split("&");
    for (let i = 0; i < items.length; i++) {
        [name, value] = items[i].split("=");
        if (name === paramName) result = decodeURIComponent(value);
    }
    return result;
}

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
            // Login success, redirect to prev page
            let nextPage = retrieveGetValue("from");
            if (nextPage.substring(0, domainName.length) === domainName) {
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
