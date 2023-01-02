from flask import Flask, render_template, request, session, redirect, url_for
import requests
import json

from datetime import timedelta


app = Flask(__name__)
app.secret_key = "hello"
app.permanent_session_lifetime = timedelta(days=7)


def get_meme():
    url = "https://meme-api.com/gimme/czechmemes"
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


@app.route("/login-page", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["usrnm"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"]
        return render_template("user.html", user=user)
    else:
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


app.run(debug=True, host="0.0.0.0", port=80)