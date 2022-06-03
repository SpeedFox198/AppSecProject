from argon2 import PasswordHasher
from .User import User

# Profile pic path
_UPLOAD_FOLDER = r"/static/img/profile-pic/"
_DEFAULT_PIC_NAME = r"default.png"

# Password hasher for hashing
_ph = PasswordHasher()


class Customer(User):
    """
    Customer account for signed up users

    Attributes:
        __user_id (str): unique ID identifier of customer
        __username (str): username of customer
        __email (str): email of customer
        __password (str): hashed password of customer
        __name (str): name of customers
        __verified (bool): True when customer's email is verified
        __profile_pic (str): path to profile pic of customer
        __gender (str): gender of customer - "M" for male, "F" for female, "O" for other
        __coupons (list): list of the coupons owned by customer
        __orders (list): list of the orders made by customer
        __enquiry (list): list of enquiry made by the customer
    """

    def __init__(self, username, email, password):
        super().__init__()
        self.username = username
        self.email = email
        self.set_password(password)
        self.name = ""
        self.verified = False
        self.profile_pic = _UPLOAD_FOLDER + _DEFAULT_PIC_NAME
        self.gender = ""
        self.coupons = []
        self.orders = []
        self.enquiry = []

    def __repr__(self):
        return super().__repr__(username=self.username, email=self.email)


    # Mutator and accessor methods
    def set_username(self, username):
        self.username = username
    def get_username(self):
        return self.username

    def set_name(self, name):
        self.name = name
    def get_name(self):
        return self.name
    
    def get_display_name(self):
        """ Returns name for displaying, displays username if name not provided """
        return self.name or self.username

    def set_email(self, email):
        self.email = email
    def get_email(self):
        return self.email

    def set_profile_pic(self):
        self.profile_pic = f"{_UPLOAD_FOLDER}{self.get_user_id()}.png"
    def get_profile_pic(self):
        return self.profile_pic

    def set_gender(self, gender):
        self.gender = gender
    def get_gender(self):
        return self.gender

    ################################################################### TODO: REMOVing coupon func
    def set_coupons(self, coupons):
        self.coupons = coupons
    def get_coupons(self):
        return self.coupons

    def set_orders(self, orders):
        self.orders = orders
    def get_orders(self):
        return self.orders

    ###################################################################### TODO: IDK
    # Verify account and return verify
    def verify(self):
        self.verified = True
    def unverify(self):
        self.verified = False
    def is_verified(self):
        return self.verified

    # Set password, and check password
    def set_password(self, password):
        self.__password = _ph.hash(password)
    def verify_password(self, password):
        try:     # Try verifying
            _ph.verify(self.__password, password)
        except:  # If verifying fails
            return False

        # Check if needs rehashing
        if _ph.check_needs_rehash(self.__password):
            self.set_password(password)

        return True

    # Eden integration
    def add_coupons(self,coupon_code):
        self.coupons.append(coupon_code)

    def add_enquiry(self,enquiry):
        self.enquiry.append(enquiry)
    
    def get_enquiry(self):
        return self.enquiry
    
    def set_enquiry(self,enquiry):
        self.enquiry = enquiry
