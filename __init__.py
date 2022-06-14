from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, g as flask_global
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from SecurityFunctions import encrypt_info, decrypt_info, generate_id
from session_handler import create_user_session, retrieve_user_session
from users import Admin, Customer
import db_fetch as dbf
import os  # For saving and deleting images
from PIL import Image
from Book import Book

from forms import (
    SignUpForm, LoginForm, ChangePasswordForm, ResetPasswordForm, ForgetPasswordForm,
    AccountPageForm, CreateUserForm, DeleteUserForm, AddBookForm, OrderForm
)

# CONSTANTS
DEBUG = True  # Debug flag (True when debugging)
ACCOUNTS_PER_PAGE = 10  # Number of accounts to display per page (manage account page)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app = Flask(__name__)
app.config.from_pyfile("config/app.cfg")  # Load config file
app.jinja_env.add_extension("jinja2.ext.do")  # Add do extension to jinja environment
BOOK_IMG_UPLOAD_FOLDER = 'static/img/books'
app.config['UPLOAD_FOLDER'] = BOOK_IMG_UPLOAD_FOLDER  # Set upload folder

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["30 per second"]
)


def get_user():
    """ Returns user if cookie is correct, else returns None """

    # Get session cookie from request
    session_cookie = request.cookies.get("session")
    user_session = retrieve_user_session(session_cookie)

    # Return None
    if user_session is not None:

        # Retrieve user id from session
        user_id = user_session.user_id

        # Retrieve user data from database
        user_data = dbf.retrieve_user(user_id)

        # If user is not found
        if user_data is not None:

            # If user is admin
            if user_data[5]:
                user = Admin(*user_data)

            # Else user is a customer
            else:
                user_data += dbf.retrieve_customer_details(user_id)
                user = Customer(*user_data)

            # Return user object
            return user




"""    Before Request    """

""" Before first request """
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


""" Before request """
@app.before_request
def before_request():
    flask_global.user = get_user()  # Get user




"""    Home Page    """

""" Home page """
@app.route("/")
@limiter.limit("100/minute", override_defaults=False)
def home():
    # Old code
    # try:
    #     books_dict = {}
    #     db = shelve.open('database', 'r')
    #     books_dict = db['Books']
    #     db.close()

    # except:
    #     print("There are no books")

    # english = []
    # chinese = []
    # for key in books_dict:
    #     book = books_dict.get(key)
    #     if book.get_language() == "English":
    #         english.append(book)
    #     elif book.get_language() == "Chinese":
    #         chinese.append(book)

    # books_list = []
    # for key in books_dict:
    #     book = books_dict.get(key)
    #     books_list.append(book)

    return render_template("home.html", english=[], chinese=[])  # optional: books_list=books_list




"""    Login/Sign-up Pages    """

""" Sign up page """
@app.route("/user/sign-up", methods=["GET", "POST"])
@limiter.limit("100/minute", override_defaults=False)
def sign_up():

    # If user is already logged in
    if flask_global.user is not None:
        return redirect(url_for("account"))

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


""" Login page """
@app.route("/user/login", methods=["GET", "POST"])
@limiter.limit("100/minute", override_defaults=False)
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

            # Check if user exists
            user_attempts = dbf.retrieve_user_attempts(username)

            # Check if account still has attempts left
            print(user_attempts)
            if user_attempts == 0:
                flash("Max login attempts has been reached, account has been locked", "form-error")
                return render_template("user/login.html", form=login_form)

            # If user_data is not succesfully retrieved (username/email/password is/are wrong)
            elif user_data is None:

                # If username / email is correct (failed password attempt)
                if user_attempts is not None:
                    dbf.decrease_login_attempts(username, user_attempts)

                # Flash login error message
                flash("Your account and/or password is incorrect, please try again", "form-error")
                return render_template("user/login.html", form=login_form)

            # If login credentials are correct
            else:
                # Get user id
                user = Admin(*user_data)
                user_id = user.user_id

                # Create session to login
                new_session = create_user_session(user_id, user.is_admin)
                response = make_response(redirect(url_for("home")))
                response.set_cookie("session", new_session)
                return response

    # Render page
    return render_template("user/login.html", form=login_form)


""" Logout """
@app.route("/user/logout")
@limiter.limit("100/minute", override_defaults=False)
def logout():
    response = make_response(redirect(url_for("home")))
    if flask_global.user is not None:
        # Remove session cookie
        response.set_cookie("session", "", expires=0)
    return response


""" Forgot password page """ ### TODO: work on this SpeedFox198 TODO TODO TODO TODO TODO TODO TODO
@app.route("/user/password/forget", methods=["GET", "POST"])
@limiter.limit("100/minute", override_defaults=False)
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




"""    User Pages    """

""" View account page """ ### TODO: work on this SpeedFox198 TODO TODO TODO TODO TODO TODO TODO TODO
@app.route("/user/account", methods=["GET", "POST"])
@limiter.limit("100/minute", override_defaults=False)
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
                    file.save(os.path.join(PROFILE_PIC_UPLOAD_FOLDER, user.get_user_id() + ".png"))
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


"""    Admin Pages    """


# Manage accounts page
@app.route("/admin/manage-accounts", methods=["GET", "POST"])
def manage_accounts():
    return "manage accounts"


@app.route('/admin/inventory')
def inventory():
    inventory_data = dbf.retrieve_inventory()

    # Create book object and store in inventory
    book_inventory = [Book(*data) for data in inventory_data]
    return render_template('admin/inventory.html', count=len(book_inventory), books_list=book_inventory)


def allowed_file(filename):
    # Return true if there is an extension in file, and its extension is in the allowed extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin/add-book', methods=['GET', 'POST'])
def add_book():
    lang_list = [('', 'Select'), ('English', 'English'), ('Chinese', 'Chinese'), ('Malay', 'Malay'), ('Tamil', 'Tamil')]
    category_list = [('', 'Select'), ('Action & Adventure', 'Action & Adventure'), ('Classic', 'Classic'),
                     ('Comic', 'Comic'), ('Detective & Mystery', 'Detective & Mystery')]
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
            book_img_filename = f"{generate_id()}_{secure_filename(book_img.filename)}"  # Generate unique name string for files
            path = os.path.join(app.config['UPLOAD_FOLDER'], book_img_filename)
            book_img.save(path)
            image = Image.open(path)
            resized_image = image.resize((259, 371))
            resized_image.save(path)

            book_details = (generate_id(),
                            add_book_form.language.data,
                            add_book_form.category.data,
                            add_book_form.title.data,
                            int(add_book_form.qty.data),  # int for sqlite
                            int(add_book_form.price.data),  # int for sqlite
                            add_book_form.author.data,
                            add_book_form.desc.data,
                            book_img_filename)

            dbf.book_add(book_details)
            flash("Book successfully added!")

    return render_template('admin/add_book.html', form=add_book_form)


@app.route('/update-book/<id>/', methods=['GET', 'POST'])
def update_book(id):
    return "update book"


@app.route('/delete-book/<id>/', methods=['POST'])
def delete_book(id):
    return "delete book"


@app.route("/admin/manage-orders")
def manage_orders():
    return "manage orders"


"""    Books Pages    """

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

""" Search Results Page """


@app.route("/search-result/<sort_this>")
@limiter.limit("100/minute", override_defaults=False)
def search_result(sort_this):
    sort_dict = {}
    books_dict = {}
    language_list = []
    inventory_data = dbf.retrieve_inventory()
    try:
        for data in inventory_data:
            book = Book(*data)
            books_dict[book.get_book_id()] = book
            language_list.append(book.get_language())
            sort_dict = {'title': 'Title', 'author': 'Author', 'language': 'Language', 'category': 'Category', 'price': 'Price'}
    except:
        print("No books in inventory")
    # try:
    #     books_dict = {}
    #     db = shelve.open('database', 'r')
    #     books_dict = db['Books']
    #     db.close()
    #     for book in books_dict:
    #         language = books_dict[book].get_language()
    #         if language not in language_list:
    #             language_list.append(language)
    #             print(language_list)

    # except:
    #     print("There are no books")

    # if books_dict != {}:
    #     if sort_this == 'latest':
    #         books_dict = dict(reversed(list(books_dict.items())))
    #         sort_dict = books_dict
    #     elif sort_this == 'name_a_to_z':
    #         sort_dict = name_a_to_z(books_dict)
    #     elif sort_this == 'name_z_to_a':
    #         sort_dict = name_z_to_a(books_dict)
    #     elif sort_this == 'price_low_to_high':
    #         sort_dict = price_low_to_high(books_dict)
    #     elif sort_this == 'price_high_to_low':
    #         sort_dict = price_high_to_low(books_dict)
    #     elif sort_this.capitalize() in language_list:
    #         sort_dict = filter_language(sort_this)
    #     else:
    #         sort_dict = books_dict

    q = request.args.get("q", default="", type=str)

    if q:
        for book_id, book in sort_dict.copy().items():
            if not any([s.lower() in book.get_title().lower() for s in q.split()]):
                sort_dict.pop(book_id, None)

    return render_template("all_books.html", books_dict=books_dict, sort_dict=sort_dict, language_list=language_list)


"""    Start of Cart Pages    """


# Add to cart
@app.route("/addtocart/<int:user_id>", methods=['GET', 'POST'])
@limiter.limit("100/minute", override_defaults=False)
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


@app.route('/shopping-cart')
@limiter.limit("100/minute", override_defaults=False)
def cart():
    user_id = get_user().get_user_id()
    cart_dict = {}
    books_dict = {}
    cart_db = None  # shelve.open('database', 'c')
    book_db = None  # shelve.open('database')
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
                total_price += float(buy_cart[key] * books_dict[key].get_price())
                total_price = float(("%.2f" % round(total_price, 2)))
        if len(user_cart) == 1:
            print('This user has nothing in the renting cart')
        else:
            rent_cart = user_cart[1]
            rent_count = len(user_cart[1])
            for book in rent_cart:
                total_price += float(books_dict[book].get_price()) * 0.1
                total_price = float(("%.2f" % round(total_price, 2)))
    return render_template('cart.html', buy_count=buy_count, rent_count=rent_count, buy_cart=buy_cart,
                           rent_cart=rent_cart, books_dict=books_dict, total_price=total_price)


"""    Order Pages    """

""" Customer Orders Page """


@app.route("/my-orders")
@limiter.limit("100/minute", override_defaults=False)
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
                           confirm_order=confirm_order, ship_order=ship_order, deliver_order=deliver_order,
                           canceled_order=canceled_order, \
                           books_dict=books_dict)


"""    Miscellaneous Pages    """

""" About Page """


@app.route("/about")
def about():
    return render_template("about.html")


"""    Error Handlers    """


# Error handling page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html")


@app.errorhandler(429)
def too_many_request(e):
    return render_template("error/429.html")


@app.route("/medium")
@limiter.limit("100/minute", override_defaults=False)
def medium():
    return ":|"


"""    Main    """

if __name__ == "__main__":
    app.run(debug=DEBUG)  # Run app
