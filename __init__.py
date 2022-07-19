from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    make_response, g as flask_global, abort, jsonify, session  # TODO: session to be removed
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from SecurityFunctions import encrypt_info, decrypt_info, generate_uuid4, generate_uuid5, sign, verify
from db_fetch.customer import create_OTP
from session_handler import create_session, create_user_session, get_cookie_value, retrieve_user_session, USER_SESSION_NAME, NEW_COOKIES, EXPIRED_COOKIES
from models import User, Book, Review, UPLOAD_FOLDER as _PROFILE_PIC_PATH, BOOK_IMG_UPLOAD_FOLDER as _BOOK_IMG_PATH
import db_fetch as dbf
import os  # For saving and deleting images
from PIL import Image
from math import ceil
from OTP import generateOTP
from GoogleEmailSend import gmail_send
from csp import CSP
from api_schema import LOGIN_SCHEMA, CREATE_USER_SCHEMA
from sanitize import sanitize
import time
from flask_expects_json import expects_json
from jsonschema import ValidationError
from functools import wraps
from flask_wtf import CSRFProtect
import pyotp

from forms import (
    SignUpForm, LoginForm, ChangePasswordForm, ResetPasswordForm, ForgetPasswordForm,
    AccountPageForm, CreateUserForm, DeleteUserForm, AddBookForm, OrderForm, OTPForm, CreateReviewText
)

# CONSTANTS
# TODO @everyone: set to False when deploying
DEBUG = True  # Debug flag (True when debugging)
ACCOUNTS_PER_PAGE = 10  # Number of accounts to display per page (manage account page)
DOMAIN_NAME = "https://localhost:5000/"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
BANNED_CHARACTERS = ('{', '}', '<', '>', '(', ')', '&', '|', '$', '`', '!')  # For input whitelist

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_pyfile("config/app.cfg")  # Load config file
app.jinja_env.add_extension("jinja2.ext.do")  # Add do extension to jinja environment
BOOK_UPLOAD_FOLDER = _BOOK_IMG_PATH[1:]  # Book image upload folder
PROFILE_PIC_UPLOAD_FOLDER = _PROFILE_PIC_PATH[1:]  # Profile pic upload folder

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["30 per second"]
)


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


def add_cookie(cookies:dict):
    """ Adds cookies """
    if not isinstance(cookies, dict):
        raise TypeError("Expected dictionary")
    new_cookies:dict = flask_global.get(NEW_COOKIES, default={})
    new_cookies.update(cookies)
    flask_global.new_cookies = new_cookies


def remove_cookies(cookies:list):
    """ Remove cookies """
    if not isinstance(cookies, list):
        raise TypeError("Expected list")
    expired_cookies:list = flask_global.get(EXPIRED_COOKIES, default=[])
    expired_cookies.extend(cookies)
    flask_global.expired_cookies = expired_cookies


def login_required(message=None):
    """
    Put this in routes that user must be logged in to access with the @ sign
    For example:
    @app.route('/user/account/")
    @login_required()
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            """
            Logged in check here
            flash_message (str): Message to be flashed if user is not logged in 
            """
            if isinstance(flask_global.user, User):
                return func(*args, **kwargs)
            if message is None:
                flash("You must log in to access this page")
            elif message:
                flash(message)
            return redirect(url_for('login'))
        return decorated_function
    return decorator


def admin_check(mode="regular"):
    """
    Put this in routes that need admin check with the @ sign
    For example:
    @app.route('/admin/manage-account")
    @admin_check()
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
            if not isinstance(user, User) or not user.is_admin:
                if mode == "regular":
                    abort(404)
                elif mode == "api":
                    return jsonify(message="The resource you requested does not exist."), 404
            # Execute routes after
            return func(*args, **kwargs)
        return decorated_function
    return decorator


""" Before first request """


@app.before_first_request
def before_first_request():
    # Create admin if not in database
    if not dbf.admin_exists():
        # Admin details
        admin_id = generate_uuid5("admin")
        username = "admin"
        email = "admin@vsecurebookstore.com"
        password = "PASS{uNh@5h3d}"

        # Create admin
        dbf.create_admin(admin_id, username, email, password)


""" Before request """


@app.before_request
def before_request():
    flask_global.user = get_user()  # Get user


""" After request """##TODO: add SECURE in header

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
        renewed_user_session = create_user_session(user.user_id, user.is_admin)
        response.set_cookie(USER_SESSION_NAME, renewed_user_session, httponly=True, secure=True)

    # Default log user out
    else:
        # Remove session cookie
        expired_cookies.append(USER_SESSION_NAME)

    # Delete expired cookies
    for delete_this in expired_cookies:
        response.set_cookie(delete_this, "", expires=0, httponly=True, secure=True)

    # Set new cookies
    for name, value in new_cookies.items():
        response.set_cookie(name, create_session(value), httponly=True, secure=True)

    # Set CSP to prevent XSS
    response.headers["Content-Security-Policy"] = CSP

    return response


"""    Home Page    """

""" Home page """


@app.route("/")
@limiter.limit("10/second", override_defaults=False)
def home():
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

        add_cookie({"username": username, "email": email, "password": password})
        one_time_pass = generateOTP()
        print(one_time_pass)
        # Send email with OTP
        subject = "OTP for registration"
        message = "Do not reply to this email.\nPlease enter " + one_time_pass + " as your OTP to complete your registration."

        gmail_send(email, subject, message)
        add_cookie({"OTP": one_time_pass})
        return redirect(url_for("OTPverification"))

    # Render sign up page
    return render_template("user/sign_up.html", form=sign_up_form)


@app.route("/user/sign-up/OTPverification", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def OTPverification():
    email = get_cookie_value(request, "email")
    username = get_cookie_value(request, "username")
    password = get_cookie_value(request, "password")
    one_time_pass = get_cookie_value(request, "OTP")

    OTPformat = OTPForm(request.form)
    print(request.method)
    if request.method == "POST":
        OTPinput = OTPformat.otp.data
        if one_time_pass == OTPinput:
            # Create new customer
            user_id = generate_uuid5(username)  # Generate new unique user id for customer
            dbf.create_customer(user_id, username, email, password)

            # Create new user session to login (placeholder values were used to create user object)
            flask_global.user = User(user_id, "", "", "", "", 0, 0)

            # Return redirect with session cookie
            remove_cookies(["username", "email", "password", "OTP"])
            return redirect(url_for("home"))

        else:
            flash("Invalid OTP Entered! Please try again!")
            return redirect(url_for("OTPverification"))
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
    if request.method == "POST":
        if not login_form.validate():
            # Flash login error message
            flash("Your account and/or password is incorrect, please try again", "form-error")
        else:
            # Extract username/email and password from login form
            username = login_form.username.data.lower()
            password = login_form.password.data

            # Check username/email
            user_data = dbf.user_auth(username, password)

            # If user_data is not successfully retrieved (username/email/password is/are wrong)
            if user_data is None:

                # Flash login error message
                flash("Your account and/or password is incorrect, please try again", "form-error")

            # If login credentials are correct
            else:
                # Get user object
                user = User(*user_data)

                # Check if user enabled 2FA
                enable_2FA = bool(dbf.retrieve_2FA_token(user.user_id))
                if enable_2FA:
                    add_cookie({"user_data": user_data, "user_id": user.user_id})
                    return redirect(url_for("twoFA"))
                else:
                    # Create session to login
                    flask_global.user = user
                    return redirect(url_for("home"))

    # Render page's template
    return render_template("user/login.html", form=login_form)

@app.route("/user/login/2FA", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def twoFA():
    user_id = get_cookie_value(request, "user_id")
    user_data = get_cookie_value(request, "user_data")
    twoFA_code = dbf.retrieve_2FA_token(user_id[6])

    OTPformat = OTPForm(request.form)
    print(request.method)
    if request.method == "POST":
        twoFAinput = OTPformat.otp.data
        twoFAchecker = pyotp.TOTP(twoFA_code).verify(twoFAinput)
        try:
            if twoFAchecker:
                # Get user object
                user = User(*user_data)

                # Create session to login
                flask_global.user = user
                remove_cookies(["user_id", "user_data"])
                return redirect(url_for("home"))
            else:
                flash("Invalid OTP Entered! Please try again!")
                return redirect(url_for("twoFA"))
        except:
            return redirect(url_for("login"))
    else:
        return render_template("user/2FA.html", form=OTPformat)


""" Logout """


@app.route("/user/logout")
@limiter.limit("10/second", override_defaults=False)
def logout():
    flask_global.user = None
    next_page = request.args.get("from", default="", type=str)
    if next_page[:len(DOMAIN_NAME)] != DOMAIN_NAME:
        next_page = url_for("home")
    return redirect(next_page)


""" Forgot password page """  ### TODO: work on this SpeedFox198


@app.route("/user/password/forget", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required()
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

            with shelve.open("database") as db:
                email_to_user_id = retrieve_db("EmailToUserID", db)

            if email in email_to_user_id:
                # Generate token
                token = url_serialiser.dumps(email, salt=app.config["PASSWORD_FORGET_SALT"])

                # Send message to email entered
                subject = "Reset Your Password"
                message = "Do not reply to this email.\nPlease click on ths link to reset your password." + url_for("password_reset", token=token, _external=True)

                gmail_send(email, subject, message)

                if DEBUG: print(f"Sent email to {email}")
            else:
                if DEBUG: print(f"No user with email: {email}")

            flash(f"Verification email sent to {email}")
            return redirect(url_for("login"))

    return render_template("user/password/password_forget.html", form=forget_password_form)

#In case maybe google authenticator

@app.route("/user/account/google_authenticator", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def google_authenticator():
    # User is a Class
    user: User = flask_global.user

    if not isinstance(user, User):
        return redirect(url_for("login"))
    elif user.is_admin:
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
            dbf.create_2FA_token(user.user_id[6], secret_token)
            print(dbf.retrieve_2FA_token(user.user_id[6]))
            remove_cookies(["token"])
            return redirect(url_for("account"))
        else:
            flash("Invalid OTP Entered! Please try again!")
            return redirect(url_for("google_authenticator"))
    else:
        return render_template("user/google_authenticator.html", form=OTP_Test, secret_token = secret_token)

@app.route("/user/account/google_authenticator_disable", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def google_authenticator_disable():
    # User is a Class
    user: User = flask_global.user

    if not isinstance(user, User):
        return redirect(url_for("login"))
    elif user.is_admin:
        abort(403)

    dbf.delete_2FA_token(user.user_id[6])
    flash("2FA has been disabled")
    return redirect(url_for("account"))

""" Reset password page """  ### TODO: work on this SpeedFox198


@app.route("/user/password/reset/<token>", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def password_reset(token):
    # Get user
    guest = get_user()

    # Only Guest will forget password
    if session["UserType"] != "Guest":
        return redirect(url_for("home"))

    # Get email from token
    try:
        email = url_serialiser.loads(token, salt=app.config["PASSWORD_FORGET_SALT"], max_age=TOKEN_MAX_AGE)
    except BadData as err:  # Token expired or Bad Signature
        if DEBUG: print("Invalid Token:", repr(err))  # print captured error (for debugging)
        return redirect(url_for("invalid_link"))

    with shelve.open("database") as db:
        email_to_user_id = retrieve_db("EmailToUserID", db)
        customers_db = retrieve_db("Customers", db)
        guests_db = retrieve_db("Guests", db)

        # Get user
        try:
            customer = customers_db[email_to_user_id[email]]
        except KeyError:
            if DEBUG: print("No user with email:", email)  # Account was deleted
            return redirect(url_for("invalid_link"))

        # Render form
        reset_password_form = ResetPasswordForm(request.form)
        if request.method == "POST":
            if not reset_password_form.validate():
                session["DisplayFieldError"] = True
            else:
                # Extract password
                new_password = reset_password_form.new_password.data

                # Reset Password
                customer.set_password(new_password)
                if DEBUG: print(f"Reset password for: {customer}")

                # Delete guest account
                guests_db.remove(guest.get_user_id())
                if DEBUG: print(f"Deleted: {guest}")

                # Log in customer
                session["UserID"] = customer.get_user_id()
                session["UserType"] = "Customer"
                if DEBUG: print(f"Logged in: {customer}")

                # Safe changes to database
                db["Customers"] = customers_db
                db["Guests"] = guests_db

                # Flash message and redirect to account page
                flash("Password has been successfully set")
                return redirect(url_for("account"))

    return render_template("user/password/password_reset.html", form=reset_password_form, email=email)


""" Change password page """


@app.route("/user/password/change", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required()
def password_change():
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
            if not dbf.user_auth(user.username, current_password):
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
                dbf.change_password(user.user_id, new_password)

                # Sign user out (proccess will be done in @app.after_request)
                flask_global.user = None

                # Flash success message and redirect
                flash("Password has been changed successfully, please login again with your new password.")
                return redirect(url_for("login"))

    return render_template("user/password/password_change.html", form=change_password_form)

# Needs to be changed
# TODO: needs to change
# NOTE: sending email is done by Royston
"""Verification page in case"""


# Send verification link page
@app.route("/user/verify")
def verify_send():
    # Get user
    user = get_user()

    # If not customer or email is verified
    if not isinstance(user, Customer) or user.is_verified():
        return redirect(url_for("home"))

    # Configure noreplybbb02@gmail.com
    # app.config.from_pyfile("config/noreply_email.cfg")
    # mail.init_app(app)

    # Get email
    email = user.get_email()

    # Generate token
    token = url_serialiser.dumps(email, salt=app.config["VERIFY_EMAIL_SALT"])

    # Send message to email entered
    msg = Message(subject="Verify Email",
                  sender=("BrasBasahBooks", "noreplybbb02@gmail.com"),
                  recipients=[email])
    link = url_for("verify", token=token, _external=True)
    msg.html = f"Click <a href='{link}'>here</a> to verify your email.<br />(Link expires after 15 minutes)"
    mail.send(msg)

    flash(f"Verification email sent to {email}")
    return redirect(url_for("account"))

"""    User Pages    """

""" View account page """


@app.route("/user/account", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
@login_required()
def account():
    # Get current user
    user: User = flask_global.user

    # If user is not logged in
    if not user:
        return redirect(url_for("login"))

    if user.is_admin:
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
                    profile_pic_filename = f"{user.user_id}_{profile_pic.filename}"
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
    twoFA_enabled = bool(dbf.retrieve_2FA_token(user.user_id[6]))
    print(twoFA_enabled)
    return render_template("user/account.html",
                           form=account_page_form,
                           picture_path=user.profile_pic,
                           username=user.username,
                           email=user.email,
                           phone_no=user.phone_no,
                           twoFA_enabled=twoFA_enabled)


"""    Admin Pages    """


# Manage accounts page
@app.route("/admin/manage-accounts", methods=["GET", "POST"])
@admin_check()
def manage_accounts():
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
            return redirect(f"{url_for('manage_accounts')}?page={active_page}")

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
            elif dbf.email_exists(email):
                errors["DisplayFieldError"] = errors["CreateUserEmailError"] = True
                flash("Email already registered", "create-user-email-error")

            # If username and email are not used, create customer
            else:
                user_id = generate_uuid5(username)  # Generate new unique user id for customer
                dbf.create_customer(user_id, username, email, password)
                flash(f"Created new customer: {username}")
                return redirect(f"{url_for('manage_accounts')}?page={active_page}")

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
        active_page=active_page, page_list=page_list,
        prev_page=prev_page, next_page=next_page,
        first_page=1, last_page=last_page,
        entries_range=entries_range, total_entries=customer_count,
        form_trigger=form_trigger,
        create_user_form=create_user_form,
        delete_user_form=delete_user_form
    )


@app.route('/admin/inventory')
@admin_check()
def inventory():
    inventory_data = dbf.retrieve_inventory()

    # Create book object and store in inventory
    book_inventory = [Book(*data) for data in inventory_data]
    return render_template('admin/inventory.html', count=len(book_inventory), books_list=book_inventory)


def allowed_file(filename):
    # Return true if there is an extension in file, and its extension is in the allowed extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


lang_list = [('', 'Select'), ('English', 'English'), ('Chinese', 'Chinese'), ('Malay', 'Malay'), ('Tamil', 'Tamil')]
category_list = [('', 'Select'), ('Action & Adventure', 'Action & Adventure'), ('Classic', 'Classic'),
                 ('Comic', 'Comic'), ('Detective & Mystery', 'Detective & Mystery')]


@app.route('/admin/add-book', methods=['GET', 'POST'])
@admin_check()
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
            book_img_filename = f"{book_id}_{secure_filename(book_img.filename)}"  # Generate unique name string for files
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

    return render_template('admin/add_book.html', form=add_book_form)


@app.route('/update-book/<book_id>/', methods=['GET', 'POST'])
@admin_check()
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
            book_img_filename = f"{generate_uuid4()}_{secure_filename(book_img.filename)}"  # Generate unique name string for files
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


@app.route('/delete-book/<book_id>/', methods=['POST'])
@admin_check()
def delete_book(book_id):
    # Deletes book and its cover image
    selected_book = Book(*dbf.retrieve_book(book_id)[0])
    book_cover_img = selected_book.cover_img[1:]  # Strip the leading slash for relative path
    print(book_cover_img)
    if os.path.isfile(book_cover_img):
        os.remove(book_cover_img)
    else:
        print("Book cover does not exist.")
    dbf.delete_book(book_id)
    return redirect(url_for('inventory'))


@app.route("/admin/manage-orders")
@admin_check()
def manage_orders():
    return "sorry for removing your code"


"""    Books Pages    """


# Wei Ren was here. hello.
# ?? wtf

@app.route("/book/<book_id>", methods=["GET", "POST"])
@limiter.limit("10/second", override_defaults=False)
def book_info(book_id):
    # Get book details
    book_data = dbf.retrieve_book(book_id)

    # Abort 404 if book_id does not exist
    if book_data is None:
        abort(404)

    book = Book(*book_data)

    return render_template("book_info.html", book=book)


# TODO: @Miku @SpeedFox198 work on this (perhaps we not using this?)
@app.route("/my-orders/review/<order_id>", methods=["GET", "POST"])
def book_review(id, reviewPageNumber):
    # Get current user
    user: User = flask_global.user

    # If user is not logged in
    if not user:
        return redirect(url_for("login"))

    if user.is_admin:
        abort(404)

    createReview = CreateReviewText(request.form)


""" Search Results Page """


@app.route("/books/<sort_this>")
@limiter.limit("10/second", override_defaults=False)
def books(sort_this):
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
            sort_dict = filter_language(sort_this)
        else:
            sort_dict = books_dict

    q = request.args.get("q", default="", type=str)

    if q:
        for book_id, book in sort_dict.copy().items():
            if not any([s.lower() in book.title.lower() for s in q.split()]):
                sort_dict.pop(book_id, None)

    return render_template("books.html", query=q, books_list=sort_dict.values(), language_list=language_list)


def filter_language(language):
    books = {}
    books_dict = {}
    inventory_data = dbf.retrieve_inventory()

    for book in inventory_data:
        if inventory_data[book].language == language:
            books.update({book: inventory_data[book]})
    return books


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


"""    Start of Cart Pages    """


# TODO: SpeedFox198 Marence: maybe shldn't abort 400, and shld reply with {"error":1}
# Add to cart
@app.route("/add-to-cart", methods=['POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required("You need to be logged in to purchase items")
def add_to_cart():
    # User is a Class
    user: User = flask_global.user

    if user.is_admin:
        abort(404)

    user_id = user.user_id

    # Getting book_id and quantity to add
    book_id = request.form['book_id']
    buying_quantity = request.form['quantity']

    # Check if quantity entered is valid
    try:
        buying_quantity = int(buying_quantity)
    except:
        abort(400)  # Bad Request

    # Ensure quantity is within correct range
    if buying_quantity < 0 or buying_quantity > 10000:
        abort(400)  # Bad Request

    book_data = dbf.retrieve_book(book_id)

    # Check if book exists in database
    if book_data is None:
        abort(400)  # Bad Request

    book = Book(*book_data)

    # if book_id is found
    # Checking if book_id is already in cart
    cart_item = dbf.get_cart_item(user_id, book_id)

    # stock left inside (basically customer can't buy more than this)
    max_quantity = book.stock

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


""" View Shopping Cart"""


@app.route('/cart')
@limiter.limit("10/second", override_defaults=False)
@login_required()
def cart():
    # User is a Class
    user: User = flask_global.user

    if user.is_admin:
        abort(404)

    user_id = user.user_id

    # Get cart items as a list of tuples, [(Book object, quantity)]
    cart_items = [(Book(*dbf.retrieve_book(items)), quantity) for items, quantity in dbf.get_shopping_cart(user_id)]
    buy_count = len(cart_items)

    # Get total price
    total_price = 0
    for book, quantity in cart_items:
        total_price += book.price * quantity

    return render_template('cart.html', buy_count=buy_count, total_price=total_price, cart_items=cart_items)


""" Update Shopping Cart """


@app.route('/update-cart/<book_id>', methods=['POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required()
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
    # cart_dict = cart_db['Cart']
    # buy_cart = cart_dict[user_id][0]
    # book_quantity = int(request.form['quantity'])
    # if book_quantity == 0:
    #     print('Oh no need to delete')
    #     delete_buying_cart(id)
    # else:
    #     buy_cart[id] = book_quantity
    #     print(buy_cart)
    #     cart_dict[user_id][0] = buy_cart
    #     cart_db['Cart'] = cart_dict
    #     print(cart_dict, 'updated database')
    #     cart_db.close()
    # return redirect(request.referrer)


""" Delete Cart """


@app.route("/delete-buying-cart/<book_id>", methods=['GET', 'POST'])
@limiter.limit("10/second", override_defaults=False)
@login_required()
def delete_buying_cart(book_id):
    user: User = flask_global.user
    # Get User ID
    user_id = user.user_id
    dbf.delete_shopping_cart(user_id, book_id)
    return redirect(url_for('cart'))


"""    Order Pages    """

""" Customer Orders Page """


@app.route("/my-orders")
@limiter.limit("10/second", override_defaults=False)
@login_required()
def my_orders():
    # User is a Class
    user: User = flask_global.user

    if user.is_admin:
        abort(404)

    user_id = user.user_id

    # Get orders

    return render_template('my-orders.html')
# def my_orders():
#     db_order = []
#     new_order = []
#     confirm_order = []
#     ship_order = []
#     deliver_order = []
#     canceled_order = []
#     books_dict = {}
#     try:
#         db = shelve.open('database')
#         books_dict = db['Books']
#         db_order = db['Order']
#         print(db_order, "orders in database")
#         db.close()
#     except:
#         print("There might not have any orders as of now.")
#     for order in db_order:
#         print(order.get_name(), order.get_rent_item())
#         if order.get_order_status() == 'Ordered':
#             new_order.append(order)
#         elif order.get_order_status() == 'Confirmed':
#             confirm_order.append(order)
#         elif order.get_order_status() == 'Shipped':
#             ship_order.append(order)
#         elif order.get_order_status() == 'Delivered':
#             deliver_order.append(order)
#         elif order.get_order_status() == 'Canceled':
#             canceled_order.append(order)
#         else:
#             print(order, "Wrong order status")

#     # display from most recent to the least
#     db_order = list(reversed(db_order))
#     new_order = list(reversed(new_order))
#     confirm_order = list(reversed(confirm_order))
#     ship_order = list(reversed(ship_order))
#     deliver_order = list(reversed(deliver_order))
#     canceled_order = list(reversed(canceled_order))

#     print("canceled_order: ", canceled_order)
#     return render_template('user/my_orders.html', all_order=db_order, new_order=new_order, \
#                            confirm_order=confirm_order, ship_order=ship_order, deliver_order=deliver_order,
#                            canceled_order=canceled_order, \
#                            books_dict=books_dict)


"""    Miscellaneous Pages    """

""" About Page """


@app.route("/about")
@limiter.limit("10/second", override_defaults=False)
def about():
    return render_template("about.html")


""" API Routes"""


@app.route("/api/login", methods=["POST"])
@limiter.limit("10/second", override_defaults=False)
@expects_json(LOGIN_SCHEMA)
def api_login():
    username = flask_global.data["username"]
    password = flask_global.data["password"]
    user_data = dbf.user_auth(username, password)
    if user_data is None:
        return jsonify(status=1)    # Status 1 for not success

    flask_global.user = User(*user_data)

    return jsonify(status=0)        # Status 0 is success


@app.route("/api/books/all", methods=["GET"])
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
@admin_check("api")
def api_users():
    if request.method == "GET":

        users_data = dbf.retrieve_these_customers(limit=0, offset=0)

        if not users_data:
            return jsonify(message="There are currently no users.")

        # Comment out personal info in case of excessive data exposure
        output = [dict(user_id=row[0],
                       username=row[1],
                       email=row[2],
                       # password=row[3],
                       profile_pic=row[4],
                       is_admin=row[5],
                       name=row[6],
                       # credit_card_no=row[7],
                       # address=row[8],
                       # phone_no=row[9],
                       )
                  for row in users_data]

        return jsonify(output)

    # elif request.method == "POST":
    #     if admin_check("api"):
    #         return admin_check("api")

    #     username = flask_global.data['username']
    #     email = flask_global.data['email']
    #     password = flask_global.data['password']

    #     if dbf.username_exists(username):
    #         return jsonify(message="The username you entered already exists. Please enter another username."), 400

    #     if dbf.email_exists(email):
    #         return jsonify(message="The email already been registered. Please enter another email."), 400

    #     dbf.create_customer(generate_uuid5(username), username, email, password)
    #     return jsonify("User created!"), 200


@app.route('/api/admin/users/<user_id>', methods=["GET"])
@limiter.limit("10/second", override_defaults=False)
@admin_check("api")
def api_single_user(user_id):
    if request.method == "GET":
        user_data = dbf.retrieve_customer_detail(user_id)

        if user_data is None:
            return jsonify(message=f"There are no such user with id of {user_id}"), 404

        output = dict(user_id=user_data[0],
                      username=user_data[1],
                      email=user_data[2],
                      # password=user_data[3],
                      profile_pic=user_data[4],
                      is_admin=user_data[5],
                      name=user_data[6],
                      # credit_card_no=user_data[7],
                      # address=user_data[8],
                      # phone_no=user_data[9],
                      )

        return jsonify(output)

    #elif request.method == "DELETE":
    #    if admin_check("api"):
    #        return admin_check("api")
    #
    #    deleted_customer = dbf.delete_customer(user_id)
    #    if deleted_customer:
    #        deleted_customer = User(*deleted_customer)
    #        customer_profile_pic = deleted_customer.profile_pic[1:]
    #        print(customer_profile_pic)
    #        if os.path.isfile(customer_profile_pic):
    #            os.remove(customer_profile_pic)
    #        else:
    #            print("Profile pic does not exist")
    #        return jsonify(message=f"Deleted customer: {deleted_customer.username}")
    #    else:
    #        return jsonify(error="Customer does not exist")


# TODO: @SpeedFox198 @Miku add limit
@app.route("/api/reviews/<book_id>")
@limiter.limit("10/second", override_defaults=False)
def api_reviews(book_id):
    """ Returns a list of customer reviews in json format """
    # TODO: allow only a max len for book_id (just in case)
    # Retrieve customer reviews
    reviews = [Review(*review).to_dict() for review in dbf.retrieve_reviews(book_id)]
    ratings = dbf.retrieve_reviews_ratings(book_id)
    return jsonify(reviews=reviews, ratings=ratings)


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
    if isinstance(error.description, ValidationError):
        original_error = error.description
        # if '^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])$' in original_error.message:  # Hacky custom message lol
        #     return jsonify(error="The password does not match the password complexity policy (At least 1 upper case letter, 1 lower case letter, 1 digit and 1 symbol)")
        return jsonify(status=1, error=original_error.message), 400
    return render_template("error/400.html"), 400


"""    Main    """

if __name__ == "__main__":
    app.run(debug=DEBUG, ssl_context=('cert.pem', 'key.pem'))  # Run app
