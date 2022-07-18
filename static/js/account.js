async function twoFA (enable) {
    const url = "/api/enable-2fa/" + "<get_user_id>" + `?enable=${enable}`;
    const response = await fetch(url);
    const data = await response.json();
    const success = data["success"];
    if (success) {
        confirm("Two factor authentication has been " + (enable ? "enabled" : "disabled") + ".");
    }
    else {
        confirm("Failed to " + (enable ? "enable" : "disable") + " two factor authentication.");
    }
}
