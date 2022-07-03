"""
Review
------

Customer review class representing
a review in the review section
"""
from dataclasses import dataclass
from .User import UPLOAD_FOLDER

@dataclass
class Review:
    """ Represents a customer review """
    username: str
    profile_pic: str
    stars: int
    time: str
    content: str

    def __post_init__(self):
        self.profile_pic = UPLOAD_FOLDER + self.profile_pic
