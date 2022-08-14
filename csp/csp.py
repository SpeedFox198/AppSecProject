"""
Content Security Policy
-----------------------

Stores the Content Security Policy used by the web app
"""


# Wrote it in a json-style format for easier management
_csp = {
    "default-src": [
        "\'none\'"                      # Default deny all
    ],
    "script-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net",     # For Bootstrap
        "https://code.jquery.com",      # For jQuery
        "https://apis.google.com",      # For Google API
        "https://www.google.com/recaptcha/api.js",      # For Google reCAPTCHA
        "https://www.gstatic.com/recaptcha/releases/mq0-U1BHZ5YTcoDC-CvsLPNc/recaptcha__en.js"  # For Google reCAPTCHA
    ],
    "style-src": [
        "\'self\'",
        "https://cdn.jsdelivr.net",     # For Bootstrap
        "https://use.fontawesome.com",  # For Font Awesome
        "https://code.jquery.com"       # For jQuery
    ],
    "img-src": [
        "\'self\'"
    ],
    "connect-src": [
        "\'self\'"
    ],
    "font-src": [
        "\'self\'",
        "https://use.fontawesome.com"   # For Font Awesome
    ],
    "frame-src": [
        "\'self\'",
        "https://www.google.com"
    ],
    "form-action": [
        "\'self\'",
        "https://checkout.stripe.com/"  # For Stripe checkout
    ],
    "base-uri": [
        "\'self\'"
    ]
}

# For loading profile pic
_img_src_blob_scp = _csp.copy()
_img_src_blob_scp["img-src"] = _img_src_blob_scp["img-src"] + ["blob:"]

# Formats csp into string in the proper format of a Content Security Policy
_DEFAULT_CSP = "".join(f"{key} {' '.join(value)};" for key, value in _csp.items())
_IMG_SRC_BLOB_SCP = "".join(f"{key} {' '.join(value)};" for key, value in _img_src_blob_scp.items())

def get_csp(blob=False) -> str:
    """ Returns the Content Security Policy """
    csp = _DEFAULT_CSP
    if blob:
        csp = _IMG_SRC_BLOB_SCP
    return csp
