from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

import json
import plotly
import plotly.express as px

import pandas as pd
import numpy as np


app = Flask(__name__)

app.secret_key = "HelloWorld"
#app.config['SQLALCHEMY_DATABASE_URI'] = 'ivanka0164.mysql.pythonanywhere-services.com'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEME_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=20)
db = SQLAlchemy(app)


class users(db.Model):

    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column( db.String(100))
    email = db.Column( db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route("/")
def home():
    return render_template('index.html', content="Testing")

#exo 1
@app.route("/exo1")
def hello():
    return "Hello World!"

#exo 2 & 3
@app.route("/exo2_3")
def hello2():
    return render_template("exo2_3.html", message = "Hello Multicolor World! I hope you like this amazing and uselessly long rainbow sentence , i add a black color:)")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"]=found_user.email

        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit()



        flash("Login Succesfull")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("already logged in !")
            return redirect(url_for("user"))
            

        return render_template("login.html")

@app.route("/user", methods=["POST","GET"])
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
            flash("Email was saved !")
        else:
            if "email" in session:
                email = session["email"]



        return render_template("user.html", email=email )
    else:
        flash("You are not logged in ! ")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    
    flash("You have been logged out !", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))


# Exo 7
@app.route("/exo7")
def exo7():
    return render_template("exo7.html")


@app.route("/exo7/dataset", methods=["POST"])
def exo7_dataset_describe():
    fichier = request.files.get("dataset")
   
    # TODO Recupérer le séparateur grâce à des Regex
    sep = request.form["sep"]

    # TODO Extraire le nom du fichier grâce à des Regex
    name = str(fichier)[15:-15]

    df = pd.read_csv(fichier, sep=sep)
    describ = round(df.describe(),2)

    dico = {}
    for x in describ:
        dico[x] = describ[x].to_dict()

    # TODO Régler problème quand 1ere entete est catégorielle
    a = list(dico.keys())[0]
    entete = list(dico[a].keys())

    return render_template("exo7.html", name=name, entete=entete, data=dico)




# Exo 7 avec plotly 
#df_sample = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/minoritymajority.csv')

gapminder = px.data.gapminder()
fig = px.scatter(gapminder.query("year==2007"), x="gdpPercap", y="lifeExp", size="pop", color="continent",
           hover_name="country", log_x=True, size_max=60)
#fig.show()


fig.layout.template = None
graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route("/plotly")
def home1():
    return render_template('plotly.html', v = graphJSON)




# Exo 7 avec plotly (plusier graphs)
df = px.data.gapminder()
fig2 = px.line_geo(df.query("year==2007"), locations="iso_alpha", color="continent", projection="orthographic")
fig2.layout.template = None
    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
@app.route('/plotly2')
def plotly2():

    return render_template('plotly2.html',
                           graphJSON2=graphJSON2 )





if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=9999)

