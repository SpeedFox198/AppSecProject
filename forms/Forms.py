"""
Form classes used by BrasBasahBooks web app
"""

# Import WTForms
from wtforms import Form, validators, StringField, RadioField, \
    TextAreaField, EmailField, PasswordField, FileField, \
    SelectField, IntegerField, DecimalField, ValidationError

# Import custom validations (for password field)
from .Validations import ContainsLower, ContainsUpper, ContainsNumSymbol, ValidUsername

# Import validation for file upload
from flask_wtf.file import FileAllowed

from flask_wtf import RecaptchaField

class SignUpForm(Form):
    """ Sign up form used when signing up """

    # Username
    username = StringField("Username", [validators.InputRequired(message=""),
                                        validators.Length(min=3, max=20, message=""),
                                        ValidUsername(message="Username can only contain letters, numbers, and underscores")])

    # Email
    email = EmailField("Email", [validators.InputRequired(message=""),
                                 validators.Email(message=""),
                                 validators.Length(max=320, message="")])

    # Password
    password = PasswordField("Password", [validators.InputRequired(message=""),
                                          validators.Length(min=8, max=80, message=""),
                                          ContainsLower(message="Password must contain at least one lowercase letter"),
                                          ContainsUpper(message="Password must contain at least one uppercase letter"),
                                          ContainsNumSymbol(message="Password must contain at least one symbol or number")])

    # Confirm password
    confirm = PasswordField("Confirm Password", [validators.InputRequired(message=""),
                                                 validators.Length(min=8, max=80, message=""),
                                                 validators.EqualTo("password", message="Password entered is different")])

    recaptcha = RecaptchaField()

class OTPForm(Form):
    """ OTP form used when signing up """

    # OTP
    otp = StringField("Enter your OTP", [validators.InputRequired(message=""),
                              validators.Length(min=6, max=6, message="")])


class TwoFAForm(Form):
    twoFAOTP = StringField("Enter 2FA OTP:", [validators.Length(min=6, max=6), validators.DataRequired()])
    

class LoginForm(Form):
    """ Login form used for logging in """

    # Username / Email
    username = StringField("Username / Email", [validators.InputRequired(message="")])

    # Password
    password = PasswordField("Password", [validators.InputRequired(message="")])

    recaptcha = RecaptchaField()
class BackUpCodeForm(Form):
    """ Form used for entering backup code """

    # Backup code
    code1 = StringField("Enter your backup code", [validators.InputRequired(message=""),
                                                validators.Length(min=6, max=6, message="")])
    code2 = StringField("Enter your backup code", [validators.InputRequired(message=""),
                                                validators.Length(min=6, max=6, message="")])
    code3 = StringField("Enter your backup code", [validators.InputRequired(message=""),
                                                validators.Length(min=6, max=6, message="")])
    code4 = StringField("Enter your backup code", [validators.InputRequired(message=""),
                                                validators.Length(min=6, max=6, message="")])
    code5 = StringField("Enter your backup code", [validators.InputRequired(message=""),
                                                validators.Length(min=6, max=6, message="")])
    code6 = StringField("Enter your backup code", [validators.InputRequired(message=""),
                                                validators.Length(min=6, max=6, message="")])


class ChangePasswordForm(Form):
    """ Changing password form used for changing password """

    # Current password
    current_password = PasswordField("Current Password", [validators.InputRequired(message="")])

    # New password
    new_password = PasswordField("New Password", [validators.InputRequired(message=""),
                                                  validators.Length(min=8, max=80, message=""),
                                                  ContainsLower(message="Password must contain at least one lowercase letter"),
                                                  ContainsUpper(message="Password must contain at least one uppercase letter"),
                                                  ContainsNumSymbol(message="Password must contain at least one symbol or number")])

    # Confirm password
    confirm_password = PasswordField("Confirm Password", [validators.InputRequired(message=""),
                                                          validators.Length(min=8, max=80, message=""),
                                                          validators.EqualTo("new_password", message="Password entered is different")])


class ForgetPasswordForm(Form):
    """ Forget password link form used for sending password reset link """

    # Email
    email = EmailField("Email", [validators.InputRequired(message=""),
                                 validators.Email(message=""),
                                 validators.Length(max=320, message="")])


class ResetPasswordForm(Form):
    """ Reset password form used when setting new password """

    # New password
    new_password = PasswordField("New Password", [validators.InputRequired(message=""),
                                                  validators.Length(min=8, max=80, message=""),
                                                  ContainsLower(message="Password must contain at least one lowercase letter"),
                                                  ContainsUpper(message="Password must contain at least one uppercase letter"),
                                                  ContainsNumSymbol(message="Password must contain at least one symbol or number")])

    # Confirm password
    confirm_password = PasswordField("Confirm Password", [validators.InputRequired(message=""),
                                                          validators.Length(min=8, max=80, message=""),
                                                          validators.EqualTo("new_password", message="Password entered is different")])


class CreateReviewText(Form):
    review = TextAreaField("Review:", [validators.Length(min=20, max=2000), validators.DataRequired()])


class AccountPageForm(Form):
    """ Account page form used for editing account """

    # Picture
    picture = FileField("Picture", [validators.Optional(),
                                    FileAllowed(["jpg", "jpeg", "png"], message="File uploaded is not in an accepted format")])

    # Name
    name = StringField("Name", [validators.Optional(),
                                validators.Regexp("^[a-zA-Z ]*$", message="Name should only contain letters and spaces"),
                                validators.Length(min=2, max=26, message="Name should be 2-26 characters long")])

    # Gender
    phone_number = StringField("Phone number", [validators.Optional(),
                                                 validators.Length(min=8, max=8, message="Phone number should be 8 characters long")])


class CreateUserForm(Form):
    """ Create user form used when creating new users """
    # Username
    username = StringField("Username", [validators.InputRequired(message=""),
                                        validators.Length(min=3, max=20, message=""),
                                        ValidUsername(message="Username can only contain letters, numbers, and underscores")])

    # Email
    email = EmailField("Email", [validators.InputRequired(message=""),
                                 validators.Email(message=""),
                                 validators.Length(max=320, message="")])

    # Password
    password = PasswordField("Password", [validators.InputRequired(message=""),
                                          validators.Length(min=8, max=80, message=""),
                                          ContainsLower(message="Password must contain at least one lowercase letter"),
                                          ContainsUpper(message="Password must contain at least one uppercase letter"),
                                          ContainsNumSymbol(message="Password must contain at least one symbol or number")])

    # Confirm password
    confirm = PasswordField("Confirm Password", [validators.InputRequired(message=""),
                                                 validators.Length(min=8, max=80, message=""),
                                                 validators.EqualTo("password", message="Password entered is different")])


class DeleteUserForm(Form):
    """ Delete user form used when deleting new users """

    # User ID
    user_id = StringField(validators=[validators.InputRequired(message="")])


class AddBookForm(Form):
    """ Form used for adding books into inventory """

    language = SelectField('Language', [validators.Optional()], default='')
    category = SelectField('Category', [validators.Optional()], default='')
    title = StringField('Title', [validators.InputRequired("Title is required")])
    author = StringField('Author', [validators.InputRequired("Author is required")])
    price = IntegerField('Price', [validators.InputRequired("Price is required"),
                                   validators.NumberRange(min=1, message="Price cannot be less than 1")])
    stock = IntegerField('Stock', [validators.InputRequired("Stock is required"),
                                    validators.NumberRange(min=1, message="Stock cannot be less than 1")])
    description = TextAreaField('Description', [validators.Length(min=1), validators.InputRequired("Description is required")])

    def validate(self, extra_validators=None):
        if not super(AddBookForm, self).validate():
            return False

        if not self.language.data:
            msg = 'Choose a language'
            self.language.errors.append(msg)
            return False

        if not self.category.data:
            msg = 'Choose a category'
            self.category.errors.append(msg)
            return False

        return True
