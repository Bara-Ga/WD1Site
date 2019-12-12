import datetime

import flask
import random
import model
import string
import hashlib
import uuid

from flask import request
from flask import url_for, render_template


##
def require_session_token(func):
    """Decorator to require authentication to access routes"""

    def wrapper(*args, **kwargs):
        session_token = flask.request.cookies.get("session_token")
        redirect_url = flask.request.path or '/'

        if not session_token:
            app.logger.error('no token in request')
            return flask.redirect(flask.url_for('login', redirectTo=redirect_url))
        user = db.query(model.User).filter_by(session_token=session_token).filter(
            model.User.session_expiry_datetime >= datetime.datetime.now()).first()

        if not user:
            app.logger.error(f'token {session_token} not valid')
            return flask.redirect(flask.url_for('login', redirectTo=redirect_url))

        app.logger.info(
            f'authenticated user {user.username} with token {user.session_token} valid until {user.session_expiry_datetime.isoformat()}')
        flask.request.user = user
        return func(*args, **kwargs)

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper

##


N_USERS = 10
N_RECEPIES = 10
N_BOOKS = 10

app = flask.Flask(__name__)
db = model.db
db.create_all()
hasher = hashlib.blake2s()


def hash_password(password):
    hasher = hashlib.sha512()
    password = password.encode('utf-8')
    hasher.update(password)
    return hasher.hexdigest()


def create_dummy_users():
    users = []

    for x in range(N_USERS):
        name = "".join(random.choices(string.ascii_lowercase, k=10))
        user = model.User(username=name, email=f"{name}@home.com", password=hash_password(name))
        users.append(user)

    my_user = model.User(username="admin", email="admin@home.com", password=hash_password("admin"))
    users.append(my_user)
    test_user = model.User(username="test", email="test@home.com", password=hash_password("test"))
    users.append(test_user)

    for user in users:
        if not db.query(model.User).filter_by(username=user.username).first():
            db.add(user)

    db.commit()


def create_dummy_recepies():
    recepies = []

    for x in range(N_RECEPIES):
        name = "".join(random.choices(string.ascii_lowercase, k=10))
        name = name.capitalize()
        description = "".join(random.choices(string.ascii_lowercase + "    ", k=80))
        taste = "".join(random.choices(string.ascii_lowercase + "    ", k=20))
        new_receipe = model.Receipe(name=name, description=description, taste=taste)
        recepies.append(new_receipe)

    receipe_1 = model.Receipe(name="Apfelstrudel", description="Cut Apple Bake Sweet", taste="sweet")
    recepies.append(receipe_1)
    receipe_2 = model.Receipe(name="Hamburger", description="Fry Meat And Eat", taste="sour")
    recepies.append(receipe_2)
    receipe_3 = model.Receipe(name="Suppe", description="Fry Meat And Drink", taste="bitter")
    recepies.append(receipe_3)
    for receipe in recepies:
        if not db.query(model.Receipe).filter_by(name=receipe.name).first():
            db.add(receipe)

    db.commit()


def create_dummy_books():
    bookslist = []

    for x in range(N_BOOKS):

        title = "".join(random.choices(string.ascii_lowercase, k=10))
        bookdescription = "".join(random.choices(string.ascii_lowercase + "    ", k=20))
        new_book = model.books(title=title, bookdescription=bookdescription)
        bookslist.append(new_book)
        book_1 = model.books(title="True Story", bookdescription="About the world we live in")
        bookslist.append(book_1)
        book_2 = model.books(title="Another Story", bookdescription="About the next generation")
        bookslist.append(book_2)
        book_3 = model.books(title="ABC Book", bookdescription="Learn to dive")
        bookslist.append(book_3)
        for book in bookslist:
            if not db.query(model.books).filter_by(title=book.title).first():
                db.add(book)

    db.commit()


def add_dummy_data():
    create_dummy_users()
    create_dummy_recepies()
    create_dummy_books()


@app.route("/")
def index():
    return flask.render_template("index.html", myname="Bara")


@app.route("/fakebook")
def fakebook():
    return flask.render_template("fakebook.html")


@app.route("/hairdress")
def hairdress():
    return flask.render_template("hairdress.html")


@app.route("/secret-number-game")
def secret_number_game():
    secret = random.randint(1, 10)
    attemps = 0
    return flask.render_template("secret_number_game.html", secret_number=secret)


@app.route("/blog")
def blog():
    db_recepies = db.query(model.Receipe).filter_by(taste="sweet").all()
    return flask.render_template("blog.html", receipes=db_recepies)


@app.route("/books")
def books():
    all_books = db.query(model.books).all()
    return flask.render_template("books.html", books=all_books)


@app.route("/register", methods=["GET", "POST"])
def register():
    current_request = flask.request

    if current_request.method == "GET":
        return flask.render_template("register.html")

    elif current_request.method == "POST":
        # TODO: register valid user
        email = current_request.form.get("email")
        username = current_request.form.get("username")
        password = current_request.form.get("password")

        user_exists = db.query(model.User).filter_by(username=username).first()  # schauen ob Username bereits vorhanden
        email_exists = db.query(model.User).filter_by(email=email).first()
        if user_exists:
            print("User already exists")

        elif email_exists:
            print("Email already exists")
        else:
            new_user = model.User(username=username, email=email, password=hash_password(password))
            db.add(new_user)
            db.commit()
        return flask.redirect(flask.url_for('register'))


@app.route("/accounts")
@require_session_token

def accounts():
    all_user = db.query(model.User).all()
    return flask.render_template("account.html", accounts=all_user)


@app.route("/accounts/<account_id>/delete", methods=["GET", "POST"])
def account_delete(account_id):
    user_to_delete = db.query(model.User).get(account_id)
    if user_to_delete is None:
        return flask.redirect(flask.url_for("accounts"))

    current_request = flask.request
    if current_request.method == "GET":
        return flask.render_template("account_delete.html", account=user_to_delete)

    elif current_request.method == "POST":
        db.delete(user_to_delete)
        db.commit()
        return flask.redirect(flask.url_for("accounts"))


@app.route("/accounts/<account_id>/edit", methods=["GET", "POST"])
def account_edit(account_id):
    user_to_edit = db.query(model.User).get(account_id)
    if user_to_edit is None:
        return flask.redirect(flask.url_for("accounts"))

    current_request = flask.request
    if current_request.method == "GET":
        return flask.render_template("account_edit.html", account=user_to_edit)

    elif current_request.method == "POST":
        email = current_request.form.get("email")
        username = current_request.form.get("username")
        user_to_edit.email = email
        user_to_edit.username = username
        db.add(user_to_edit)
        db.commit()
        return flask.redirect(flask.url_for("accounts"))


## Books
@app.route("/books/<books_id>/delete", methods=["GET", "POST"])
def books_delete(books_id):
    books_delete = db.query(model.books).get(books_id)
    if books_delete is None:
        return flask.redirect(flask.url_for("books"))

    current_request = flask.request
    if current_request.method == "GET":
        return flask.render_template("books_delete.html")

    elif current_request.method == "POST":
        db.delete(books_delete)
        db.commit()
        return flask.redirect(flask.url_for("books"))


@app.route("/books/<books_id>/edit", methods=["GET", "POST"])
def books_edit(books_id):
    books_edit = db.query(model.books).get(books_id)
    if books_edit is None:
        return flask.redirect(flask.url_for("books"))

    current_request = flask.request
    if current_request.method == "GET":
        return flask.render_template("books_edit.html", book=books_edit)

    elif current_request.method == "POST":
        title = current_request.form.get("title")
        bookdescription = current_request.form.get("description")
        books_edit.title = title
        books_edit.bookdescription = bookdescription
        db.add(books_edit)
        db.commit()
        return flask.redirect(flask.url_for("books"))


## Books End

## Log in
@app.route("/login", methods=["GET", "POST"])
def login():
    current_request = flask.request
    if current_request.method == "GET":
        return flask.render_template("login.html")
    elif current_request.method == "POST":
        email = current_request.form.get("email")
        password = current_request.form.get("password")
        user = db.query(model.User).filter_by(email=email).first()
        if user is None:
            print("User does not exist")
            return flask.redirect(flask.url_for("login"))
        else:
            if hash_password(password) == user.password:
                # find redirect method from request argument
                redirect_url = current_request.args.get("redirectTo", "/")

                # generate token axpiry time in 1 hour from now
                session_token = str(uuid.uuid4())
                session_expiry_datetime = datetime.datetime.now() + datetime.timedelta(seconds=3600)
                # update user with new session token and expiry
                user.session_token = session_token
                user.session_expiry_datetime = session_expiry_datetime
                # save in DB
                db.add(user)
                db.commit()

                # make response and add cookie with session token
                response = flask.make_response(flask.redirect(redirect_url))
                response.set_cookie("session_token", session_token)
                return response

            else:
                return flask.redirect(flask.url_for("forbidden"))


@app.route("/forbidden")
def forbidden():
    return flask.render_template("forbidden.html")


@app.route("/logout")
def logout():
    # get session token
    current_request = flask.request
    session_token = current_request.cookies.get("session_token")
    if not session_token:
        # TODO: use redirect url to get back to this page after Login
        return flask.redirect(flask.url_for("login"))
    user = db.query(model.User).filter_by(session_token=session_token).first()
    if not user:
        return flask.redirect(flask.url_for("login"))
    if user and not user.session_expiry_datetime > datetime.datetime.now():
        return flask.redirect(flask.url_for("login"))

    # remove token from db and browser cookie
    user.session_token = None
    user.session_expiry_datetime = None
    db.add(user)
    db.commit()

    return flask.redirect(flask.url_for("login"))


if __name__ == '__main__':
    add_dummy_data()
    app.run()
