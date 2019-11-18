import flask
import random
import model

app = flask.Flask(__name__)  #erstelle eine Instanz von Flask Klasse


@app.route("/")   #endpoints mit "/"    "@" über einer Funktion = Decorator
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
    receipe_1 = model.Receipe ("Apfelstrudel", "Cut Apple Bake Sweet", "Sweet")
    receipe_2 = model.Receipe ("Hamburger", "Fry Meat And Eat", "Sour")
    receipe_3 = model.Receipe ("Suppe", "Cut Carrots Add Water", "Salty")

    return flask.render_template("blog.html", receipes=[receipe_1, receipe_2, receipe_3])


if __name__ == '__main__':
    app.run()