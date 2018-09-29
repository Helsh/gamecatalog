#!/usr/bin/python3

#Imports

from flask import Flask, render_template, request
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, User, Game, GameCategory
from DbOperations import DbOperations

app = Flask(__name__)

# Web application - Games catalog

# Connection with database

engine = create_engine('sqlite:///gamescatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

dbOperations = DbOperations()

# Read endpoints

@app.route("/")
def showMainPage():
    categories = session.query(GameCategory).all()
    return render_template("index.html", categories = categories)

@app.route("/category/<string:gamecat_id>/games")
def showSelectedGames(gamecat_id):
    games = session.query(Game).filter_by(gamecategory_id = gamecat_id).all()
    return render_template("games.html", games = games)

@app.route("/category/<string:category>/<string:item>")
def showSelectedGame():

    return ""

# Create endpoints

@app.route("/category/new", methods=['GET', 'POST'])
def createNewGameCategory():
    if request.method == 'POST':
        gameGategory = GameCategory(name=request.form["categoryname"])
        dbOperations.addRecord(gameGategory)
        return render_template("index.html")
    else:
        return render_template('newcategory.html')

@app.route("/category/<string:gamecat_id>/new", methods=['GET', 'POST'])
def createNewGame(gamecat_id):
    if request.method == 'POST':
        game = Game(name=request.form["gamename"], description=request.form["description"], user_id=0, gamecategory_id=gamecat_id)
        dbOperations.addRecord(game)
        return render_template('index.html')
    else:
        return render_template('newgame.html')

# Delete endpoints

@app.route("/category/<string:game_id>/delete", methods=['GET', 'POST'])
def deleteSelectedGame(game_id):
    if request.method == 'POST':
        dbOperations.removeRecord(game_id)
        return render_template("games.html")
    else:
        return render_template("deletegame.html")

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
