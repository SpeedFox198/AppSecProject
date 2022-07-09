LOGIN_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["username", "password"]
}

CREATE_USER_SCHEMA = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "email": {
            "type": "string",
            "format": "email",
            "maxLength": 320
        },
        "password": {
            "type": "string",
            "minLength": 8,
            "maxLength": 80,
            "pattern": "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])$"
            # At least one upper, lower, digit and symbol
        }
    },
    "required": ["username", "email", "password"]
}
