#!/usr/bin/python3
from flask import Flask

app = Flask(__name__)

# Web application - Games catalog

# Read endpoints

@app.route("/")
def showMainPage():

    return ""

@app.route("/catalog/<string:category>/items")
def showSelectedItems():

    return ""

@app.route("/catalog/<string:category>/<string:item>")
def showSelectedItem():

    return ""

# Create endpoints

@app.route("/catalog/<string:item>/new")
def createNewItem():

    return ""

# Delete endpoints

@app.route("/catalog/<string:item>/delete")
def deleteSelectedItem():

    return ""

# Update endpoints

@app.route("/catalog/<string:item>/edit")
def editSelectedItem():

    return ""

# API - Json

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)
