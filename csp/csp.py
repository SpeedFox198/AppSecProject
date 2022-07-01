"""
Content Security Policy
-----------------------

Stores the Content Security Policy used by the web app
"""


# Wrote it in a json-style format for easier management
csp = {
    "default-src": [
        "\'none\'"                      # Default deny all
    ],
    "script-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net",     # For bootstrap
        "https://code.jquery.com"       # For jQuery
    ],
    "style-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net",     # For bootstrap
        "https://use.fontawesome.com",  # For fontawesome
        "https://code.jquery.com"       # For jQuery
    ],
    "img-src": [
        "\'self\'"
    ],
    "font-src": [
        "\'self\'",
        "https://use.fontawesome.com"   # For fontawesome
    ],
    "form-action": [
        "\'self\'"
    ],
    "base-uri": [
        "\'self\'"
    ]
}


# Formats csp into string in the proper format of a Content Security Policy
CSP = "".join(f"{key} {' '.join(value)};" for key, value in csp.items())
