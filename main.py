from flask import Flask, render_template, request, session, redirect, url_for, flash
import requests
import json
from flask_sqlalchemy import SQLAlchemy

from datetime import timedelta


app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)
app.app_context().push()

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email
    

def get_meme():
    url = "https://meme-api.com/gimme"
    response = json.loads(requests.request("GET", url).text)
    meme_large = response["preview"][-2]
    subreddit = response["subreddit"]
    return meme_large, subreddit
    



@app.route("/meme")
def meme():
    meme_pic, subreddit = get_meme()
    return render_template("meme.html", meme_pic=meme_pic, subreddit=subreddit)

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/users")
def view():
    return render_template("users.html", values=users.query.all())

@app.route("/login-page", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["usrnm"]
        session["user"] = user
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
            flash("Přihlášen!")
            return redirect(url_for("user"))
        else:
            flash("Účet neexistuje")
            return render_template("login.html")
            #usr = users(user, "")
            #db.session.add(usr)
            #db.session.commit()


    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email uložen!")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        flash("Nejsi přihlášen!")
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"Úspěšně odhlášen!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=80)