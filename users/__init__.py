from dataclasses import dataclass

# Profile pic path
_UPLOAD_FOLDER = r"/static/img/profile-pic/"
_DEFAULT_PIC_NAME = r"default.png"

@dataclass
class User:
    user_id: str
    username: str
    email: str
    password: str
    _profile_pic: str
    is_admin: int
    name: str = None
    credit_card_no: str = None
    address: str = None
    phone_no: int = None

    def __post_init__(self):
        self._profile_pic = self._profile_pic or _DEFAULT_PIC_NAME

    @property
    def profile_pic(self):
        return _UPLOAD_FOLDER + self._profile_pic
