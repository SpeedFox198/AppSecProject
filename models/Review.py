"""
Review
------

Customer review class representing
a review in the review section
"""
from dataclasses import dataclass
from .User import _DEFAULT_PIC_NAME, UPLOAD_FOLDER

@dataclass
class Review:
    """ Represents a customer review """
    user_id: str
    username: str
    profile_pic: str
    stars: int
    time: str
    content: str

    def __post_init__(self):
        self.profile_pic = UPLOAD_FOLDER + (self.profile_pic or _DEFAULT_PIC_NAME)

    def to_customer_dict(self):
        """ Returns customers' dictionary form of class for jsonifying """
        return {
            "username": self.username,
            "profile_pic": self.profile_pic,
            "stars": self.stars,
            "time": self.time,
            "content": self.content
        }

    def to_staff_dict(self):
        """
        Return staffs' version
        Staff requires user_id to delete a specific review and exposing the user_id to the customer can be a security risk.
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "profile_pic": self.profile_pic,
            "stars": self.stars,
            "time": self.time,
            "content": self.content
        }
