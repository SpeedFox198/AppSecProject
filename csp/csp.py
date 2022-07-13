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
        "https://cdn.jsdelivr.net",     # For Bootstrap
        "https://code.jquery.com",      # For jQuery
        "https://apis.google.com"       # For Google API
    ],
    "style-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net",     # For Bootstrap
        "https://use.fontawesome.com",  # For Font Awesome
        "https://code.jquery.com"       # For jQuery
    ],
    "img-src": [
        "\'self\'",
        "data:"                         # For loading images from data scheme
    ],
    "connect-src": [
        "\'self\'"
    ],
    "font-src": [
        "\'self\'",
        "https://use.fontawesome.com"   # For Font Awesome
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
