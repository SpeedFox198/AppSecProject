"""
Sanitize Function
-----------------

Function for sanitizing user input into HTML friendly text.
For preventing XSS.
(Used american spelling for function for consistency)
"""

from html import escape


# TODO: @SpeedFox198 - NOTE: If bytes can't be written into file, decode to string
def sanitize(text) -> bytes:
    """ Sanitizes text into HTML friendly text """
    return escape(text, quote=True).encode("ascii", "xmlcharrefreplace")
