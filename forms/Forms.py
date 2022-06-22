"""
Form classes used by BrasBasahBooks web app
"""

# Import WTForms
from wtforms import Form, validators, StringField, RadioField,\
                    TextAreaField, EmailField, PasswordField, FileField,\
                    SelectField, IntegerField, DecimalField

# Import custom validations (for password field)
from .Validations import ContainsLower, ContainsUpper, ContainsNumSymbol, ValidUsername

# Import validation for file upload
from flask_wtf.file import FileAllowed


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


class LoginForm(Form):
    """ Login form used for logging in """

    # Username / Email
    username = StringField("Username / Email", [validators.InputRequired(message="")])

    # Password
    password = PasswordField("Password", [validators.InputRequired(message="")])


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


class CreateUserForm(SignUpForm):
    """ Create user form used when creating new users """

    # User Type
    user_type = SelectField("User Type", [validators.InputRequired(message="")],
                            choices=[("", "Select User Type"), ("C", "Customer"), ("A", "Admin")],
                            default="")

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
                                   validators.NumberRange(min=1, message="Price cannot be lower than 1")])
    qty = IntegerField('Quantity', [validators.InputRequired("Quantity is required"),
                                    validators.NumberRange(min=1, message="Quantity cannot be lower than 1")])
    desc = TextAreaField('Description', [validators.Length(min=1), validators.InputRequired("Description is required")])

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
