#!/usr/bin/python3

#Imports

from flask import Flask, render_template, request, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, User, Game, GameCategory
from DbOperations import DbOperations
import httplib2
import json
from flask import make_response
import requests
from WebHelper import WebHelper

# Import OAuth2 for Google

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

# Web application - Games catalog

# Connection with database

engine = create_engine('sqlite:///gamescatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

dbOperations = DbOperations()
webHelper = WebHelper()

# Define Client ID

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Login / Logout endpoints (Google Accounts)

@app.route("/login")
def logIn():
    login_session['state'] = webHelper.generateRandomClientId(64)
    return render_template('login.html', STATE=login_session['state'])

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        return webHelper.generateJsonDump('Invalid state parameter.', 401)
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return webHelper.generateJsonDump('Failed to upgrade the authorization code.', 401)
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}').format(access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return webHelper.generateJsonDump("Token's user ID doesn't match given user ID.", 401)

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        return webHelper.generateJsonDump("Token's client ID does not match app's.", 401)

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        return webHelper.generateJsonDump('Current user is already connected.', 200)

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # revoke current token
    # access_token = credentials.access_token
    print("{}{}{}".format("start:", access_token, ":end"))
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(access_token)
    # print(url)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is {}'.format(result))
    print(result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route("/logout")
def logOut():

    return ""

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
        return redirect(url_for('showMainPage'))
    else:
        return render_template('newcategory.html')

@app.route("/category/<string:gamecat_id>/new", methods=['GET', 'POST'])
def createNewGame(gamecat_id):
    if request.method == 'POST':
        game = Game(name=request.form["gamename"], description=request.form["description"], user_id=0, gamecategory_id=gamecat_id)
        dbOperations.addRecord(game)
        return redirect(url_for('showSelectedGames', gamecat_id = gamecat_id))
    else:
        return render_template('newgame.html')

# Delete endpoints

@app.route("/games/<string:game_id>/delete", methods=['GET', 'POST'])
def deleteSelectedGame(game_id):
    if request.method == 'POST':
        game = session.query(Game).filter_by(id = game_id).first()
        gamecat_id = game.gamecategory_id
        dbOperations.removeRecordById(game_id)
        return redirect(url_for('showSelectedGames', gamecat_id = gamecat_id))
    else:
        return render_template("deletegame.html")

# Update endpoints

@app.route("/games/<string:game_id>/edit", methods=['GET', 'POST'])
def editSelectedItem(game_id):
    if request.method == 'POST':
        game = session.query(Game).filter_by(id = game_id).first()
        gamecat_id = game.gamecategory_id
        game.name = request.form["gamename"]
        game.description = request.form["description"]
        session.add(game)
        session.commit()
        return redirect(url_for('showSelectedGames', gamecat_id = gamecat_id))
    else:
        return render_template("editgame.html")

# API - Json

@app.route("/category.json")
def showContentInJson():

    return ""

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
