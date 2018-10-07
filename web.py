#!/usr/bin/python3

# Imports

from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, g
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
from functools import wraps

# Import OAuth2 for Google

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

# Web application - Games catalog

# Connection with database

engine = create_engine('sqlite:///gamescatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)


dbOperations = DbOperations()
webHelper = WebHelper()

# Define Client ID

CLIENT_ID = json.loads(open(
    'client_secrets.json', 'r').read())['web']['client_id']

# Login / Logout endpoints (Google Accounts)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if login_session.get('email') is not None:
            return f(*args, **kwargs)
        return redirect(url_for('showMainPage'))
    return decorated_function


@app.route("/login")
def logIn():
    login_session['state'] = webHelper.generateRandomClientId(64)
    return render_template(
        'login.html', STATE=login_session['state'],
        loginstate=login_session.get('email'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validation of state
    if request.args.get('state') != login_session['state']:
        return webHelper.generateJsonDump('Invalid state parameter.', 401)

    # Obtain authorization code
    code = request.data

    try:
        # Authorization code used to obtain credentials
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return webHelper.generateJsonDump(
            'Failed to upgrade the authorization code.', 401)
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'
          ).format(access_token)
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
        return webHelper.generateJsonDump(
            "Token's user ID doesn't match given user ID.", 401)

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        return webHelper.generateJsonDump(
            "Token's client ID does not match app's.", 401)

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        return webHelper.generateJsonDump(
            'Current user is already connected.', 200)

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info via request
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # Sometimes we don't receive "name"
    # This case can be solved with adding email as name to db

    if data.get('name') is not None:
        login_session['username'] = data['name']
    else:
        login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check whether is user. If not then create new one in db.
    session = DBSession()
    user = dbOperations.findUserByEmail(login_session['email'], session)
    output = ""
    if user is None:
        user = User(
            name=login_session['username'], email=login_session['email'])
        dbOperations.addRecord(user, session)
        output += "{} {} {} \n {}{} {}".format(
            '<div style="display:table; margin: 0 auto;">'
            '<h1>Welcome,', user.name, '!</h1>',
            '<img src="', login_session['picture'],
            ' " style = "width: 150px; height: 150px;'
            'border-radius: 150px;-webkit-border-radius: 150px;'
            '-moz-border-radius: 150px;> </div>"')
    elif user is not None:
        output += "{} {} {} \n {}{} {}".format(
            '<div style="display:table; margin: 0 auto;">'
            '<h1>Welcome,', user.name, '!</h1>',
            '<img src="', login_session['picture'],
            ' " style = "width: 150px; height: 150px;'
            'border-radius: 150px;-webkit-border-radius: 150px;'
            '-moz-border-radius: 150px;> </div>"')
    else:
        output += 'An error regarding account occured.'

    return output


@app.route('/logout')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        return webHelper.generateJsonDump('Current user not connected.', 401)

    # Revoke current token

    url = (
        'https://accounts.google.com/o/oauth2/revoke?token={}'
          ).format(access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Clear data stored in session
        login_session.clear()
        return webHelper.generateJsonDump('Successfully disconnected.', 200)
    else:
        return webHelper.generateJsonDump(
            'Failed to revoke token for given user.', 400)

# Read endpoints


@app.route("/")
def showMainPage():
    session = DBSession()
    categories = session.query(GameCategory).all()
    return render_template(
        "index.html", categories=categories, loginstate=login_session.get(
            'email'))


@app.route("/category/<string:gamecat_id>/games")
def showSelectedGames(gamecat_id):
    session = DBSession()
    games = session.query(
        Game).filter_by(gamecategory_id=gamecat_id).all()
    return render_template(
        "games.html", games=games, loginstate=login_session.get('email'))


@app.route("/game/<string:game_id>")
def showSelectedGame(game_id):
    session = DBSession()
    user = dbOperations.findUserByEmail(login_session.get('email'), session)
    game = session.query(Game).filter_by(id=game_id).first()
    if user is not None:
        if user.id == game.user_id:
            return render_template(
                "authorizedgame.html", id=game_id,
                description=game.description, name=game.name,
                loginstate=login_session.get('email'))

    return render_template(
        "game.html", id=game_id, description=game.description,
        name=game.name, loginstate=login_session.get('email'))

# Create endpoints


@app.route("/category/new", methods=['GET', 'POST'])
@login_required
def createNewGameCategory():
    if request.method == 'POST':
        session = DBSession()
        gameGategory = GameCategory(name=request.form["categoryname"])
        dbOperations.addRecord(gameGategory, session)
        return redirect(url_for('showMainPage'))
    else:
        return render_template(
            'newcategory.html', loginstate=login_session.get('email'))


@app.route("/category/<string:gamecat_id>/new", methods=['GET', 'POST'])
@login_required
def createNewGame(gamecat_id):
    if request.method == 'POST':
        session = DBSession()
        user = dbOperations.findUserByEmail(
            login_session['email'], session)
        game = Game(
            name=request.form["gamename"],
            description=request.form["description"], user_id=user.id,
            gamecategory_id=gamecat_id)
        dbOperations.addRecord(game, session)
        return redirect(url_for(
            'showSelectedGames', gamecat_id=gamecat_id))
    else:
        return render_template(
            'newgame.html', loginstate=login_session.get('email'))


# Delete endpoints


@app.route("/games/<string:game_id>/delete", methods=['GET', 'POST'])
@login_required
def deleteSelectedGame(game_id):
    if request.method == 'POST':
        session = DBSession()
        user = dbOperations.findUserByEmail(
            login_session['email'], session)
        game = session.query(Game).filter_by(id=game_id).first()
        if user.id == game.user_id:
            gamecat_id = game.gamecategory_id
            dbOperations.removeRecordById(game_id, session)
            return redirect(url_for(
                'showSelectedGames', gamecat_id=gamecat_id))
        else:
            return render_template(
                "nopermissions.html",
                loginstate=login_session.get('email'))
    else:
        return render_template(
            "deletegame.html", loginstate=login_session.get('email'))

# Update endpoints


@app.route("/games/<string:game_id>/edit", methods=['GET', 'POST'])
@login_required
def editSelectedItem(game_id):
    if request.method == 'POST':
        session = DBSession()
        user = dbOperations.findUserByEmail(
            login_session['email'], session)
        game = session.query(Game).filter_by(id=game_id).first()
        if user.id == game.user_id:
            gamecat_id = game.gamecategory_id
            game.name = request.form["gamename"]
            game.description = request.form["description"]
            dbOperations.addRecord(game, session)
            return redirect(url_for(
                'showSelectedGames', gamecat_id=gamecat_id))
        else:
            return render_template(
                "nopermissions.html",
                loginstate=login_session.get('email'))
    else:
        return render_template(
            "editgame.html", loginstate=login_session.get('email'))


# API - Json


@app.route("/category/<int:category_id>/games.json")
def showContentInJson(category_id):
    session = DBSession()
    games = session.query(Game).filter_by(gamecategory_id=category_id)

    return jsonify(games=[g.serialize for g in games])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
