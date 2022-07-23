"""
User
----

User representing both customers and admins
"""
from dataclasses import dataclass


# Profile pic path
UPLOAD_FOLDER = r"/static/img/profile-pic/"
_DEFAULT_PIC_NAME = r"default.png"


@dataclass
class User:
    """ Represents a user """
    user_id: str
    username: str
    email: str
    password: str
    _profile_pic: str
    role: str
    name: str = None
    credit_card_no: str = None
    address: str = None
    phone_no: int = None

    def __post_init__(self):
        # Set default value of profile pic if not defined
        self._profile_pic = self._profile_pic or _DEFAULT_PIC_NAME

    @property
    def profile_pic(self):
        """ Path to profile picture of user """
        return UPLOAD_FOLDER + self._profile_pic
