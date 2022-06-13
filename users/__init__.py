"e59c9e15-e875-4393-8f19-55682e2c2041"

from typing import NamedTuple

class User(NamedTuple):
    user_id: str
    username: str
    email: str
    password: str
    profile_pic: str
    is_admin: int
    login_attempts: int


# Profile pic path
_UPLOAD_FOLDER = r"/static/img/profile-pic/"
_DEFAULT_PIC_NAME = r"default.png"

# class User:

#     def __init__(self, user_id, username, email, password, profile_pic, is_admin):
#         self.user_id = user_id
#         self.username = username
#         self.email = email
#         self.password = password
#         self.profile_pic = profile_pic
#         self.is_admin = is_admin

#     def set_profile_pic(self):
#         self.profile_pic = f"{_UPLOAD_FOLDER}{self.get_user_id()}.png"

#     def get_profile_pic(self):
#         return _UPLOAD_FOLDER + (self.profile_pic or _DEFAULT_PIC_NAME)
