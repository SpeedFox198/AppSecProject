# Import modules
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadData
from werkzeug.utils import secure_filename
from typing import Union, Dict
from PIL import Image
import math
import shelve
import os
import stripe
import datetime
import db_fetch as dbf
from session_handler import create_user_session, retrieve_session
from user import Admin

# Import classes
import Book, Cart as c
from users_old import GuestDB, Guest, Customer, Admin
from forms import (
    SignUpForm, LoginForm, ChangePasswordForm, ResetPasswordForm, ForgetPasswordForm,
    AccountPageForm, CreateUserForm, DeleteUserForm, AddBookForm, OrderForm
)


# CONSTANTS
DEBUG = True            # Debug flag (True when debugging)
TOKEN_MAX_AGE = 900     # Max age of token (15 mins)
ACCOUNTS_PER_PAGE = 10  # Number of accounts to display per page (manage account page)

# For image file upload (Eden having issues with this)
#BOOK_IMG_UPLOAD_FOLDER = '1566-App-dev-Team-2/static/img/books'
# For image file upload Everyone
BOOK_IMG_UPLOAD_FOLDER = 'static/img/books'
PROFILE_PIC_UPLOAD_FOLDER = "static/img/profile-pic"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file
app.config['UPLOAD_FOLDER'] = BOOK_IMG_UPLOAD_FOLDER  # Set upload folder
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # Set maximum file upload limit (4MB)
app.jinja_env.add_extension("jinja2.ext.do")  # Add do extension to jinja environment
# testing mode
stripe.api_key = 'sk_test_51KPNSMLcZKZGRW8Qkzf58oSvjzX5LxhHQLBPZkmlCijcfXdhdXtXTTDXf3FqMHd1fd3kWcvxktgp7cj0ka4uSmzS00ilLjWTBX' # Stripe API Key
# live mode
# stripe.api_key = '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'


# Serialiser for generating tokens
url_serialiser = URLSafeTimedSerializer(app.config["SECRET_KEY"])

app.config["MAIL_SERVER"] = "smtp.gmail.com" # using gmail
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "noreplybbb02@gmail.com" # using gmail
app.config["MAIL_PASSWORD"] = "Hs!3ck;qnCSyyz^8-p"
mail = Mail(app)

#mail = Mail()  # Mail object for sending emails


"""|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|"""
"""|---------- Jabriel's Codes ----------|"""
"""|_____________________________________|"""


"""    General Funtions    """

######################################################################### TODO: remove cuz will be using SQL
# Added type hintings as I needed my editor to recognise the type
def retrieve_db(key, db, value=None):
    pass


def get_user():
    """ Returns user if cookie is correct, else returns None """

    # Get session cookie from request
    session_cookie = request.cookies.get("session")
    user_session = retrieve_session(session_cookie)

    # Return None
    if user_session is None:
        return

    # Retrieve user id from session
    user_id = user_session.user_id

    # Retrieve user data from database
    user_data = dbf.retrieve_user(user_id)

    # If user is not found
    if user_data is None:
        return

    # Create and return user object
    return Admin(*user_data)


"""    Before Request    """

# Before first request
@app.before_first_request
def before_first_request():

    # Create admin if not in database
    if not dbf.admin_exists():

        # Admin details
        admin_id = generate_id()
        username = "admin"
        email = "admin@vsecurebookstore.com"
        password = "PASS{uNh@5h3d}"

        # Create admin
        dbf.create_admin(admin_id, username, email, password)


# Before request
@app.before_request
def before_request():
    pass            ######################## TODO: might use this (idk?)


"""    Login/Sign-up Pages    """

# Sign up page
@app.route("/user/sign-up", methods=["GET", "POST"])
def sign_up():

    # Get sign up form
    sign_up_form = SignUpForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST":
        if not sign_up_form.validate():
            if DEBUG: print("Sign-up: form field invalid")
            session["DisplayFieldError"] = True
            return render_template("user/sign_up.html", form=sign_up_form)

        # Extract data from sign up form
        username = sign_up_form.username.data
        email = sign_up_form.email.data.lower()
        password = sign_up_form.password.data

        # Create new user

        # Ensure that email and username are not registered yet
        if dbf.username_exists(username):
            session["DisplayFieldError"] = session["SignUpUsernameError"] = True
            flash("Username taken", "sign-up-username-error")
            return render_template("user/sign_up.html", form=sign_up_form)

        elif dbf.email_exists(email):
            session["DisplayFieldError"] = session["SignUpEmailError"] = True
            flash("Email already registered", "sign-up-email-error")
            return render_template("user/sign_up.html", form=sign_up_form)

        # Create new customer
        user_id = generate_id()  # Generate new unique user id for customer
        dbf.create_customer(user_id, username, email, password)

        # Create session to login
        new_session = create_user_session(user_id)
        response = make_response(redirect(url_for("verify_send")))
        response.set_cookie("session", new_session)

        # Return redirect with session cookie
        return response

    # Render page
    return render_template("user/sign_up.html", form=sign_up_form)


# Login page
@app.route("/user/login", methods=["GET", "POST"])
def login():

    # Get user
    user = get_user()

    # If user is already logged in
    if user is not None:
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

            # If user_data is not succesfully retrieved (username/email/password is/are wrong)
            if user_data is None:
                # Flash login error message
                flash("Your account and/or password is incorrect, please try again", "form-error")
                return render_template("user/login.html", form=login_form)

            # If login credentials are correct
            else:
                # Get user id
                user = Admin(*user_data)
                user_id = user.user_id

                # Create session to login
                new_session = create_user_session(user_id)
                response = make_response(redirect(url_for("home")))
                response.set_cookie("session", new_session)

    # Render page
    return render_template("user/login.html", form=login_form)


# Logout
@app.route("/user/logout")
def logout():
    if session["UserType"] != "Guest":
        if DEBUG: print("Logout:", get_user())
    return redirect(url_for("home"))


"""    Account Pages    """

# Forgot password page
@app.route("/user/password/forget", methods=["GET", "POST"])
def password_forget():

    # Get user
    user = get_user()

    # Only Guest will forget password
    if session["UserType"] != "Guest":
        return redirect(url_for("home"))

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
                msg = Message(subject="Reset Your Password",
                            sender=("BrasBasahBooks", "noreplybbb02@gmail.com"),
                            recipients=[email])
                link = url_for("password_reset", token=token, _external=True)
                msg.html = render_template("emails/_password_reset.html", link=link)
                mail.send(msg)
                if DEBUG: print(f"Sent email to {email}")
            else:
                if DEBUG: print(f"No user with email: {email}")

            flash(f"Verification email sent to {email}")
            return redirect(url_for("login"))

    return render_template("user/password/password_forget.html", form=forget_password_form)


# Reset password page
@app.route("/user/password/reset/<token>", methods=["GET", "POST"])
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

# Change password page
@app.route("/user/password/change", methods=["GET", "POST"])
def password_change():
    # Get current user
    user = get_user()

    # If user is not logged in
    if session["UserType"] == "Guest":
        return redirect(url_for("login"))

    # Get change password form
    change_password_form = ChangePasswordForm(request.form)

    # Validate sign up form if request is post
    if request.method == "POST":
        if not change_password_form.validate():
            session["DisplayFieldError"] = True
        else:
            # Extract data from sign up form
            current_password = change_password_form.current_password.data
            new_password = change_password_form.new_password.data

            if not user.verify_password(current_password):
                flash("Your password is incorrect, please try again", "form-error")
            else:
                with shelve.open("database") as db:

                    # Retrieve user database
                    key = session["UserType"] + "s"
                    user_db = retrieve_db(key, db)

                    # Get user and set password
                    user = user_db[session["UserID"]]
                    user.set_password(new_password)

                    # Save changes to database
                    db[key] = user_db

                    if DEBUG: print("Password changed for", user)
                    return redirect(url_for("account"))

    return render_template("user/password/password_change.html", form=change_password_form)


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


########################################################### TODO: incomplete! (verified email does nothing much rn)
# Verify email page
@app.route("/user/verify/<token>")
def verify(token):

    # Get email from token
    try:
        email = url_serialiser.loads(token, salt=app.config["VERIFY_EMAIL_SALT"], max_age=TOKEN_MAX_AGE)
    except BadData as err:  # Token expired or Bad Signature
        if DEBUG: print("Invalid Token:", repr(err))  # print captured error (for debugging)
        return redirect(url_for("invalid_link"))

    with shelve.open("database") as db:
        email_to_user_id = retrieve_db("EmailToUserID", db)
        customers_db = retrieve_db("Customers", db)

        # Get user
        try:
            user = customers_db[email_to_user_id[email]]
        except KeyError:
            if DEBUG: print("No user with email:", email)  # Account was deleted
            return redirect(url_for("invalid_link"))

        # Verify email
        if not user.is_verified():
            user.verify()
        else:  # Email was alreadyt verified
            if DEBUG: print(email, "is already verified")
            return redirect(url_for("invalid_link"))

        # Safe changes to database
        db["Customers"] = customers_db

    return render_template("user/verify/verify.html", email=email)


# Invalid link page
@app.route("/invalid-link")
def invalid_link():
    return render_template("user/verify/invalid_link.html")


"""    User Pages    """

######################################################################### TODO: cater to admin acc
# View account page
@app.route("/user/account", methods=["GET", "POST"])
def account():
    # Get current user
    user = get_user()

    # If user is not logged in
    if session["UserType"] == "Guest":
        return redirect(url_for("login"))

    # Get account page form
    account_page_form = AccountPageForm(request.form)

    # Validate account page form if request is post
    if request.method == "POST":

        if not account_page_form.validate():
            name = account_page_form.name
            gender = account_page_form.gender
            picture = account_page_form.picture

            # Flash error message (only flash the 1st error)
            error = name.errors[0] if name.errors else picture.errors[0] if picture.errors else gender.errors[0]
            flash(error, "error")
        else:
            # Flash success message
            flash("Account settings updated successfully")

            # Extract email and password from sign up form
            name = " ".join(account_page_form.name.data.split())
            gender = account_page_form.gender.data

            # Check files submitted for profile pic
            if "picture" in request.files:
                file = request.files["picture"]
                if file and allowed_file(file.filename):
                    file.save(os.path.join(PROFILE_PIC_UPLOAD_FOLDER, user.get_user_id()+".png"))
                else:
                    file = None
            else:
                file = None

            with shelve.open("database") as db:
                # Get Customers
                customers_db = retrieve_db("Customers", db)
                user = customers_db[session["UserID"]]

                # Set name and gender
                user.set_name(name)
                user.set_gender(gender)

                # If image uploaded, set profile pic
                if file is not None:
                    user.set_profile_pic()

                # Save changes to database
                db["Customers"] = customers_db

        # Redirect to prevent form resubmission
        return redirect(url_for("account"))

    # Set username and gender to display
    account_page_form.name.data = user.get_name()
    account_page_form.gender.data = user.get_gender()
    return render_template("user/account.html",
                           form=account_page_form,
                           display_name=user.get_display_name(),
                           picture_path=user.get_profile_pic(),
                           username=user.get_username(),
                           email=user.get_email())


@app.route("/search-result/<sort_this>")
def search_result(sort_this):
    sort_dict = {}
    books_dict = {}
    language_list = []
    try:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()
        for book in books_dict:
            language = books_dict[book].get_language()
            if language not in language_list:
                language_list.append(language)
                print(language_list)

    except:
        print("There are no books")

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
            if not any([s.lower() in book.get_title().lower() for s in q.split()]):
                sort_dict.pop(book_id, None)

    return render_template("all_books.html", books_dict=books_dict, sort_dict=sort_dict, language_list=language_list)


"""    Admin Pages    """

# Manage accounts page
@app.route("/admin/manage-accounts", methods=["GET", "POST"])
def manage_accounts():
    admin = get_user()

    # If user is not admin
    if not isinstance(admin, Admin):
        return redirect(url_for("home"))

    # Get page number
    active_page = request.args.get("page", default=1, type=int)

    # Get sign up form
    create_user_form = CreateUserForm(request.form)
    delete_user_form = DeleteUserForm(request.form)

    form_trigger = "addUserButton"  # id of form to trigger on page load

    # Validate sign up form if request is post
    if request.method == "GET":
        form_trigger = ""
    else:
        if delete_user_form.validate() and delete_user_form.user_id.data:
            form_trigger = ""

            # Delete selected user
            user_id = delete_user_form.user_id.data

            with shelve.open("database") as db:

                # Get Customers, Admins, UsernameToUserID, EmailToUserID
                customers_db = retrieve_db("Customers", db)
                admins_db = retrieve_db("Admins", db)
                username_to_user_id = retrieve_db("UsernameToUserID", db)
                email_to_user_id = retrieve_db("EmailToUserID", db)
            
                try:
                    del_user = customers_db[user_id]
                except KeyError:
                    if not admin.is_master():
                        del_user = None
                    else:
                        try:
                            del_user = admins_db[user_id]
                        except KeyError:
                            del_user = None
                        else:
                            user_type = "A"
                else:
                    user_type = "C"

                if del_user is None:
                    flash("No changes were made", "warning")
                else:
                    # Delete user
                    {"C":customers_db, "A":admins_db}[user_type].pop(user_id, None)
                    username_to_user_id.pop(del_user.get_username(), None)
                    email_to_user_id.pop(del_user.get_email(), None)
                    if DEBUG: print(f"Delete User: deleted {del_user}")

                    # Save changes
                    db["Customers"] = customers_db
                    db["Admins"] = admins_db
                    db["UsernameToUserID"] = username_to_user_id
                    db["EmailToUserID"] = email_to_user_id

                    # Redirect to prevent form resubmission
                    flash(f"Deleted {del_user.__class__.__name__.lower()}: {del_user.get_username()}")
                    return redirect(f"{url_for('manage_accounts')}?page={active_page}")

        elif not create_user_form.validate():
            if DEBUG: print("Create User: form field invalid")
            session["DisplayFieldError"] = True
        else:
            # Extract data from sign up form
            if admin.is_master():
                user_type = create_user_form.user_type.data
            else:
                user_type = "C"  # non-master admins can only create customers
            username = create_user_form.username.data
            email = create_user_form.email.data.lower()
            password = create_user_form.password.data

            # Create new user
            with shelve.open("database") as db:

                # Get UsersDB, UsernameToUserID, EmailToUserID
                db_key = {"C":"Customers", "A":"Admins"}[user_type]
                users_db = retrieve_db(db_key, db)
                username_to_user_id = retrieve_db("UsernameToUserID", db)
                email_to_user_id = retrieve_db("EmailToUserID", db)

                # Ensure that email and username are not registered yet
                if username.lower() in username_to_user_id:
                    if DEBUG: print("Create User: username already exists")
                    session["DisplayFieldError"] = session["CreateUserUsernameError"] = True
                    flash("Username taken", "create-user-username-error")
                elif email in email_to_user_id:
                    if DEBUG: print("Create User: email already exists")
                    session["DisplayFieldError"] = session["CreateUserEmailError"] = True
                    flash("Email already registered", "create-user-email-error")
                else:
                    # Create customer
                    created_user = {"C":Customer, "A":Admin}[user_type](username, email, password)
                    if DEBUG: print(f"Created: {created_user}")

                    # Store customer into database
                    user_id = created_user.get_user_id()
                    users_db[user_id] = created_user
                    username_to_user_id[username.lower()] = user_id
                    email_to_user_id[email] = user_id

                    # Save changes to database
                    db["UsernameToUserID"] = username_to_user_id
                    db["EmailToUserID"] = email_to_user_id
                    db[db_key] = users_db

                    # Redirect to prevent form resubmission
                    form_trigger = ""
                    flash(f"Created new {created_user.__class__.__name__.lower()}: {username}")
                    return redirect(f"{url_for('manage_accounts')}?page={active_page}")

    # Get users database
    with shelve.open("database") as db:
        all_users = tuple(retrieve_db("Customers", db).values())

        # If is master admin
        if admin.is_master():
            # Removed master admin from list
            admins_db = retrieve_db("Admins", db)
            admins_db.pop(retrieve_db("UsernameToUserID", db)["admin"], None)
            all_users = tuple(admins_db.values()) + all_users

    # Set page number
    last_page = math.ceil(len(all_users)/ACCOUNTS_PER_PAGE)
    if active_page < 1:
        active_page = 1
    elif active_page > last_page:
        active_page = last_page

    first_index = (active_page-1)*ACCOUNTS_PER_PAGE
    display_users = all_users[first_index:first_index+10]

    # Get page list
    if last_page <= 5:
        page_list = [i for i in range(1, last_page+1)]
    else:
        center_item = active_page
        if center_item < 3:
            center_item = 3
        elif center_item > last_page - 2:
            center_item = last_page - 2
        page_list = [i for i in range(center_item-2, center_item+2+1)]
    prev_page = active_page-1 if active_page-1 > 0 else active_page
    next_page = active_page+1 if active_page+1 <= last_page else last_page

    # Get entries range
    entries_range = (first_index+1, first_index+len(display_users))

    return render_template("admin/manage_accounts.html",
                           display_users=display_users, is_master=admin.is_master(),
                           active_page=active_page, page_list=page_list,
                           prev_page=prev_page, next_page=next_page,
                           first_page=1, last_page=last_page,
                           entries_range=entries_range, total_entries=len(all_users),
                           form_trigger=form_trigger,
                           create_user_form=create_user_form,
                           delete_user_form=delete_user_form)


"""|‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾|"""
"""|---------- End of Jabriel's Codes ----------|"""
"""|____________________________________________|"""


#
# Start of Chee Qing's Codes
#

#
# allbooks
#
@app.route("/all_books/<sort_this>")
def all_books(sort_this):
    sort_dict = {}
    books_dict = {}
    language_list = []
    try:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()
        for book in books_dict:
            language = books_dict[book].get_language()
            if language not in language_list:
                language_list.append(language)
                print(language_list)

    except:
        print("There are no books")

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

    return render_template("all_books.html", books_dict=books_dict, sort_dict=sort_dict, language_list=language_list, sort_this=sort_this)

def filter_language(language):
    books = {}
    books_dict = {}
    try:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()
    except:
        print("There are no books")

    for book in books_dict:
        if books_dict[book].get_language() == language:
            books.update({book: books_dict[book]})
    return books

# Sort name from a to z
def name_a_to_z(books_dict):
    sort_dict = {}
    unsorted_dict = {}
    if books_dict != {}:
        for book in books_dict:
            unsorted_dict.update({book: books_dict[book].get_title()})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key = lambda kv:(kv[1], kv[0]))
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in books_dict:
                sort_dict.update({id: books_dict[id]})
    return sort_dict

# Sort name from z to a
def name_z_to_a(books_dict):
    sort_dict = {}
    unsorted_dict = {}
    if books_dict != {}:
        for book in books_dict:
            unsorted_dict.update({book: books_dict[book].get_title()})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in books_dict:
                sort_dict.update({id: books_dict[id]})
    return sort_dict

# Sort price from low to high
def price_low_to_high(books_dict):
    sort_dict = {}
    unsorted_dict = {}
    if books_dict != {}:
        for book in books_dict:
            unsorted_dict.update({book: float(books_dict[book].get_price())})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key = lambda kv:(kv[1], kv[0]))
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in books_dict:
                sort_dict.update({id: books_dict[id]})
    return sort_dict

# Sort price from high to low
def price_high_to_low(books_dict):
    sort_dict = {}
    unsorted_dict = {}
    if books_dict != {}:
        for book in books_dict:
            unsorted_dict.update({book: float(books_dict[book].get_price())})
        print(unsorted_dict)
        unsorted_dict = sorted(unsorted_dict.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
        unsorted_dict = {k: v for k, v in unsorted_dict}
        print(unsorted_dict)

        for id in unsorted_dict:
            if id in books_dict:
                sort_dict.update({id: books_dict[id]})
    return sort_dict

""" Adding to cart """
@app.route("/addtocart/<int:user_id>", methods=['GET', 'POST'])
def add_to_cart(user_id, book_id, quantity):
    pass
# def add_to_buy(id):
#     user_id = get_user().get_user_id()
#     buy_quantity = int(request.form['quantity'])
#     cart_dict = {}
#     cart_db = shelve.open('database', 'c')
#     msg = ""
#     try:
#         cart_dict = cart_db['Cart']
#         print(cart_dict, "original database")
#     except:
#         print("Error while retrieving data from cart.db")

#     book = c.AddtoBuy(id, buy_quantity)
#     if user_id in cart_dict:
#         book_dict = cart_dict[user_id]
#         print(book_dict)
#         book_dict = book_dict[0]
#         if book_dict == '':
#             print("This user does not has anything in buying cart")
#             cart_dict[user_id].pop(0)
#             cart_dict[user_id].insert(0, {id:buy_quantity})
#         else:
#             if book.get_book_id() in book_dict:
#                 book_dict[book.get_book_id()] += buy_quantity
#                 print("This user has the book in cart")
#                 cart_dict[user_id][0] = book_dict
#                 msg = "Added to cart"
#             else:
#                 print('This user does not has this book in cart')
#                 book_dict[id] = buy_quantity
#                 cart_dict[user_id][0] = book_dict
#     else:
#         print("This user has nothing in cart")
#         cart_dict[user_id] = [{id:buy_quantity}]
#     flash("Book has been added to your cart for you to buy.")
#     cart_db['Cart'] = cart_dict
#     print(cart_dict, "final database")
#     return redirect(request.referrer)


""" View Shopping Cart"""
@app.route('/shopping_cart')
def cart():
    user_id = get_user().get_user_id()
    cart_dict = {}
    books_dict = {}
    cart_db = shelve.open('database', 'c')
    book_db = shelve.open('database')
    try:
        books_dict = book_db['Books']
        book_db.close()
    except:
        print("There is no books in the database currently.")
    buy_count = 0
    rent_count = 0
    total_price = 0
    buy_cart = {}
    rent_cart = []
    try:
        cart_dict = cart_db['Cart']
        print(cart_dict)
        books_dict = book_db['Books']
        book_db.close()
    except:
        print("Error while retrieving data from cart.db")

    if user_id in cart_dict:
        user_cart = cart_dict[user_id]
        if user_cart[0] == '':
            print('This user has nothing in the buying cart')
        else:
            buy_cart = user_cart[0]
            # buy_count = len(user_cart[0])
            for key in buy_cart:
                buy_count += buy_cart[key]
                total_price = float(total_price)
                total_price += float(buy_cart[key]*books_dict[key].get_price())
                total_price = float(("%.2f" % round(total_price, 2)))
        if len(user_cart) == 1:
            print('This user has nothing in the renting cart')
        else:
            rent_cart = user_cart[1]
            rent_count = len(user_cart[1])
            for book in rent_cart:
                total_price += float(books_dict[book].get_price()) * 0.1
                total_price = float(("%.2f" % round(total_price, 2)))
    return render_template('cart.html', buy_count=buy_count, rent_count=rent_count, buy_cart=buy_cart, rent_cart=rent_cart, books_dict=books_dict, total_price=total_price)

#
# update quantity in buying cart
#
@app.route('/update_cart/<int:id>', methods=['GET', 'POST'])
def update_cart(id):
    user_id = get_user().get_user_id()
    cart_db = shelve.open('database')
    cart_dict = cart_db['Cart']
    buy_cart = cart_dict[user_id][0]
    book_quantity = int(request.form['quantity'])
    if book_quantity == 0:
        print('Oh no need to delete')
        delete_buying_cart(id)
    else:
        buy_cart[id] = book_quantity
        print(buy_cart)
        cart_dict[user_id][0] = buy_cart
        cart_db['Cart'] = cart_dict
        print(cart_dict, 'updated database')
        cart_db.close()
    return redirect(request.referrer)

#
# delete item in buying cart
#
@app.route("/delete_buying_cart/<int:id>", methods=['GET', 'POST'])
def delete_buying_cart(id):
    user_id = get_user().get_user_id()
    cart_db = shelve.open('database')
    cart_dict = cart_db['Cart']
    buy_cart = cart_dict[user_id][0]
    #only has buying cart
    if len(buy_cart) == 1:
        if len(cart_dict[user_id]) == 1:
            del cart_dict[user_id]
        else:
            cart_dict[user_id][0] = ''
    else:
        del buy_cart[id]
        cart_dict[user_id][0] = buy_cart
    cart_db['Cart'] = cart_dict
    print(cart_dict, 'updated database')
    cart_db.close()
    return redirect(request.referrer)

#
# Checkout Form (for shipping address etc)
#
@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    user_id = get_user().get_user_id()
    cart_dict = {}
    db = shelve.open('database', 'c')
    buy_count = 0
    rent_count = 0
    total_price = 0
    buy_cart = {}
    rent_cart = []
    # eden integration
    discount = 0
    discount_dict = retrieve_db('Discount',db)
    if user_id in discount_dict:
            user = discount_dict.get(user_id)
            print(user)
            discount = user.get_discount()
            print(discount)
    #end of eden integration

    try:
        books_dict = db['Books']
        db = shelve.open('database', 'c')
        db_pending = db['Pending_Order']
        del db_pending[user_id]
        db['Pending_Order'] = db_pending
        db.close()
    except:
        pass

    try:
        cart_dict = db['Cart']
        print(cart_dict)
    except:
        print("Error while retrieving data from database")

    if user_id in cart_dict:
        user_cart = cart_dict[user_id]
        if user_cart[0] == '':
            print('This user has nothing in the buying cart')
        else:
            buy_cart = user_cart[0]
            for key in buy_cart:
                buy_count += buy_cart[key]
                total_price = float(total_price)
                total_price += float(buy_cart[key]*books_dict[key].get_price())
                total_price = float(("%.2f" % round(total_price, 2)))
        if len(user_cart) == 1:
            print('This user has nothing in the renting cart')
        else:
            rent_cart = user_cart[1]
            rent_count = len(user_cart[1])
            for book in rent_cart:
                total_price += float(books_dict[book].get_price()) * 0.1
                total_price = float(("%.2f" % round(total_price, 2)))
    else:
        return redirect(url_for("home"))
    #eden integration
    before_discount = total_price
    discount_applied = total_price * discount/100
    total_price = total_price - discount_applied
    Orderform = OrderForm.OrderForm(request.form)

    return render_template("checkout.html", form=Orderform, total_price=total_price, buy_count=buy_count,\
                           rent_count=rent_count, buy_cart=buy_cart, rent_cart=rent_cart, books_dict=books_dict\
                               ,discount_applied=discount_applied, before_discount=before_discount)

#
# Create Check out session with Stripe
#
@app.route('/create-checkout-session/<total_price>', methods=['POST'])
def create_checkout_session(total_price):
    user_id = get_user().get_user_id()
    order_dict = {}
    ship_method = request.form['ship-method']
    print("creating checkout session...")
    total_price = float(total_price)
    try:
        db = shelve.open('database')
        cart_dict = db['Cart']
        user_cart = cart_dict[user_id]
        #db = shelve.open('database')
    except:
        user_cart = []
    Orderform = OrderForm.OrderForm(request.form)
    if request.method == 'POST' and Orderform.validate():
        if ship_method == 'Standard Delivery':
            total_price += 5
        new_order = OrderForm.Order_Detail(user_id, Orderform.name.data, Orderform.email.data, str(Orderform.contact_num.data), \
                   Orderform.address.data, ship_method, user_cart, total_price)
        order_dict[user_id] = new_order
        db['Pending_Order'] = order_dict
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
            success_url='http://127.0.0.1:5000/orderconfirm',
            cancel_url=request.referrer,
        )

        return redirect(checkout_session.url)
    else:
        flash(list(Orderform.errors.values())[0][0], 'warning')
        return redirect(request.referrer)

#
# show confirmation page upon successful payment
#
@app.route("/orderconfirm")
def orderconfirm():
    user_id = get_user().get_user_id()
    db_order= []
    books_dict = {}
    db = shelve.open('database')
    cart_dict = db['Cart']
    db_pending = db['Pending_Order']
    books_dict = db['Books']
    # in case user hand itchy go and reload the page, bring them back to home page
    try:
        new_order = db_pending[user_id]
        cartvalue = cart_dict[user_id]

        try:
            db_order = db['Order']
        except:
            print("Error while loading data from database")
            # return redirect(url_for("home"))

        db_order.append(new_order)

        print("cartvalue:", cartvalue)
        try:
            cartbuy = cartvalue[0]
            print("cartbuy:", cartbuy)
        except:
            pass
        if cartbuy != "":
            for i in books_dict:
                for x, y in zip(list(cartbuy.keys()), list(cartbuy.values())):
                    if i == x:
                        book = books_dict.get(i)
                        print("qty b4", book.get_qty())
                        newqty = int(book.get_qty()) - int(y)
                        book.set_qty(newqty)
                        print("qty aft", book.get_qty())

        try:
            cartrent = cartvalue[1]
            print("cartrent:", cartrent)
            if cartrent != "":
                for i in books_dict:
                    for x in cartrent:
                        if i == x:
                            book = books_dict.get(i)
                            print("rent qty b4:", book.get_rented())
                            newrented = int(book.get_rented()) + int(1)
                            book.set_rented(newrented)
                            print("rent qty aft:", book.get_rented())

        except:
            pass

        del cart_dict[user_id]
        del db_pending[user_id]
        db['Books'] = books_dict
        db['Pending_Order'] = db_pending
        db['Order'] = db_order
        db['Cart'] = cart_dict
        print(db_pending, 'should not have pending order as user already check out')
        print(cart_dict, 'updated database[cart]')
        print(db_order, 'updated databas[order]')
    except KeyError:
        return redirect(url_for("home"))

    db.close()
    return render_template("order_confirmation.html")

#
# Admin manage orders
#
@app.route("/admin/manage-orders")
def manage_orders():
    db_order = []
    delivery_method = []
    collection_method =[]
    new_order = []
    confirm_order = []
    ship_order = []
    deliver_order = []
    canceled_order = []
    not_returned_order  = []
    books_dict = {}
    try:
        db = shelve.open('database')
        books_dict = db['Books']
        db_order = db['Order']
        print(db_order, "orders in database")
        db.close()
    except:
        print("There might not have any orders as of now.")

    for order in db_order:
        print(order.get_order_id(),  order.get_order_status())
        # if order has been cancel, do not show in other tab
        if order.get_order_status() == 'Canceled':
            canceled_order.append(order)
        else:
        # filter by shipping method
            if order.get_ship_method() == 'Standard Delivery':
                delivery_method.append(order)
            else:
                collection_method.append(order)

            # filter by order status
            if order.get_order_status() == 'Ordered':
                new_order.append(order)
            elif order.get_order_status() == 'Confirmed':
                confirm_order.append(order)
            elif order.get_order_status() == 'Shipped':
                ship_order.append(order)
            else:
                deliver_order.append(order)
                # filter by return status of rented books (only delivered orders can see this)
                if order.get_returned_status() == 'Not Returned':
                    not_returned_order.append(order)

    # display from most recent to the least
    db_order = list(reversed(db_order))
    delivery_method = list(reversed(delivery_method))
    collection_method = list(reversed(collection_method))
    new_order = list(reversed(new_order))
    confirm_order = list(reversed(confirm_order))
    ship_order = list(reversed(ship_order))
    deliver_order = list(reversed(deliver_order))
    canceled_order = list(reversed(canceled_order))

    return render_template('admin/manage_orders.html', all_order=db_order, delivery_method=delivery_method, collection_method=collection_method, \
                           new_order=new_order, confirm_order=confirm_order, ship_order=ship_order, deliver_order=deliver_order, \
                           canceled_order=canceled_order, not_returned_order=not_returned_order, books_dict=books_dict)

#
# Admin update order status
#
@app.route("/admin/manage_orders/edit_status/<order_id>", methods=['GET', 'POST'])
def edit_status(order_id):
    db_order = []
    order_status = request.form['order-status']
    print(order_status)
    try:
        db = shelve.open('database')
        db_order = db['Order']
        print(db_order, "orders in database")
    except:
        print("Error while loading data from database")
    for order in db_order:
        if order.get_order_id() == order_id:
            order.set_order_status(order_status)
            flash('Order status for ' + order_id + ' has been updated.')
    db['Order'] = db_order
    db.close()
    return redirect(request.referrer)

#
# Admin Cancel Order
#
@app.route("/admin/manage_orders/cancel_order/<order_id>", methods=['GET', 'POST'])
def cancel_order(order_id):
    db_order = []
    try:
        db = shelve.open('database')
        db_order = db['Order']
        books_dict = db['Books']
    except:
        print("Error while loading data from database")
    for order in db_order:
        if order.get_order_id() == order_id:
            order.set_order_status('Canceled')
            rent_item = order.get_rent_item()
            for book in rent_item:
                rented_number = books_dict[book].get_rented()
                new_rented_number = rented_number - 1
                books_dict[book].set_rented(new_rented_number)
            flash(order_id + ' has been canceled.')
    db['Order'] = db_order
    db['Books'] = books_dict
    db.close()
    return redirect(request.referrer)

#
# Edit return status for rented books
#
@app.route("/admin/manage_orders/edit_return/<order_id>", methods=['GET', 'POST'])
def edit_return(order_id):
    db_order = []
    try:
        db = shelve.open('database')
        db_order = db['Order']
        print(db_order, "orders in database")
        books_dict = db['Books']
    except:
        print("Error while loading data from database")
    for order in db_order:
        if order.get_order_id() == order_id:
            rent_item = order.get_rent_item()
            # for returned orders [1, 2, 'Returned']
            # set to not returned, rented book increase by 1
            if order.get_returned_status() == 'Returned':
                order.set_returned_status('No')
                for book in rent_item:
                    rented_number = books_dict[book].get_rented()
                    new_rented_number = rented_number+1
                    books_dict[book].set_rented(new_rented_number)
                flash('Return status for rented books in ' + order_id + ' has changed to "Not Returned".')
            # for not returned orders [1, 2]
            # set to returned, rented book decrease by 1
            else:
                for book in rent_item:
                    rented_number = books_dict[book].get_rented()
                    new_rented_number = rented_number-1
                    books_dict[book].set_rented(new_rented_number)
                order.set_returned_status('yes')
                flash('Rented books in ' + order_id + ' has been returned.')
    db['Order'] = db_order
    db['Books'] = books_dict
    db.close()
    print(order.get_returned_status())
    return redirect(request.referrer)


#
# End of Chee Qing's Codes
#


#
# counter for generating id
#
def count_id(Table): 
    the_dict = {} #empty dictionary
    db = shelve.open('database','c') #open database
    the_dict = db[Table] #load table details from database
    db.close() #close database

    count = [0] #test
    for key in the_dict: #loop through the dictionary
        count.append(key) #add to list
    
    highest_id = max(count) #gets the highest id


    return int(highest_id) #return highest id

#
# about page static
#
@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")


# test sitemap for my links
@app.route('/sitemap',methods=["GET", "POST"])
def sitemap():
    return render_template("sitemap.html")

#
#End of eden codes
#

#
# luqman's codes
#

# Function to return id of last book to set ID for newly added books
def get_last_book_id():
    """ Return the ID of the last book """

    books_dict = {}
    db = shelve.open('database', 'r')
    books_dict = db['Books']
    db.close()

    id_list = list(books_dict.keys())
    last_id = max(id_list)
    return int(last_id)

    # count_dict = {}
    # db = shelve.open('database.db', 'c')
    #
    # try:
    #     count_dict = db['Count']
    # except:
    #     print("Error in retrieving count from database.db")
    #
    # count_dict[last_id] = last_id
    # db['Count'] = count_dict


# Check if file extension is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Home page
@app.route("/")
def home():

    try:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()

    except:
        print("There are no books")


    english = []
    chinese = []
    for key in books_dict:
        book = books_dict.get(key)
        if book.get_language() == "English":
            english.append(book)
        elif book.get_language() == "Chinese":
            chinese.append(book)

    # books_list = []
    # for key in books_dict:
    #     book = books_dict.get(key)
    #     books_list.append(book)

    return render_template("home.html", english=english, chinese=chinese)  # optional: books_list=books_list


# Add Book
lang_list = [('', 'Select'), ('English', 'English'), ('Chinese', 'Chinese'), ('Malay', 'Malay'), ('Tamil', 'Tamil')]
cat_list = [('', 'Select'), ('Action & Adventure', 'Action & Adventure'), ('Classic', 'Classic'), ('Comic', 'Comic'), ('Detective & Mystery', 'Detective & Mystery')]


@app.route('/admin/add-book', methods=['GET', 'POST'])
def add_book():
    add_book_form = AddBookForm(request.form)
    add_book_form.language.choices = lang_list
    add_book_form.category.choices = cat_list
    if request.method == "POST" and add_book_form.validate():
        books_dict = {}
        db = shelve.open('database', 'c')

        try:
            books_dict = db['Books']
        except:
            print("Error in retrieving Books from database")

        try:
            Book.Book.count_id = get_last_book_id()
        except:
            print("First time adding book so last book id not needed")

        book = Book.Book(add_book_form.language.data, add_book_form.category.data, add_book_form.age.data, add_book_form.action.data, add_book_form.title.data, add_book_form.author.data, add_book_form.price.data, add_book_form.stock.data, add_book_form.desc.data, add_book_form.img.data, rented=0)

        if add_book_form.language2.data != "":
            book.set_language(add_book_form.language2.data)
            lang_list.append(tuple([add_book_form.language2.data, add_book_form.language2.data]))

        if add_book_form.category2.data != "":
            book.set_category(add_book_form.category2.data)
            cat_list.append(tuple([add_book_form.category2.data, add_book_form.category2.data]))


        # check if post request has image file part
        if 'bookimg' not in request.files:
            flash('There is no image uploaded!')
            return redirect(request.url)
        bookimg = request.files['bookimg']
        if bookimg == '':
            flash("No image selected for uploading")
            return redirect(request.url)
        if bookimg and allowed_file(bookimg.filename):
            filename = str(secure_filename(bookimg.filename))
            currentbookid = book.get_book_id()
            extension=filename.split(".")
            extension=str(extension[1])
            bookimg.filename = str(currentbookid) + "." + extension

            path = os.path.join(app.config['UPLOAD_FOLDER'], bookimg.filename)
            bookimg.save(path)

            #resize codes
            image = Image.open(path)
            resized_image = image.resize((259,371))
            resized_image.save(path)

            print("upload_image filename: " + filename)

        else:
            print('Allowed image types are -> png, jpg, jpeg')
            return render_template('add_book.html', form=add_book_form)

        print("Book image uploaded under " + str(path))

        book.set_img(str("/" + path))
        books_dict[book.get_book_id()] = book
        db['Books'] = books_dict

        # Test codes
        books_dict = db['Books']
        book = books_dict[book.get_book_id()]
        print(book.get_title(), book.get_price(), "was stored in database successfully with book_id==", book.get_book_id())
        db.close()
        flash("Book successfully added!")
        # return redirect(url_for('inventory'))

    return render_template('admin/add_book.html', form=add_book_form)


# Inventory system for admin
@app.route('/admin/inventory')
def inventory():

    try:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()

    except:
        print("There are no books")

    books_list = []
    for key in books_dict:
        book = books_dict.get(key)
        books_list.append(book)

    return render_template('admin/inventory.html', count=len(books_list), books_list=books_list)


# Update Book
@app.route('/update-book/<int:id>/', methods=['GET', 'POST'])
def update_book(id):
    update_book_form = AddBookForm(request.form)
    update_book_form.language.choices = lang_list
    update_book_form.category.choices = cat_list
    if request.method == 'POST' and update_book_form.validate():
        books_dict = {}
        db = shelve.open('database', 'w')
        books_dict = db['Books']

        book = books_dict.get(id)
        if update_book_form.language.data != "":
            book.set_language(update_book_form.language.data)
        else:
            book.set_language(update_book_form.language2.data)
        if update_book_form.category.data != "":
            book.set_category(update_book_form.category.data)
        else:
            book.set_category(update_book_form.category2.data)
        book.set_age(update_book_form.age.data)
        book.set_action(update_book_form.action.data)
        book.set_title(update_book_form.title.data)
        book.set_author(update_book_form.author.data)
        book.set_price(update_book_form.price.data)
        book.set_qty(update_book_form.stock.data)
        book.set_desc(update_book_form.desc.data)
        book.set_img(book.get_img())

        # check if post request has image file part
        if 'bookimg' not in request.files:
            flash('There is no image uploaded!')
            return redirect(request.url)
        bookimg = request.files['bookimg']
        if bookimg == '':
            flash("No image selected for uploading")
            return redirect(request.url)
        if bookimg and allowed_file(bookimg.filename):
            filename = str(secure_filename(bookimg.filename))
            currentbookid = book.get_book_id()
            extension=filename.split(".")
            extension=str(extension[1])
            bookimg.filename = str(currentbookid) + "." + extension

            path = os.path.join(app.config['UPLOAD_FOLDER'], bookimg.filename)
            bookimg.save(path)

            #resize codes
            image = Image.open(path)
            resized_image = image.resize((259,371))
            resized_image.save(path)

            book.set_img(str("/" + path))
            print("upload_image filename: " + filename)

        db['Books'] = books_dict
        db.close()

        flash("Book successfully updated!")
        return redirect(url_for('inventory'))


    else:
        books_dict = {}
        db = shelve.open('database', 'r')
        books_dict = db['Books']
        db.close()

        book = books_dict.get(id)
        update_book_form.language.data = book.get_language()
        update_book_form.language2.data = book.get_language()
        update_book_form.category.data = book.get_category()
        update_book_form.category2.data = book.get_category()
        update_book_form.age.data = book.get_age()
        update_book_form.action.data = book.get_action()
        update_book_form.title.data = book.get_title()
        update_book_form.author.data = book.get_author()
        update_book_form.price.data = book.get_price()
        update_book_form.stock.data = book.get_qty()
        update_book_form.desc.data = book.get_desc()
        update_book_form.img.data = book.get_img()

        return render_template('update_book.html', form=update_book_form)


# Delete Book
@app.route('/delete-book/<int:id>', methods=['POST'])
def delete_book(id):
    books_dict = {}
    db = shelve.open('database', 'w')
    books_dict = db['Books']

    book = books_dict.get(id)
    deletethisbook = str(book.get_img())
    deletethisbook = deletethisbook[1:]
    books_dict.pop(id)
    if os.path.isfile(deletethisbook):
        os.remove(deletethisbook)
        print(deletethisbook + ' is deleted')
    else:
        print(deletethisbook)
        print("This book cover image does not exist")

    db['Books'] = books_dict
    db.close()

    return redirect(url_for('inventory'))


# Book info page v2
@app.route('/book/<int:id>', methods=['GET', 'POST'])
def book_info2(id):
    book_db = shelve.open('database', 'r')
    books_dict = book_db['Books']
    book_db.close()

    currentbook = []
    book = books_dict.get(id)



    book.set_book_id(book.get_book_id())
    book.set_language(book.get_language())
    book.set_category(book.get_category())
    book.set_age(book.get_age())
    book.set_action(book.get_action())
    book.set_title(book.get_title())
    book.set_author(book.get_author())
    book.set_price(book.get_price())
    book.set_qty(book.get_qty())
    book.set_desc(book.get_desc())
    book.set_img(book.get_img())

    currentbook.append(book)
    print(currentbook, book.get_title())

    return render_template('book_info2.html', currentbook=currentbook)

@app.route('/book/<int:id>/reviews/page_<int:reviewPageNumber>')
def book_reviews(id, reviewPageNumber):
    pass

# My Orders for customer
@app.route("/my-orders")
def my_orders():
    db_order = []
    new_order = []
    confirm_order = []
    ship_order = []
    deliver_order = []
    canceled_order = []
    books_dict = {}
    try:
        db = shelve.open('database')
        books_dict = db['Books']
        db_order = db['Order']
        print(db_order, "orders in database")
        db.close()
    except:
        print("There might not have any orders as of now.")
    for order in db_order:
        print(order.get_name(), order.get_rent_item())
        if order.get_order_status() == 'Ordered':
            new_order.append(order)
        elif order.get_order_status() == 'Confirmed':
            confirm_order.append(order)
        elif order.get_order_status() == 'Shipped':
            ship_order.append(order)
        elif order.get_order_status() == 'Delivered':
            deliver_order.append(order)
        elif order.get_order_status() == 'Canceled':
            canceled_order.append(order)
        else:
            print(order, "Wrong order status")

    # display from most recent to the least
    db_order = list(reversed(db_order))
    new_order = list(reversed(new_order))
    confirm_order = list(reversed(confirm_order))
    ship_order = list(reversed(ship_order))
    deliver_order = list(reversed(deliver_order))
    canceled_order = list(reversed(canceled_order))

    print("canceled_order: ", canceled_order)
    return render_template('user/my_orders.html', all_order=db_order, new_order=new_order, \
                           confirm_order=confirm_order, ship_order=ship_order, deliver_order=deliver_order, canceled_order=canceled_order, \
                           books_dict=books_dict)


# Confirm delivery
@app.route("/my-orders/confirm-delivery/<order_id>", methods=['GET', 'POST'])
def confirm_delivery(order_id):
    print("confirm delivery function start")
    print("order_id: ", order_id)
    db_order = []
    # order_status = request.form['order-status']
    # print(order_status)
    try:
        db = shelve.open('database')
        db_order = db['Order']
        print(db_order, "orders in database")
    except:
        print("Error while loading data from database")
    for order in db_order:
        print("order.get_order_id: ", order.get_order_id())
        if order.get_order_id() == order_id:
            order.set_order_status("Delivered")
            print("change alr liao")
            flash('Order #' + order_id + ' has been received.')
    db['Order'] = db_order
    db.close()
    return redirect(request.referrer)


# User Sitemap
@app.route('/user-sitemap',methods=["GET", "POST"])
def user_sitemap():
    return render_template("user_sitemap.html")


# Terms of Use
@app.route('/tos',methods=["GET", "POST"])
def tos():
    return render_template("tos.html")

@app.route('/pp',methods=["GET", "POST"])
def pp():
    return render_template("privacypolicy.html")

#
# end of luqman's codes
#


######################################################################### TODO: REMOVing these
# Only during production. To be removed when published.
# temp home page
@app.route("/temp-home")
def temp_home():
    return render_template("home.html")
@app.route("/test", methods=["GET", "POST"])  # To go to test page: http://127.0.0.1:5000/test
def test():
    # Get current (guest) user
    current_user = get_user()
    current_type = session["UserType"]
    if current_type == "Admin" and current_user.is_master(): current_type = "Master"
    flash(f"Currently logged in as: {current_user}")
    type_list = ("Guest", "Customer", "Admin", "Master")
    return render_template("TESTTEST.html", current_type=current_type, type_list=type_list)
@app.route("/test/<user_type>")
def test2(user_type):
    # Get current (guest) user
    current_user = get_user()
    current_user_type = session["UserType"]
    with shelve.open("database") as db:
        # Get DB
        guests_db = retrieve_db("Guests", db, GuestDB())
        customers_db = retrieve_db("Customers", db)
        admins_db = retrieve_db("Admins", db)
        username_to_user_id = retrieve_db("UsernameToUserID", db)
        email_to_user_id = retrieve_db("EmailToUserID", db)

        if user_type == "Guest":
            if current_user_type == "Guest":
                user = current_user
            else:
                user = Guest()
                guests_db.add(user.get_user_id(), user)
                guests_db.clean()
        elif user_type == "Customer":
            if current_user_type == "Customer":
                user = current_user
            elif "quick_switch_customer" in username_to_user_id:
                user = customers_db[username_to_user_id["quick_switch_customer"]]
            else:
                user = Customer("quick_switch_customer", "quick@switch.customer", "Password1")
                customers_db[user.get_user_id()] = user
                username_to_user_id["quick_switch_customer"] = user.get_user_id()
                email_to_user_id["quick@switch.customer"] = user.get_user_id()
        elif user_type == "Admin":
            if current_user_type == "Admin" and not current_user.is_master():
                user = current_user
            elif "quick_switch_admin" in username_to_user_id:
                user = admins_db[username_to_user_id["quick_switch_admin"]]
            else:
                user = Admin("quick_switch_admin", "quick@switch.admin", "Password1")
                admins_db[user.get_user_id()] = user
                username_to_user_id["quick_switch_admin"] = user.get_user_id()
                email_to_user_id["quick@switch.admin"] = user.get_user_id()
        elif user_type == "Master":
            user = admins_db[username_to_user_id["admin"]]

        # Remove guest if needed
        if current_user is not user and current_user_type == "Guest":
            guests_db.remove(current_user.get_user_id())

        # Save changes
        db["Guests"] = guests_db
        db["Customers"] = customers_db
        db["Admins"] = admins_db
        db["UsernameToUserID"] = username_to_user_id
        db["EmailToUserID"] = email_to_user_id

    # Log in if needed
    if current_user is not user:
        session["UserID"] = user.get_user_id()
        session["UserType"] = user.__class__.__name__

    return redirect(url_for("test"))
@app.route("/test/random/<int:num>")
def test_rand(num,x=('James','Robert','John','Michael','William','David','Richard','Joseph','Thomas','Charles','Christopher','Daniel','Matthew','Anthony','Mark','Donald','Steven','Paul','Andrew','Joshua','Kenneth','Kevin','Brian','George','Edward','Ronald','Timothy','Jason','Jeffrey','Ryan','Jacob','Gary','Nicholas','Eric','Jonathan','Stephen','Larry','Justin','Scott','Brandon','Benjamin','Samuel','Gregory','Frank','Alexander','Raymond','Patrick','Jack','Dennis','Jerry','Tyler','Aaron','Jose','Adam','Henry','Nathan','Douglas','Zachary','Peter','Kyle','Walter','Ethan','Jeremy','Harold','Keith','Christian','Roger','Noah','Gerald','Carl','Terry','Sean','Austin','Arthur','Lawrence','Jesse','Dylan','Bryan','Joe','Jordan','Billy','Bruce','Albert','Willie','Gabriel','Logan','Alan','Juan','Wayne','Roy','Ralph','Randy','Eugene','Vincent','Russell','Elijah','Louis','Bobby','Philip','Johnny','Mary','Patricia','Jennifer','Linda','Elizabeth','Barbara','Susan','Jessica','Sarah','Karen','Nancy','Lisa','Betty','Margaret','Sandra','Ashley','Kimberly','Emily','Donna','Michelle','Dorothy','Carol','Amanda','Melissa','Deborah','Stephanie','Rebecca','Sharon','Laura','Cynthia','Kathleen','Amy','Shirley','Angela','Helen','Anna','Brenda','Pamela','Nicole','Emma','Samantha','Katherine','Christine','Debra','Rachel','Catherine','Carolyn','Janet','Ruth','Maria','Heather','Diane','Virginia','Julie','Joyce','Victoria','Olivia','Kelly','Christina','Lauren','Joan','Evelyn','Judith','Megan','Cheryl','Andrea','Hannah','Martha','Jacqueline','Frances','Gloria','Ann','Teresa','Kathryn','Sara','Janice','Jean','Alice','Madison','Doris','Abigail','Julia','Judy','Grace','Denise','Amber','Marilyn','Beverly','Danielle','Theresa','Sophia','Marie','Diana','Brittany','Natalie','Isabella','Charlotte','Rose','Alexis','Kayla'),y=('Smith','Johnson','Williams','Jones','Brown','Davis','Miller','Wilson','Moore','Taylor','Anderson','Thomas','Jackson','White','Harris','Martin','Thompson','Garcia','Martinez','Robinson','Clark','Rodriguez','Lewis','Lee','Walker','Hall','Allen','Young','Hernandez','King','Wright','Lopez','Hill','Scott','Green','Adams','Baker','Gonzalez','Nelson','Carter','Mitchell','Perez','Roberts','Turner','Phillips','Campbell','Parker','Evans','Edwards','Collins','Stewart','Sanchez','Morris','Rogers','Reed','Cook','Morgan','Bell','Murphy','Bailey','Rivera','Cooper','Richardson','Cox','Howard','Ward','Torres','Peterson','Gray','Ramirez','James','Watson','Brooks','Kelly','Sanders','Price','Bennett','Wood','Barnes','Ross','Henderson','Coleman','Jenkins','Perry','Powell','Long','Patterson','Hughes','Flores','Washington','Butler','Simmons','Foster','Gonzales','Bryant','Alexander','Russell','Griffin','Diaz','Hayes')):
    import random
    lx = len(x)-1
    ly = len(y)-1
    with shelve.open("database") as db:
        # Get DB
        customers_db = retrieve_db("Customers", db)
        username_to_user_id = retrieve_db("UsernameToUserID", db)
        email_to_user_id = retrieve_db("EmailToUserID", db)

        maxno = len(customers_db)+1
        n=0
        for i in range(maxno, maxno+num):
            rand1, rand2 = x[random.randint(0,lx)], y[random.randint(0,ly)]
            username,mail,name,gender=f"{rand1.lower()}{('_','')[random.randint(0,1)]}{rand2.lower()}{('_','')[random.randint(0,1)]}{random.randint(0,999):03}",f"{rand1.lower()}{('_','')[random.randint(0,1)]}{rand2.lower()}@{'exyz'[random.randint(0,3)]}mail.{('com','org','net')[random.randint(0,2)]}",f"{rand1}{(f' {rand2}','')[random.randint(0,1)]}",("O","MF"[random.randint(0,1)])[bool(random.randint(0,40))]
            customer = Customer(username,mail,f"Password{i}")
            if username not in username_to_user_id and mail not in email_to_user_id:
                n+=1
                customer.set_name(('',name)[bool(random.randint(0,8))])
                customer.set_gender(('',gender)[bool(random.randint(0,3))])
                customers_db[customer.get_user_id()] = customer
                username_to_user_id["quick_switch_customer"] = customer.get_user_id()
                email_to_user_id["quick@switch.customer"] = customer.get_user_id()

        # Save changes
        db["Customers"] = customers_db
        db["UsernameToUserID"] = username_to_user_id
        db["EmailToUserID"] = email_to_user_id
    return f"{n} customers created"

if __name__ == "__main__":
    app.run(debug=DEBUG)  # Run app
