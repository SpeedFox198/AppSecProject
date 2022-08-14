from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    make_response, g as flask_global, abort, jsonify, session  # TODO: session to be removed
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from SecurityFunctions import generate_uuid4, generate_uuid5, pw_hash, pw_verify, pw_rehash
from db_fetch.customer import create_lockout_time, delete_failed_logins
from session_handler import create_session, create_user_session, get_cookie_value, retrieve_user_session, \
    USER_SESSION_NAME, NEW_COOKIES, EXPIRED_COOKIES
from models import User, Book, Review, Order, UPLOAD_FOLDER as _PROFILE_PIC_PATH, \
    BOOK_IMG_UPLOAD_FOLDER as _BOOK_IMG_PATH
import db_fetch as dbf
import os  # For saving and deleting images
from PIL import Image
from math import ceil
from itsdangerous import URLSafeTimedSerializer, BadData
from encrypt import aws_encrypt, aws_decrypt
from OTP import generateOTP
from google_authenticator import gmail_send
from csp import get_csp
from api_schema import LOGIN_SCHEMA, CREATE_USER_SCHEMA
from flask_expects_json import expects_json
import jsonschema
from functools import wraps
from flask_wtf.csrf import CSRFProtect, CSRFError
from urllib.parse import unquote
from typing import Union
import pyotp
import datetime

from forms import (
    SignUpForm, LoginForm, ChangePasswordForm, ResetPasswordForm, ForgetPasswordForm,
    AccountPageForm, CreateUserForm, DeleteUserForm, AddBookForm, OrderForm, OTPForm, CreateReviewText, BackUpCodeForm
)

import stripe

# CONSTANTS
# TODO @everyone: set to False when deploying
DEBUG = False  # Debug flag (True when debugging)
TOKEN_MAX_AGE = 900  # Max age of token (15 mins)
ACCOUNTS_PER_PAGE = 10  # Number of accounts to display per page (manage account page)
DOMAIN_NAME = "https://localhost:5000/"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
DISALLOWED_CHARA_DICT = str.maketrans("", "", r"<>{}")

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_pyfile("config/app.cfg")  # Load config file
app.jinja_env.add_extension("jinja2.ext.do")  # Add do extension to jinja environment
BOOK_UPLOAD_FOLDER = _BOOK_IMG_PATH[1:]  # Book image upload folder
PROFILE_PIC_UPLOAD_FOLDER = _PROFILE_PIC_PATH[1:]  # Profile pic upload folder
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Ld_DnUhAAAAAGcuOtjXHX-peLN2QURPU8nhtT2d'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ld_DnUhAAAAAKHGn71fzgPvdcvvoqRLDF812aKr'
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["30 per second"]
)

url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# testing mode
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51LNFSvLeIrXIJDLVMtA0cZuNhFl3fFrgE6fjUAgSEzhs9SHLF5alwOVK8Cu1XZcF7NF9GBEinYI9nY8WuRw7c7ee00qzmDKaVq'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51LNFSvLeIrXIJDLVEVQ8XVgIIhIWcKy0d7WVM5mM7TIBTxNLNMFUcN5Gx3zcmTKHyxJkrxiB98qZzdt5qYYrPM55002ARsY3yC'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

def allowed_file(filename):
    # Return true if there is an extension in file, and its extension is in the allowed extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user():
    """ Returns user if cookie is correct, else returns None """

    # Get session cookie from request
    user_session = retrieve_user_session(request)

    # Return None
    if user_session is not None and not user_session.is_expired():

        # Retrieve user id from session
        user_id = user_session.user_id

        # Retrieve user data from database
        user_data = dbf.retrieve_user(user_id)

        # If user is not found
        if user_data is not None:

            # If user is a customer
            if not user_data[5]:
                user_data += dbf.retrieve_customer_details(user_id)

            # Return user object
            return User(*user_data)


def user_authenticate(username: str, password: str) -> Union[tuple, None]:
    """ Authenticates password for username/email """

    if "@" in username:  # Authenticate by email
        user_emails = dbf.retrieve_user_ids_and_emails()
        user_id = None
        for i in user_emails:
            the_email = i[1]  # Email is in index 0 of tuple
            if aws_decrypt(the_email) == username:
                user_id = i[0]
                break
    else:                # Authenticate by username
        user_id = dbf.retrieve_user_by_username(username)

    user = None
    if user_id is not None:
        hashed_pass = dbf.retrieve_password(user_id)
        if hashed_pass is None:
            raise ValueError(f"Critical: {user_id} user's password is empty!")
        elif pw_verify(hashed_pass, password):
            user = dbf.retrieve_user(user_id)

    return user


def add_cookie(cookies: dict):
    """ Adds cookies """
    if not isinstance(cookies, dict):
        raise TypeError("Expected dictionary")
    new_cookies: dict = flask_global.get(NEW_COOKIES, default={})
    new_cookies.update(cookies)
    flask_global.new_cookies = new_cookies


def remove_cookies(cookies: list):
    """ Remove cookies """
    if not isinstance(cookies, list):
        raise TypeError("Expected list")
    expired_cookies: list = flask_global.get(EXPIRED_COOKIES, default=[])
    expired_cookies.extend(cookies)
    flask_global.expired_cookies = expired_cookies


def login_required(func):
    """
    Put this in routes that user must be logged in to access with the @ sign
    For example:
    @app.route('/user/account")
    @login_required
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        Logged in check here
        """
        if isinstance(flask_global.user, User):
            return func(*args, **kwargs)
        return redirect(url_for('login'))

    return decorated_function


def roles_required(roles: list[str], mode="regular"):
    """
    Put this in routes that only allow selected roles with the @ sign
    For example:
    @app.route('/admin/manage-account")
    @roles_required(["admin"])

    You can also add multiple roles for the route
    E.g:
    @app.route('/admin/inventory')
    @roles_required(["admin", "staff"])
    """

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            """Admin Check Here
            2 Modes:
            regular - for regular routes
            api - for api routes
            Checks if there is a logged-in session and if the user is an admin
            """
            user: User = flask_global.user
            if not isinstance(user, User) or user.role not in roles:
                if mode == "regular":
                    abort(404)
                elif mode == "api":
                    return jsonify(message="The resource you requested does not exist."), 404
            # Execute routes after
            return func(*args, **kwargs)
        return decorated_function
    return decorator


""" Before request """


@app.before_request
def before_request():
    flask_global.user = get_user()  # Get user
    csrf.protect()


""" After request """


@app.after_request
def after_request(response):
    user: User = flask_global.user

    # Get expired cookies to be deleted and new cookies to be set
    expired_cookies = flask_global.get(EXPIRED_COOKIES, default=[])
    new_cookies = flask_global.get(NEW_COOKIES, default={})

    # It needs to be a list for me to iterate through
    if not isinstance(expired_cookies, list):
        raise TypeError("Expired cookies should be stored in a list")

    # I need name value and value for each new cookie
    if not isinstance(new_cookies, dict):
        raise TypeError("New cookies should be stored in a dictionary")

    # Only renew session if login
    if isinstance(user, User):
        renewed_user_session = create_user_session(user.user_id, user.role)
        response.set_cookie(USER_SESSION_NAME, renewed_user_session, httponly=True, secure=True, samesite="Lax")

    # Default log user out
    else:
        # Remove session cookie
        expired_cookies.append(USER_SESSION_NAME)

    # Delete expired cookies
    for delete_this in expired_cookies:
        response.set_cookie(delete_this, "", expires=0, httponly=True, secure=True, samesite="Lax")

    # Set new cookies
    for name, value in new_cookies.items():
        response.set_cookie(name, create_session(value), httponly=True, secure=True, samesite="Lax")

    # Set CSP to prevent XSS
    allow_blob = flask_global.get("allow_blob", default=False)
    response.headers["Content-Security-Policy"] = get_csp(blob=allow_blob)

    return response


"""    Home Page    """

""" Home page """


@app.route("/")
@limiter.limit("10/second", override_defaults=False)
def home():
    if flask_global.user and flask_global.user.role in ["admin", "staff"]:
        return redirect(url_for("dashboard"))

    english_books_data = dbf.retrieve_books_by_language("English")
    chinese_books_data = dbf.retrieve_books_by_language("Chinese")
    english = [Book(*data) for data in english_books_data]
    chinese = [Book(*data) for data in chinese_books_data]
    return render_template("home.html", english=english, chinese=chinese)  # optional: books_list=books_list


"""    Login/Sign-up Pages    """

""" Sign up page """


@app.route("/user/sign-up", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def sign_up():
    # If user is already logged in
    if flask_global.user is not None:
        return redirect(url_for("account"))

    # Get sign up form
    sign_up_form = SignUpForm(request.form)

    # Flask global error variable for css
    errors = flask_global.errors = {}

    # Validate sign up form if request is post
    if request.method == "POST":
        if not sign_up_form.validate():
            errors["DisplayFieldError"] = True
            return render_template("user/sign_up.html", form=sign_up_form)

        # Extract data from sign up form
        username = sign_up_form.username.data
        email = sign_up_form.email.data.lower()
        password = sign_up_form.password.data

        # Create new user

        # Ensure that email and username are not registered yet
        if dbf.username_exists(username):
            errors["DisplayFieldError"] = errors["SignUpUsernameError"] = True
            flash("Username taken", "sign-up-username-error")
            return render_template("user/sign_up.html", form=sign_up_form)

        elif dbf.email_exists(email):
            errors["DisplayFieldError"] = errors["SignUpEmailError"] = True
            flash("Email already registered", "sign-up-email-error")
            return render_template("user/sign_up.html", form=sign_up_form)

        elif username.lower() in password.lower():
            errors["DisplayFieldError"] = errors["SignUpPasswordError"] = True
            flash("Password cannot contain username", "sign-up-password-error")
            return render_template("user/sign_up.html", form=sign_up_form)

        one_time_pass = generateOTP()
        user_id = generate_uuid5(username)
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        second = datetime.datetime.now().second
        print(one_time_pass)
        if dbf.retrieve_otp(user_id):
            print("deleted")
            dbf.delete_otp(user_id)
        dbf.create_otp(user_id, one_time_pass, year, month, day, hour, minute, second)
        # Send email with OTP
        subject = "OTP for registration"
        message = "Do not reply to this email.\nPlease enter " + one_time_pass + " as your OTP to complete your registration."

        gmail_send(email, subject, message)
        add_cookie({"Temp_User_ID": user_id, "Temp_User_Email": email, "Temp_User_Password": password, "Temp_User_Username": username})

        return redirect(url_for("otpverification"))

    # Render sign up page
    return render_template("user/sign_up.html", form=sign_up_form)


@app.route("/user/sign-up/otpverification", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def otpverification():
    temp_user_id = get_cookie_value(request, "Temp_User_ID")
    username = get_cookie_value(request, "Temp_User_Username")
    email = get_cookie_value(request, "Temp_User_Email")
    password = get_cookie_value(request, "Temp_User_Password")
    if temp_user_id is None:
        return redirect(url_for("sign_up"))
    else:
        pass
    temporary_data = dbf.retrieve_otp(temp_user_id)
    if temporary_data is None:
        return redirect(url_for("sign_up"))
    else:
        pass
    one_time_pass = temporary_data[1]
    year = temporary_data[2]
    month = temporary_data[3]
    day = temporary_data[4]
    hour = temporary_data[5]
    minute = temporary_data[6]
    second = temporary_data[7]
    print(one_time_pass)
    dateregister = datetime.datetime(year, month, day, hour, minute, second)
    time_check = datetime.datetime.now() - dateregister
    if time_check.seconds > 300:
        dbf.delete_otp(temp_user_id)
        flash("OTP expired please try again", "OTP-expired")
        return redirect(url_for("sign_up"))
    OTPformat = OTPForm(request.form)
    print(request.method)
    if request.method == "POST":
        OTPinput = OTPformat.otp.data
        if one_time_pass == OTPinput:
            # Create new customer
            user_id = generate_uuid5(username)  # Generate new unique user id for customer
            dbf.create_customer(user_id, username, aws_encrypt(email), pw_hash(password))

            # Create new user session to login (placeholder values were used to create user object)
            flask_global.user = User(user_id, "", "", "", "", "customer")
            remove_cookies(["Temp_User_ID", "Temp_User_Email", "Temp_User_Password", "Temp_User_Username"])

            # Return redirect with session cookie
            return redirect(url_for("home"))

        else:
            flash("Invalid OTP Entered! Please try again!")
            return redirect(url_for("otpverification"))
    else:
        return render_template("user/OTP.html", form=OTPformat)


""" Login page """


@app.route("/user/login", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def login():
    # If user is already logged in
    if flask_global.user is not None:
        return redirect(url_for("account"))

    login_form = LoginForm(request.form)

    # Render page's template
    return render_template("user/login.html", form=login_form)


@app.route("/user/login/twoFA", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def twoFA():
    user_id = get_cookie_value(request, "user_id")
    user_data = get_cookie_value(request, "user_data")
    twoFA_code = dbf.retrieve_2FA_token(user_id)

    next_page = unquote(request.args.get("from", default="", type=str))

    OTPformat = OTPForm(request.form)

    if not (user_id and user_data and twoFA_code):
        remove_cookies(["user_id", "user_data"])
        return redirect(url_for("login"))

    if request.method == "POST":
        twoFAinput = OTPformat.otp.data
        twoFAchecker = pyotp.TOTP(twoFA_code[1]).verify(twoFAinput)
        try:
            if twoFAchecker:
                # Get user object
                user = User(*user_data)

                # Create session to login
                flask_global.user = user
                if bool(dbf.retrieve_failed_login(user.user_id[1])):
                    dbf.delete_failed_logins(user.user_id)
                remove_cookies(["user_id", "user_data"])

                if next_page and next_page[:len(DOMAIN_NAME)] == DOMAIN_NAME:
                    return redirect(next_page)
                else:
                    return redirect(url_for("home"))
            else:
                flash("Invalid OTP Entered! Please try again!")
                return redirect(request.full_path)
        except:
            remove_cookies(["user_id", "user_data"])
            return redirect(url_for("login"))
    else:
        return render_template("user/2FA.html", form=OTPformat, twoFA_code=twoFA_code)


""" Forgot password page """


@app.route("/user/password/forget", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def password_forget():
    # Create form
    forget_password_form = ForgetPasswordForm(request.form)

    if request.method == "POST":
        if not forget_password_form.validate():
            if DEBUG: print("Forget Password: form field invalid")
            session["DisplayFieldError"] = True
        else:
            # Configure noreplybbb02@gmail.com
            # app.config.from_pyfile("config/noreply_email.cfg")
            # mail.init_app(app)

            # Get email
            email = forget_password_form.email.data.lower()

            if dbf.email_exists(aws_encrypt(email)):
                # Generate token
                token = url_serialiser.dumps(email, salt=app.config["PASSWORD_FORGET_SALT"])

                # Send message to email entered
                subject = "Reset Your Password"
                message = "Do not reply to this email.\nPlease click on ths link to reset your password." + url_for(
                    "password_reset", token=token, _external=True)

                gmail_send(email, subject, message)

            flash(f"Verification email sent to {email}")
            return redirect(url_for("login"))

    return render_template("user/password/password_forget.html", form=forget_password_form)

#In case maybe google authenticator

@app.route("/user/account/google_authenticator", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required
def google_authenticator():
    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(403)

    secret_token = get_cookie_value(request, "token")
    if secret_token is None:
        secret_token = pyotp.random_base32()
        add_cookie({"token": secret_token})
    OTP_Test = OTPForm(request.form)
    OTP_check = OTP_Test.otp.data
    if request.method == "POST":
        verified = pyotp.TOTP(secret_token).verify(OTP_check)
        if verified:
            flash("2FA setup Complete")
            dbf.create_2FA_token(user.user_id, secret_token)
            remove_cookies(["token"])
            return redirect(url_for("backup_codes"))
        else:
            flash("Invalid OTP Entered! Please try again!")
            return redirect(url_for("google_authenticator"))
    else:
        return render_template("user/google_authenticator.html", form=OTP_Test, secret_token=secret_token)

@app.route("/user/account/google_authenticator/backup_codes", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required
def backup_codes():
    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(403)
    code1 = generateOTP()
    code2 = generateOTP()
    code3 = generateOTP()
    code4 = generateOTP()
    code5 = generateOTP()
    code6 = generateOTP()
    dbf.create_backup_codes(user.user_id, code1, code2, code3, code4, code5, code6)
    return render_template("user/backup_codes.html", code1=code1, code2=code2, code3=code3, code4=code4, code5=code5, code6=code6)

@app.route("/user/login/twoFA/backup_codes", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def backup_codes_login():
    # User is a Class
    user_id = get_cookie_value(request, "user_id")
    user_data = get_cookie_value(request, "user_data")

    back_up_form = BackUpCodeForm(request.form)
    codes = dbf.retrieve_backup_codes(user_id)
    code1 = codes[1]
    code2 = codes[2]
    code3 = codes[3]
    code4 = codes[4]
    code5 = codes[5]
    code6 = codes[6]
    if request.method == "POST":
        codecheck1 = back_up_form.code1.data
        codecheck2 = back_up_form.code2.data
        codecheck3 = back_up_form.code3.data
        codecheck4 = back_up_form.code4.data
        codecheck5 = back_up_form.code5.data
        codecheck6 = back_up_form.code6.data
        if codecheck1 == code1 and codecheck2 == code2 and codecheck3 == code3 and codecheck4 == code4 and codecheck5 == code5 and codecheck6 == code6:
            user = User(*user_data)

            # Create session to login
            flask_global.user = user
            if bool(dbf.retrieve_failed_login(user.user_id[1])):
                dbf.delete_failed_logins(user.user_id)
            remove_cookies(["user_id", "user_data"])
            return redirect(url_for("home"))
        else:
            flash("Invalid Backup Codes Entered! Please try again!")
            return redirect(url_for("backup_codes_login"))
            
    return render_template("user/lost_2FA.html", form=back_up_form, code1=code1, code2=code2, code3=code3, code4=code4, code5=code5, code6=code6)


@app.route("/user/account/google_authenticator_disable", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required
def google_authenticator_disable():
    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(403)

    dbf.delete_2FA_token(user.user_id)
    dbf.delete_backup_codes(user.user_id)
    flash("2FA has been disabled")
    return redirect(url_for("account"))

""" Reset password page """


@app.route("/user/password/reset/<token>", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def password_reset(token):
    # Get user

    # Only Guest will forget password
    user: User = flask_global.user

    if isinstance(user, User):
        return redirect(url_for("account"))

    # Get email from token
    try:
        email = url_serialiser.loads(token, salt=app.config["PASSWORD_FORGET_SALT"], max_age=TOKEN_MAX_AGE)
    except BadData:  # Token expired or Bad Signature
        flash("Token expired or invalid")
        return redirect(url_for("home"))

    # Get user
    try:
        user_check = dbf.retrieve_user_id(aws_encrypt(email))
    except:
        flash("Token expired or invalid")
        return redirect(url_for("home"))

    # Render form
    reset_password_form = ResetPasswordForm(request.form)
    if request.method == "POST":
        if not reset_password_form.validate():
            session["DisplayFieldError"] = True
        else:
            # Extract password
            new_password = reset_password_form.new_password.data

            # Reset Password
            print(user_check)
            dbf.change_password(user_check, pw_hash(new_password))

            # Get user object
            user = User(*user_authenticate(email, new_password))

            # Create session to login
            flask_global.user = user

            print(user)
            user_username = user.username
            print(user_username)
            if bool(dbf.retrieve_failed_login(user_username)):
                print("Check 1")
                dbf.delete_failed_logins(user_username)
            if bool(dbf.retrieve_lockout_time(user_username)):
                print("Check 2")
                dbf.delete_lockout_time(user_username)
            # Flash message and redirect to account page
            flash("Password has been successfully set")
            return redirect(url_for("account"))

    return render_template("user/password/password_reset.html", form=reset_password_form, email=email)


""" Change password page """


@app.route("/user/password/change", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required
def password_change():
    # Get current user
    user: User = flask_global.user

    if user.role == "admin":
        abort(404)
    # Flask global error variable for css
    errors = flask_global.errors = {}

    # Get change password form
    change_password_form = ChangePasswordForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST":
        if not change_password_form.validate():
            errors["DisplayFieldError"] = True

        else:
            # Extract data from sign up form
            current_password = change_password_form.current_password.data
            new_password = change_password_form.new_password.data

            # Password (current) was incorrect, disallow change
            if not user_authenticate(user.username, current_password):
                errors["DisplayFieldError"] = errors["CurrentPasswordError"] = True
                flash("Your password is incorrect, please try again", "current-password-error")

            # Current and new passwords are the same, disallow change
            elif current_password == new_password:
                errors["DisplayFieldError"] = errors["NewPasswordError"] = True
                flash("New password should not be the same as current password", "new-password-error")

            # Username is inside new password (insecure), disallow change
            elif user.username.lower() in new_password.lower():
                errors["DisplayFieldError"] = errors["NewPasswordError"] = True
                flash("Password cannot contain username", "new-password-error")

            # Password (current) was correct, change to new password
            else:
                # Change user password
                dbf.change_password(user.user_id, pw_hash(new_password))

                # Sign user out (proccess will be done in @app.after_request)
                flask_global.user = None

                # Flash success message and redirect
                flash("Password has been changed successfully, please login again with your new password.")
                return redirect(url_for("login"))

    return render_template("user/password/password_change.html", form=change_password_form)


""" View account page """


@app.route("/user/account", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required
def account():
    # Get current user
    user: User = flask_global.user

    # If user is not logged in
    if not user:
        return redirect(url_for("login"))

    if user.role == "admin":
        abort(404)

    # Get account page form
    account_page_form = AccountPageForm(request.form)

    # Validate account page form if request is post
    if request.method == "POST":

        if not account_page_form.validate():
            name = account_page_form.name
            picture = account_page_form.picture
            phone_number = account_page_form.phone_number

            # Flash error message (only flash the 1st error)
            error = name.errors[0] if name.errors else picture.errors[0] if picture.errors else phone_number.errors[0]
            flash(error, "error")
        else:
            # Flash success message
            flash("Account settings updated successfully")

            # Extract email and password from sign up form
            name = " ".join(account_page_form.name.data.split())
            phone_number = account_page_form.phone_number.data
            profile_pic_filename = user._profile_pic

            # Check files submitted for profile pic
            if "picture" in request.files:
                profile_pic = request.files["picture"]
                if profile_pic and allowed_file(profile_pic.filename):
                    profile_pic_filename = f"{user.user_id}.png"
                    profile_pic.save(os.path.join(PROFILE_PIC_UPLOAD_FOLDER, profile_pic_filename))

            # Apparently account details were needed to be split because profile picture is in user table
            account_details = (name, phone_number, user.user_id)
            account_details2 = (profile_pic_filename, user.user_id)
            dbf.update_customer_account(account_details, account_details2)

        # Redirect to prevent form resubmission
        return redirect(url_for("account"))

    # Set username and gender to display
    account_page_form.name.data = user.name
    account_page_form.phone_number.data = user.phone_no
    twoFA_enabled = bool(dbf.retrieve_2FA_token(user.user_id))

    # Allow blob on this site only (for CSP)
    flask_global.allow_blob = True

    return render_template("user/account.html",
                           form=account_page_form,
                           picture_path=user.profile_pic,
                           username=user.username,
                           email=aws_decrypt(user.email),
                           phone_no=user.phone_no,
                           twoFA_enabled=twoFA_enabled)


"""    Admin/Staff Pages    """


@app.route("/admin/dashboard", methods=["GET"])
@roles_required(["admin", "staff"])
def dashboard():
    customers = dbf.number_of_customers()
    orders = dbf.number_of_orders()
    book_count = dbf.number_of_books()
    staff = dbf.number_of_staff()
    reviews = dbf.no_of_all_reviews()
    if flask_global.user.role == "admin":
        return render_template("admin/admin_dashboard.html",
                               customer_count=customers,
                               order_count=orders,
                               book_count=book_count,
                               staff_count=staff)

    elif flask_global.user.role == "staff":
        return render_template("admin/staff_dashboard.html",
                               order_count=orders,
                               book_count=book_count,
                               review_count=reviews)


# Manage accounts page
@app.route("/admin/manage-users", methods=["GET", "POST"])
@roles_required(["admin"])
def manage_users():
    # Flask global error variable for css
    flask_global.errors = {}
    errors = flask_global.errors

    # Get page number
    active_page = request.args.get("page", default=1, type=int)

    # Get sign up form
    create_user_form = CreateUserForm(request.form)
    delete_user_form = DeleteUserForm(request.form)

    form_trigger = "addUserButton"  # id of form to trigger on page load

    # If GET request to page (no forms sent)
    if request.method == "GET":
        form_trigger = ""

    # Else, POST request to delete/create user
    else:

        # If action is to delete user (and POST request is valid)
        if delete_user_form.validate() and delete_user_form.user_id.data:

            # Delete selected user
            user_id = delete_user_form.user_id.data

            # Try deleting the user (False if user doesn't exist)
            deleted_customer = dbf.delete_customer(user_id)

            # If customer exists in database (and is deleted)
            if deleted_customer:
                deleted_customer = User(*deleted_customer)
                # Flash success message
                flash(f"Deleted customer: {deleted_customer.username}")

            # Else user is not in database
            else:
                # Flash warning message
                flash("Customer does not exist", "warning")

            # Redirect to prevent form resubmission
            return redirect(f"{url_for('manage_users')}?page={active_page}")

        # If action is to create user (and POST request is valid)
        elif create_user_form.validate():
            # Extract data from sign up form
            username = create_user_form.username.data
            email = create_user_form.email.data.lower()
            password = create_user_form.password.data

            # Ensure that username is not registered yet
            if dbf.username_exists(username):
                errors["DisplayFieldError"] = errors["CreateUserUsernameError"] = True
                flash("Username taken", "create-user-username-error")

            # Ensure that email is not registered yet
            elif dbf.email_exists(aws_encrypt(email)):
                errors["DisplayFieldError"] = errors["CreateUserEmailError"] = True
                flash("Email already registered", "create-user-email-error")

            # If username and email are not used, create customer
            else:
                user_id = generate_uuid5(username)  # Generate new unique user id for customer
                dbf.create_customer(user_id, username, aws_encrypt(email), pw_hash(password))
                flash(f"Created new customer: {username}")
                return redirect(f"{url_for('manage_users')}?page={active_page}")

        # Else, form was invalid
        else:
            errors["DisplayFieldError"] = True

    # Get total number of customers
    customer_count = dbf.number_of_customers()

    # Set page number
    last_page = ceil(customer_count / ACCOUNTS_PER_PAGE) or 1
    if active_page < 1:
        active_page = 1
    elif active_page > last_page:
        active_page = last_page

    # Get users to be displayed
    offset = (active_page - 1) * ACCOUNTS_PER_PAGE  # Offset for SQL query
    display_users = [User(*data) for data in dbf.retrieve_these_customers(ACCOUNTS_PER_PAGE, offset)]

    first_index = (active_page - 1) * ACCOUNTS_PER_PAGE

    # Get page list
    if last_page <= 5:
        page_list = [i for i in range(1, last_page + 1)]
    else:
        center_item = active_page
        if center_item < 3:
            center_item = 3
        elif center_item > last_page - 2:
            center_item = last_page - 2
        page_list = [i for i in range(center_item - 2, center_item + 2 + 1)]
    prev_page = active_page - 1 if active_page - 1 > 0 else active_page
    next_page = active_page + 1 if active_page + 1 <= last_page else last_page

    # Get entries range
    entries_range = (first_index + 1, first_index + len(display_users))

    return render_template(
        "admin/manage_accounts.html",
        display_users=display_users,
        aws_decrypt=aws_decrypt,
        active_page=active_page, page_list=page_list,
        prev_page=prev_page, next_page=next_page,
        first_page=1, last_page=last_page,
        entries_range=entries_range, total_entries=customer_count,
        form_trigger=form_trigger,
        create_user_form=create_user_form,
        delete_user_form=delete_user_form
    )


@app.route('/admin/manage-staff', methods=["GET", "POST"])
@roles_required(["admin"])
def manage_staff():
    # Flask global error variable for css
    flask_global.errors = {}
    errors = flask_global.errors

    # Get page number
    active_page = request.args.get("page", default=1, type=int)

    # Get sign up form
    create_staff_form = CreateUserForm(request.form)
    delete_staff_form = DeleteUserForm(request.form)

    form_trigger = "addUserButton"  # id of form to trigger on page load

    # If GET request to page (no forms sent)
    if request.method == "GET":
        form_trigger = ""

    # Else, POST request to delete/create user
    else:
        # If action is to delete user (and POST request is valid)
        if delete_staff_form.validate() and delete_staff_form.user_id.data:

            # Delete selected user
            user_id = delete_staff_form.user_id.data

            # Try deleting the user (False if user doesn't exist)
            deleted_staff = dbf.delete_staff(user_id)

            # If customer exists in database (and is deleted)
            if deleted_staff:
                deleted_staff = User(*deleted_staff)
                # Flash success message
                flash(f"Deleted staff: {deleted_staff.username}")

            # Else user is not in database
            else:
                # Flash warning message
                flash("Staff does not exist", "warning")

            # Redirect to prevent form resubmission
            return redirect(f"{url_for('manage_staff')}?page={active_page}")

        # If action is to create user (and POST request is valid)
        elif create_staff_form.validate():
            # Extract data from sign up form
            username = create_staff_form.username.data
            email = create_staff_form.email.data.lower()
            password = create_staff_form.password.data

            # Ensure that username is not registered yet
            if dbf.username_exists(username):
                errors["DisplayFieldError"] = errors["CreateUserUsernameError"] = True
                flash("Username taken", "create-user-username-error")

            # Ensure that email is not registered yet
            elif dbf.email_exists(aws_encrypt(email)):
                errors["DisplayFieldError"] = errors["CreateUserEmailError"] = True
                flash("Email already registered", "create-user-email-error")

            # If username and email are not used, create customer
            else:
                user_id = generate_uuid5(username)  # Generate new unique user id for customer
                dbf.create_staff(user_id, username, aws_encrypt(email), pw_hash(password))
                flash(f"Created new staff: {username}")
                return redirect(f"{url_for('manage_staff')}?page={active_page}")

        # Else, form was invalid
        else:
            errors["DisplayFieldError"] = True

    # Get total number of customers
    staff_count = dbf.number_of_staff()

    # Set page number
    last_page = ceil(staff_count / ACCOUNTS_PER_PAGE) or 1
    if active_page < 1:
        active_page = 1
    elif active_page > last_page:
        active_page = last_page

    # Get users to be displayed
    offset = (active_page - 1) * ACCOUNTS_PER_PAGE  # Offset for SQL query
    display_users = [User(*data) for data in dbf.retrieve_all_staff(ACCOUNTS_PER_PAGE, offset)]

    first_index = (active_page - 1) * ACCOUNTS_PER_PAGE

    # Get page list
    if last_page <= 5:
        page_list = [i for i in range(1, last_page + 1)]
    else:
        center_item = active_page
        if center_item < 3:
            center_item = 3
        elif center_item > last_page - 2:
            center_item = last_page - 2
        page_list = [i for i in range(center_item - 2, center_item + 2 + 1)]
    prev_page = active_page - 1 if active_page - 1 > 0 else active_page
    next_page = active_page + 1 if active_page + 1 <= last_page else last_page

    # Get entries range
    entries_range = (first_index + 1, first_index + len(display_users))

    return render_template(
        "admin/manage_staff.html",
        display_users=display_users,
        aws_decrypt=aws_decrypt,
        active_page=active_page, page_list=page_list,
        prev_page=prev_page, next_page=next_page,
        first_page=1, last_page=last_page,
        entries_range=entries_range, total_entries=staff_count,
        form_trigger=form_trigger,
        create_user_form=create_staff_form,
        delete_user_form=delete_staff_form
    )


@app.route('/admin/inventory')
@roles_required(["admin", "staff"])
def inventory():
    inventory_data = dbf.retrieve_inventory()

    # Create book object and store in inventory
    book_inventory = [Book(*data) for data in inventory_data]
    return render_template('admin/inventory.html', count=len(book_inventory), books_list=book_inventory)


@app.route('/admin/book/<book_id>')
@roles_required(["admin", "staff"])
def view_book(book_id):
    book_data = dbf.retrieve_book(book_id)

    if book_data is None:
        abort(404)

    book = Book(*book_data)
    return render_template("admin/book_info_admin.html", book=book)


lang_list = [('', 'Select'), ('English', 'English'), ('Chinese', 'Chinese'), ('Malay', 'Malay'), ('Tamil', 'Tamil')]
category_list = [('', 'Select'), ('Action & Adventure', 'Action & Adventure'), ('Classic', 'Classic'),
                 ('Comic', 'Comic'), ('Detective & Mystery', 'Detective & Mystery')]


@app.route('/admin/add-book', methods=['GET', 'POST'])
@roles_required(["admin", "staff"])
def add_book():
    add_book_form = AddBookForm(request.form)
    add_book_form.language.choices = lang_list
    add_book_form.category.choices = category_list

    # Book cover upload (Code is from Flask documentation https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/)

    if request.method == "POST" and add_book_form.validate():
        if 'bookimg' not in request.files:
            flash('There is no image uploaded!')
            return redirect(request.url)

        book_img = request.files['bookimg']

        if book_img == '':
            flash('No selected image')
            return redirect(request.url)

        if book_img and allowed_file(book_img.filename):
            book_id = generate_uuid4()
            book_img_filename = f"{book_id}.png"  # Generate unique name string for files
            path = os.path.join(BOOK_UPLOAD_FOLDER, book_img_filename)
            book_img.save(path)
            image = Image.open(path)
            resized_image = image.resize((259, 371))
            resized_image.save(path)

            book_details = (book_id,
                            add_book_form.language.data,
                            add_book_form.category.data,
                            add_book_form.title.data,
                            int(add_book_form.stock.data),  # int for sqlite
                            int(add_book_form.price.data),  # int for sqlite
                            add_book_form.author.data,
                            add_book_form.description.data,
                            book_img_filename)

            dbf.book_add(book_details)
            flash("Book successfully added!")

    # Allow blob on this site only (for CSP)
    flask_global.allow_blob = True

    return render_template('admin/add_book.html', form=add_book_form)


@app.route('/admin/update-book/<book_id>/', methods=['GET', 'POST'])
@roles_required(["admin", "staff"])
def update_book(book_id):
    # Get specified book
    if not dbf.retrieve_book(book_id):
        abort(404)

    selected_book = Book(*dbf.retrieve_book(book_id))

    update_book_form = AddBookForm(request.form)
    update_book_form.language.choices = lang_list
    update_book_form.category.choices = category_list

    if request.method == 'POST' and update_book_form.validate():

        book_img = request.files['bookimg']

        # If no selected book cover
        book_img_filename = selected_book._cover_img

        if book_img and allowed_file(book_img.filename):
            book_img_filename = f"{generate_uuid4()}.png"  # Generate unique name string for files
            path = os.path.join(BOOK_UPLOAD_FOLDER, book_img_filename)
            book_img.save(path)
            image = Image.open(path)
            resized_image = image.resize((259, 371))
            resized_image.save(path)

        updated_details = (
            update_book_form.language.data,
            update_book_form.category.data,
            update_book_form.title.data,
            int(update_book_form.stock.data),
            int(update_book_form.price.data),
            update_book_form.author.data,
            update_book_form.description.data,
            book_img_filename,
        )
        dbf.book_update(updated_details, selected_book.book_id)
        flash("Book successfully updated!")
        return redirect(url_for('inventory'))
    else:
        update_book_form.language.data = selected_book.language
        update_book_form.category.data = selected_book.genre
        update_book_form.title.data = selected_book.title
        update_book_form.author.data = selected_book.author
        update_book_form.price.data = selected_book.price
        update_book_form.stock.data = selected_book.stock
        update_book_form.description.data = selected_book.description
        return render_template('admin/update_book.html', form=update_book_form)


@app.route('/admin/delete-book/<book_id>/', methods=['POST'])
@roles_required(["admin", "staff"])
def delete_book(book_id):
    # Deletes book and its cover image
    selected_book = Book(*dbf.retrieve_book(book_id))
    book_cover_img = selected_book.cover_img[1:]  # Strip the leading slash for relative path
    print(book_cover_img)
    if os.path.isfile(book_cover_img):
        os.remove(book_cover_img)
    else:
        print("Book cover does not exist.")
    dbf.delete_book(book_id)
    return redirect(url_for('inventory'))


@app.route("/staff/manage-orders")
@roles_required(["staff"])
def manage_orders():
    orders = [Order(*data) for data in dbf.get_all_orders()]
    return render_template('staff/manage_orders.html',
                           orders=orders,
                           get_order_items=dbf.get_order_items,
                           retrieve_book=dbf.retrieve_book,
                           Book=Book)


@app.route("/staff/manage-reviews")
@roles_required(["staff"])
def manage_reviews():
    books_list = [Book(*rows) for rows in dbf.retrieve_inventory()]
    books_and_reviews_list = [(book, dbf.no_of_reviews_from_book(book.book_id)) for book in books_list]
    return render_template('staff/manage_reviews.html', books_list=books_and_reviews_list)


"""    Books Pages    """


@app.route("/book/<book_id>", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def book_info(book_id):
    if flask_global.user and flask_global.user.role in ["admin", "staff"]:
        return redirect(url_for('dashboard'))

    # Get book details
    book_data = dbf.retrieve_book(book_id)

    # Abort 404 if book_id does not exist
    if book_data is None:
        abort(404)

    book_id = book_data[0]
    book = Book(*book_data)

    return render_template("book_info.html", book=book, book_id=book_id)


# TODO: @Miku @SpeedFox198 work on this (perhaps we not using this?)
@app.route("/book/<book_id>/book_review", methods=["GET", "POST"])
def book_review(book_id):
    # Get current user
    user: User = flask_global.user

    # If user is not logged in
    if not user:
        return redirect(url_for("login"))

    if user.role == "admin":
        abort(404)

    # Get book details
    book_data = dbf.retrieve_book(book_id)

    if book_data is None:
        abort(404)

    book_id = book_data[0]
    book = Book(*book_data)
    createReview = CreateReviewText(request.form)
    if request.method == "POST":
        error_occured = True
        if createReview.validate():
            error_occured = False
            data:str = " ".join(createReview.review.data.split())
            data = data.translate(DISALLOWED_CHARA_DICT)
            if len(data) < 20 or len(data) > 200:
                error_occured = True
            else:
                dbf.add_review(book_id, user.user_id, request.form.get("rate"), data)
                flash("Review successfully added!")
        if error_occured:
            flash("An error occured, review not added!", category="error")
        return redirect(url_for("book_info", book_id=book_id))
    return render_template("review.html", book=book, form=createReview, book_id = book_id)


""" Search Results Page """


@app.route("/books/<sort_this>")
@limiter.limit("10/second", override_defaults=False)
def books(sort_this):
    if flask_global.user and flask_global.user.role == "admin":
        abort(403)
    sort_dict = {}
    books_dict = {}
    language_list = set()
    inventory_data = dbf.retrieve_inventory()

    sort_by = request.args.get("sort-by", default="", type=str)

    for data in inventory_data:
        book = Book(*data)
        books_dict[book.book_id] = book
        language_list.add(book.language)

    if books_dict != {}:
        if sort_this == 'latest':
            books_dict = dict(reversed(list(books_dict.items())))
            sort_dict = books_dict
        elif sort_this == 'name_a_to_z':
            sort_dict = name_a_to_z(books_dict)
        elif sort_this == 'name_z_to_a':
            sort_dict = name_z_to_a(books_dict)
        elif sort_this == 'price_low_to_high':
            sort_dict = price_low_to_high(books_dict)
        elif sort_this == 'price_high_to_low':
            sort_dict = price_high_to_low(books_dict)
        elif sort_this.capitalize() in language_list:
            sort_dict = {}
            for book_id, book in books_dict.items():
                if book.language == sort_this.capitalize():
                    sort_dict[book_id] = book
        else:
            sort_dict = books_dict

    q = request.args.get("q", default="", type=str)

    if q:
        for book_id, book in sort_dict.copy().items():
            if not any([s.lower() in book.title.lower() for s in q.split()]):
                sort_dict.pop(book_id, None)

    return render_template("books.html", query=q, books_list=sort_dict.values(), language_list=language_list)


# Sort name from a to z
def name_a_to_z(inventory_data):
    sort_dict = {}
    unsorted_dict = {}
    if inventory_data != {}:
        for book in inventory_data:
            unsorted_dict.update({book: inventory_data[book].title})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key=lambda kv: (kv[1], kv[0]))
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in inventory_data:
                sort_dict.update({id: inventory_data[id]})
    return sort_dict


# Sort name from z to a
def name_z_to_a(inventory_data):
    sort_dict = {}
    unsorted_dict = {}
    if inventory_data != {}:
        for book in inventory_data:
            unsorted_dict.update({book: inventory_data[book].title})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in inventory_data:
                sort_dict.update({id: inventory_data[id]})
    return sort_dict


# Sort price from low to high
def price_low_to_high(inventory_data):
    sort_dict = {}
    unsorted_dict = {}
    if inventory_data != {}:
        for book in inventory_data:
            unsorted_dict.update({book: float(inventory_data[book].price)})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key=lambda kv: (kv[1], kv[0]))
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in inventory_data:
                sort_dict.update({id: inventory_data[id]})
    return sort_dict


# Sort price from high to low
def price_high_to_low(inventory_data):
    sort_dict = {}
    unsorted_dict = {}
    if inventory_data != {}:
        for book in inventory_data:
            unsorted_dict.update({book: float(inventory_data[book].price)})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in inventory_data:
                sort_dict.update({id: inventory_data[id]})
    return sort_dict


"""  View Shopping Cart  """


@app.route('/cart')
@limiter.limit("10/second", override_defaults=False)
@login_required
def cart():
    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(404)

    user_id = user.user_id

    # Get cart items as a list of tuples, [(Book object, quantity)]
    cart_items = [(Book(*dbf.retrieve_book(items)), quantity)
                  for items, quantity in dbf.get_shopping_cart(user_id)]
    buy_count = len(cart_items)

    # Get total price
    total_price = 0
    for book, quantity in cart_items:
        total_price += book.price * quantity

    return render_template('cart.html', buy_count=buy_count, total_price=total_price, cart_items=cart_items)


"""    Add to Shopping Cart    """


# Add to cart
@app.route("/add-to-cart", methods=['POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required
def add_to_cart():
    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(404)

    user_id = user.user_id

    # Getting book_id and quantity to add
    book_id = request.form['book_id']
    buying_quantity = int(request.form['quantity'])

    book_data = dbf.retrieve_book(book_id)

    # Check if book exists in database
    if book_data is None:
        abort(400)  # Bad Request

    book = Book(*book_data)

    # Check if quantity entered is valid
    if buying_quantity is None:
        raise TypeError("Must have buying quantity")

    # stock left inside (basically customer can't buy more than this)
    max_quantity = book.stock

    # Ensure quantity is within correct range
    if buying_quantity < 0 or buying_quantity > max_quantity:
        abort(400)  # Bad Request

    # if book_id is found
    # Checking if book_id is already in cart
    cart_item = dbf.get_cart_item(user_id, book_id)

    # If book is not in customer's cart
    if cart_item is None:
        buying_quantity = min(max_quantity, buying_quantity)
        # Add to cart
        dbf.add_to_shopping_cart(user_id, book_id, buying_quantity)

    # Else book is already added in customer's cart
    else:
        # Update quantity
        buying_quantity += cart_item[2]
        buying_quantity = min(max_quantity, buying_quantity)
        dbf.update_shopping_cart(user_id, book_id, buying_quantity)

    # Flash success message to user
    flash("Book has been added to your cart")

    return redirect(request.referrer)  # Return to catalogue if book_id is not in inventory



""" Update Shopping Cart """


@app.route('/update-cart/<book_id>', methods=['POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required
def update_cart(book_id):
    # User is a Class
    user: User = flask_global.user

    # Update quantity
    book_quantity = int(request.form['quantity'])
    if book_quantity == 0:
        # No books in cart, delete cart
        return redirect(url_for("delete_buying_cart", book_id=book_id))
    else:
        # update book quantity
        dbf.update_shopping_cart(user.user_id, book_id, book_quantity)
        print('Update book quantity: ', str(book_quantity))

    return redirect(url_for('cart'))


""" Delete Cart """


@app.route("/delete-buying-cart/<book_id>", methods=['GET', 'POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required
def delete_buying_cart(book_id):
    user: User = flask_global.user
    # Get User ID
    user_id = user.user_id
    dbf.delete_shopping_cart_item(user_id, book_id)
    return redirect(url_for('cart'))


""" Customer Orders Page """


@app.route("/my-orders")
@limiter.limit("10/second", override_defaults=False)
@login_required
def my_orders():
    new_order = []
    confirm_order = []
    ship_order = []
    deliver_order = []
    canceled_order = []

    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(404)

    user_id = user.user_id

    # Get order details as a list of tuples(order_id, book_id, shipping option, order status)
    order_details = [Order(*item) for item in dbf.get_order_details(user_id)]

    for orders in order_details:
        if orders.order_pending == "Ordered":
            new_order.append(orders)
        elif orders.order_pending == "Confirmed":
            confirm_order.append(orders)
        elif orders.order_pending == "Shipped":
            ship_order.append(orders)
        elif orders.order_pending == "Delivered":
            deliver_order.append(orders)
        elif orders.order_pending == "Cancelled":
            canceled_order.append(orders)
    print(order_details)

    return render_template("user/my_orders.html")


""" Checkout Pages """


@app.route('/checkout', methods=['GET', 'POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required
def checkout():
    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(404)

    user_id = user.user_id

    # Get cart items as a list of tuples, [(Book object, quantity)]
    cart_items = [(Book(*dbf.retrieve_book(items)), quantity) for items, quantity in dbf.get_shopping_cart(user_id)]
    buy_count = len(cart_items)

    # Get total price
    total_price = 0
    for book, quantity in cart_items:
        total_price += book.price * quantity
    total_price = float(total_price)

    if request.method == 'POST':
        Orderform = OrderForm.OrderForm(request.form)

    return render_template("checkout.html", form=Orderform, total_price=total_price, buy_count=buy_count, cart_items=cart_items)


# Create Check out session with Stripe
@app.route('/create-checkout-session', methods=['POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required
def create_checkout_session():
    # User is a Class
    user: User = flask_global.user

    if user.role == "admin":
        abort(404)

    user_id = user.user_id

    # Get cart items as a list of tuples, [(Book object, quantity)]
    cart_items = [(Book(*dbf.retrieve_book(items)), quantity) for items, quantity in dbf.get_shopping_cart(user_id)]
    buy_count = len(cart_items)

    # Get total price
    total_price = 0
    for book, quantity in cart_items:
        total_price += book.price * quantity

    ship_method = 'Standard Delivery'
    print("creating checkout session...")

    Orderform = OrderForm.OrderForm(request.form)

    if request.method == 'POST' and Orderform.validate():
        if ship_method == 'Standard Delivery':  # Standard Delivery
            total_price += 5

        total_price *= 100
        total_price = int(total_price)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'sgd',
                        'product_data': {
                            'name': 'Books',
                        },
                        'unit_amount': total_price,
                    },
                    'quantity': 1,
                },
            ],
            payment_method_types=['card'],
            mode='payment',
            success_url='https://127.0.0.1:5000/order-confirm',
            cancel_url=request.referrer,
        )
        print(checkout_session.url)
        return redirect(checkout_session.url)
    else:
        flash(list(Orderform.errors.values())[0][0], 'warning')
        return redirect(request.referrer)


#
# show confirmation page upon successful payment
#
@app.route("/order-confirm")
@login_required
def orderconfirm():
    # User is a Class
    flask_global.user = get_user()
    user: User = flask_global.user

    if user.role == "admin":
        abort(404)

    user_id = user.user_id

    # Get cart items as a list of tuples, [(Book object, quantity)]
    cart_items = [(Book(*dbf.retrieve_book(items)), quantity)
                  for items, quantity in dbf.get_shopping_cart(user_id)]
    
    # Generate order id
    order_id = generate_uuid4()

    # Shipping Option
    shipping_option = 'Standard Delivery'

    # Order pending
    order_pending = 'Ordered'

    # Create order
    dbf.create_order_details(order_id, user_id, shipping_option, order_pending)

    # Create order items
    for item, quantity in cart_items:
        dbf.create_order_items(order_id, item.book_id, quantity)
        
        # Delete cart items
        dbf.delete_shopping_cart_item(user_id, item.book_id)
    

    return render_template("order_confirmation.html")


"""    Miscellaneous Pages    """

""" About Page """


@app.route("/about")
@limiter.limit("10/second", override_defaults=False)
def about():
    return render_template("about.html")


""" API Routes"""


@app.route("/api/user/login", methods=["POST"])
@limiter.limit("10/second", override_defaults=False)
@expects_json(LOGIN_SCHEMA)
def api_login():
    username = flask_global.data["username"]
    password = flask_global.data["password"]
    user_data = user_authenticate(username, password)
    time_check = datetime.datetime.now()
    if user_data is None:
        print("Check 1")
        if bool(dbf.retrieve_user_by_username(username)):
            print("Check 2")
            if bool(dbf.retrieve_failed_login(username)) == False:
                print("Check 3")
                dbf.create_failed_login(username, 1)
                return jsonify(status=1)
            if dbf.retrieve_failed_login(username)[1] == 5:
                print("Check 4")
                year = datetime.datetime.now().year
                month = datetime.datetime.now().month
                day = datetime.datetime.now().day
                hour = datetime.datetime.now().hour
                minute = datetime.datetime.now().minute
                second = datetime.datetime.now().second
                create_lockout_time(username, year, month, day, hour, minute, second)
                delete_failed_logins(username)
                print("Your account has been locked for 30 minutes")
                email = dbf.retrieve_email_by_username(username)
                subject = "ALERT - Account Locked"
                message = "Your account has been locked for 30 minutes, someone has tried to login to your account 5 times. If this was not you, change your password immediately."
                gmail_send(aws_decrypt(email), subject, message)
                return jsonify(status=1)
            if dbf.retrieve_failed_login(username)[1] < 5 and dbf.retrieve_failed_login(username)[1] > 0:
                print("Check 5")
                dbf.update_failed_login(username, dbf.retrieve_failed_login(username)[1] + 1)
                return jsonify(status=1)
        else:
            print("Check 6")
            return jsonify(status=1)
    user = User(*user_data)
    enable_2FA = bool(dbf.retrieve_2FA_token(user.user_id))
    if dbf.retrieve_lockout_time(username) is not None:
        year = dbf.retrieve_lockout_time(username)[1]
        month = dbf.retrieve_lockout_time(username)[2]
        day = dbf.retrieve_lockout_time(username)[3]
        hour = dbf.retrieve_lockout_time(username)[4]
        minute = dbf.retrieve_lockout_time(username)[5]
        second = dbf.retrieve_lockout_time(username)[6]
        lockout_time = datetime.datetime(year, month, day, hour, minute, second)
        print(time_check)
        print(lockout_time)
        difference_time = time_check - lockout_time
        print(difference_time)
        print(difference_time.seconds)
        if difference_time.seconds < 1800:
            print("Your account is still locked")
            return jsonify(status=1)
        else:
            dbf.delete_lockout_time(username)
            print("Your account is unlocked")
    if not enable_2FA:
        # Log user in
        flask_global.user = User(*user_data)
    else:
        # Go to 2FA
        add_cookie({"user_data": user_data, "user_id": user.user_id})

    # Status 0 for success
    return jsonify(status=0, enable_2FA=enable_2FA)


@app.route("/api/user/logout", methods=["POST"])
@limiter.limit("10/second", override_defaults=False)
def api_logout():
    flask_global.user = None
    return jsonify(status=0)  # Status 0 is success


@app.route("/api/books", methods=["GET"])
@limiter.limit("10/second", override_defaults=False)
def api_all_books():
    books_data = dbf.retrieve_inventory()
    if not books_data:
        return jsonify(message="There are no books."), 404

    output = [dict(book_id=row[0],
                   language=row[1],
                   genre=row[2],
                   title=row[3],
                   quantity=row[4],
                   price=row[5],
                   author=row[6],
                   description=row[7],
                   image=row[8]
                   )
              for row in books_data]
    return jsonify(output)


@app.route("/api/books/<book_id>", methods=["GET"])
@limiter.limit("10/second", override_defaults=False)
def api_single_book(book_id):
    if request.method == "GET":
        book_data = dbf.retrieve_book(book_id)
        if not book_data:
            return jsonify(message=f"There are no such books with id of {book_id}"), 404

        output = dict(book_id=book_data[0],
                      language=book_data[1],
                      genre=book_data[2],
                      title=book_data[3],
                      quantity=book_data[4],
                      price=book_data[5],
                      author=book_data[6],
                      description=book_data[7],
                      image=book_data[8]
                      )
        return jsonify(output)


@app.route('/api/admin/users', methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@expects_json(CREATE_USER_SCHEMA, ignore_for=["GET"])
@roles_required(["admin"], "api")
def api_users():
    if request.method == "GET":

        users_data = dbf.retrieve_these_customers(limit=0, offset=0)

        if not users_data:
            return jsonify(message="There are currently no users.")

        # Comment out personal info in case of excessive data exposure
        output = [dict(user_id=row[0],
                       username=row[1],
                       email=aws_decrypt(row[2]),
                       profile_pic=row[4],
                       role=row[5],
                       name=row[6],
                       )
                  for row in users_data]

        return jsonify(output)


@app.route('/api/admin/users/<user_id>', methods=["GET"])
@limiter.limit("10/second", override_defaults=False)
@roles_required(["admin"], "api")
def api_single_user(user_id):
    if request.method == "GET":
        user_data = dbf.retrieve_customer_detail(user_id)

        if user_data is None:
            return jsonify(message=f"There are no such user with id of {user_id}"), 404

        output = dict(user_id=user_data[0],
                      username=user_data[1],
                      email=user_data[2],
                      profile_pic=user_data[4],
                      role=user_data[5],
                      name=user_data[6],
                      )

        return jsonify(output)


# TODO: @SpeedFox198 @Miku add limit
@app.route("/api/reviews/<book_id>")
@limiter.limit("10/second", override_defaults=False)
def api_reviews(book_id):
    """ Returns a list of customer reviews in json format """
    # TODO: allow only a max len for book_id (just in case)
    # Retrieve customer reviews
    if flask_global.user and flask_global.user.role == "staff":
        reviews = [Review(*review).to_staff_dict() for review in dbf.retrieve_reviews(book_id)]
    else:
        reviews = [Review(*review).to_customer_dict() for review in dbf.retrieve_reviews(book_id)]
    ratings = dbf.retrieve_reviews_ratings(book_id)
    return jsonify(reviews=reviews, ratings=ratings)


@app.route('/api/reviews/<book_id>', methods=["DELETE"])
@limiter.limit("10/second", override_defaults=False)
@roles_required(["staff"], "api")
def api_delete_reviews(book_id):  # created delete route bc staff only can delete but everyone can read reviews
    user_id = request.args.get("user_id")
    deleted_review = dbf.retrieve_selected_review(book_id=book_id, user_id=user_id)
    deleted_review_username = dbf.retrieve_username_by_user_id(user_id)

    if user_id is None:
        return jsonify(status=1, error="Parameter 'user_id' is required."), 400

    if not deleted_review:
        return jsonify(status=1, error="Review does not exist"), 404

    dbf.delete_review(book_id=book_id, user_id=user_id)
    return jsonify(status=0, message=f"Review by {deleted_review_username} deleted!")


"""    Error Handlers    """


# Error handling page
@app.errorhandler(403)
def forbidden(e):
    return render_template("error/403.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html"), 404


@app.errorhandler(429)
def too_many_request(e):
    return render_template("error/429.html"), 429


@app.errorhandler(400)
def bad_request(error):
    if isinstance(error.description, jsonschema.ValidationError):
        original_error = error.description
        return jsonify(status=1, error=original_error.message), 400
    return render_template("error/400.html"), 400


@app.errorhandler(CSRFError)
def csrf_error(error):
    return render_template("error/csrf.html", error=error), 400


"""    Main    """
if __name__ == "__main__":
    app.run(debug=DEBUG, ssl_context=('cert.pem', 'key.pem'))  # Run app
