const loginLinks = document.getElementsByClassName("login-link");

Array.prototype.filter.call(loginLinks, loginLink => {
  loginLink.href += `?from=${encodeURIComponent(window.location.href)}`;
});
