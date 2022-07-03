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
    username: str
    profile_pic: str
    stars: int
    time: str
    content: str

    def __post_init__(self):
        self.profile_pic = UPLOAD_FOLDER + (self.profile_pic or _DEFAULT_PIC_NAME)

    def jsonify(self):
        return {
            "username": self.username,
            "profile_pic": self.profile_pic,
            "stars": self.stars,
            "time": self.time,
            "content": self.content
        }
