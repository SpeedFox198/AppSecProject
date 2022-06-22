"""
Validation classes used by Forms.py
Mainly uses regex to check if field is of correct pattern
"""
from wtforms.validators import Regexp


class ContainsLower(Regexp):
    """
    Validates if incoming data contains a lowercase character
    """

    def __init__(self, message=None):
        pattern = r".*[a-z].*"
        super().__init__(pattern, message=message)

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext("Field must contain at least one lowercase letter.")

        super().__call__(form, field, message)


class ContainsUpper(Regexp):
    """
    Validates if incoming data contains a uppercase character
    """

    def __init__(self, message=None):
        pattern = r".*[A-Z].*"
        super().__init__(pattern, message=message)

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext("Field must contain at least one uppercase letter.")

        super().__call__(form, field, message)


class ContainsNumSymbol(Regexp):
    """
    Validates if incoming data contains a number or symbol
    """

    def __init__(self, message=None):
        # numbers:      [0-9]
        # symbols: [ -/]     [:-@]     [\[-`]     [{-~]
        # letters:                [A-Z]      [a-z]
        # num&sym: [      -     @]     [\[-`]     [{-~]
        pattern = r".*[ -@\[-`{-~].*"
        super().__init__(pattern, message=message)

    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext("Field must contain at least one symbol or number.")

        super().__call__(form, field, message)

class ValidUsername(Regexp):
    """
    Validates if incoming data is a valid format for username

    Username must only contain alphanumeric characters (including underscore)
    """

    def __init__(self, message=None):
        pattern = r"^\w*$"
        super().__init__(pattern, message=message)
    
    def __call__(self, form, field):
        message = self.message
        if message is None:
            message = field.gettext("Username can only contain letters, numbers, and underscores.")

        super().__call__(form, field, message)


