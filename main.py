from io import BytesIO

from flask import Flask, render_template, request, session, redirect, url_for, flash, send_file
import requests
import json
from flask_sqlalchemy import SQLAlchemy

from datetime import timedelta


app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_BINDS'] = {
    'files': 'sqlite:///files.sqlite3'
}
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


class files(db.Model):
    __bind_key__ = 'files'
    id = db.Column("id", db.Integer, primary_key=True)
    uploader = db.Column(db.String(50))
    uploader_email = db.Column(db.String(100))
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)


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
    if "user" in session:
        return render_template("users.html", values=users.query.all())
    else:
        flash("Nejsi přihlášen!")
        return redirect(url_for("login"))

@app.route("/login-page", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["usrnm"]
        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["user"] = user
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


@app.route("/user", methods=["POST", "GET"], )
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
        return render_template("user.html", email=email, values=files.query.all(), download=download)
    else:
        flash("Nejsi přihlášen!")
        return redirect(url_for("login"))
    

@app.route('/download/<upload_filename>')
def download(upload_filename):
    if "user" in session:
        upload = files.query.filter_by(filename=upload_filename).first()
        return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)
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

@app.route("/upload", methods=["POST", "GET"])
def upload():
    if "user" in session:
        user = session["user"]
        email = session["email"]

        if request.method == "POST":
            file = request.files['file']
            
            upload = files(uploader=user, uploader_email=email,filename=file.filename, data=file.read())
            db.session.add(upload)
            db.session.commit()

            #found_user = users.query.filter_by(name=user).first()

        return render_template("upload_a_file.html")
    else:
        flash("Nejsi přihlášen!")
        return redirect(url_for("login"))
    

if __name__ == "__main__":
    
    app.run(debug=True, host="0.0.0.0", port=80)
    
    #---Create a new user---
    #usr = users("name", "email")
    #db.session.add(usr)
    #db.session.commit()
    #---Remove a user---
    #usr = files.query.filter_by(name="file_name").delete()
    #db.session.commit()

