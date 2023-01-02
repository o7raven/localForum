from flask import Flask, render_template, request, session
import requests
import json

app = Flask(__name__)

def get_meme():
    url = "https://meme-api.com/gimme/czechmemes"
    response = json.loads(requests.request("GET", url).text)
    meme_large = response["preview"][-2]
    subreddit = response["subreddit"]
    return meme_large, subreddit
    

@app.route("/base-not-permitted")
def base():
    return render_template("base.html")

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
        user = request.form["usrnm"]
        session['user'] = user
    return render_template("login.html")

app.run(debug=True, host="0.0.0.0", port=80)