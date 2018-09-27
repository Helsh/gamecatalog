#!/usr/bin/python3

#Imports

from flask import Flask, render_template, request
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, User, Game, GameCategory

app = Flask(__name__)

# Web application - Games catalog

engine = create_engine('sqlite:///gamescatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Read endpoints

@app.route("/")
def showMainPage():
    categories = session.query(GameCategory).all()
    return render_template("category.html", categories = categories)

@app.route("/category/<string:category>/items")
def showSelectedItems():
    
    return ""

@app.route("/category/<string:category>/<string:item>")
def showSelectedItem():

    return ""

# Create endpoints

@app.route("/category/new", methods=['GET', 'POST'])
def createNewGameCategory():
    if request.method == 'POST':
        gameGategory = GameCategory(name=request.form["categoryname"])
        session.add(gameGategory)
        session.commit()
        return render_template("index.html")
    else:
        return render_template('newcategory.html')

@app.route("/category/<string:item>/new", methods=['GET', 'POST'])
def createNewItem():
    if request.method == 'POST':
        return render_template('index.html')
    else:
        return render_template('newgame.html')

# Delete endpoints

@app.route("/category/<string:item>/delete")
def deleteSelectedItem():

    return ""

# Update endpoints

@app.route("/category/<string:item>/edit")
def editSelectedItem():

    return ""

# API - Json

@app.route("/category.json")
def showContentInJson():

    return ""

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
