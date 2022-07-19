// Our Domain Name ٩(๑`^´๑)۶
export const DOMAIN_NAME = "https://localhost:5000/"

/* retrieve get parameter value */
export function retrieveGetValue(paramName) {
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
