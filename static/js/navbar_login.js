import {DOMAIN_NAME, LOGOUT_ALLOWED_ROUTES} from "./package.js"

const loginLinks = document.getElementsByClassName("login-link");

Array.prototype.filter.call(loginLinks, loginLink => {
    loginLink.href += `?from=${encodeURIComponent(window.location.href)}`;
});

async function post_logout(csrf_token) {
  const url = "/api/user/logout";
  const response = await fetch(url, {
      "method": "POST",
      "headers": {
          "Accept": "application.json",
          "Content-Type": "application/json",
          "X-CSRF-TOKEN": csrf_token
      },
      "body": ""
  });
  if (response.ok) {
      return await response.json();
  }
  else {
      throw new Error("API response not ok.");
  }
}

const logoutButton = document.getElementById("logoutButton");
if (logoutButton) {
    const csrf_token = document.getElementById("csrf_token").textContent;
    logoutButton.addEventListener("click", async e => {
        try {
            const {status} = await post_logout(csrf_token);
            if (status) {
                // Logout unsuccessful
                throw new Error("Unexpected error.");
            }
            else {
                // Login success, redirect to current page
                if (location.href.substring(0, DOMAIN_NAME.length) === DOMAIN_NAME &&
                    location.pathname.substring(0, LOGOUT_ALLOWED_ROUTES.length) === LOGOUT_ALLOWED_ROUTES) {
                    location.replace(location.href);
                }
                else {
                    location.href = "/";
                }
            }
        }
        catch (err) {
            console.error(err);
        }
    });
}
