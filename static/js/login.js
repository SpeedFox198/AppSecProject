/* Post credentials to API */
async function post_login(username, password) {
    const url = "/api/login";
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Accept": "application.json",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
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
async function login(username, password) {
    try {
        const {status} = await post_login(username, password);
        if (status) {
            // Display login failed message
            console.log("failure");
        }
        else {
            // Login success, redirect to prev page (prevent DOM XSS)
            console.log("success");
        }
    }
    catch (err) {
        // Display login failed message
        console.log("failure");
        console.error(err);
    }
}
