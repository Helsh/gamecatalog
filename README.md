## About project:
Games Catalog is a project developed for Udacity course. This project is a simple CRUD with very minimalistic frontend with raw HTML and CSS. It provides managing of games catalog with other users. Every user with Google account can participate in adding/delete/editing games in this application, but it's all restricted to managing your own created games, you are not authorized to delete or edit others games in categories!

## Requirements:

- Vagrant (+ download Vagrantfile from [Github](https://github.com/udacity/fullstack-nanodegree-vm/tree/master/vagrant))
- Google account (for purpose of testing OAuth2 authentication)
- Replace CLIENT_ID with your own one in web.py (you should import Google secrets json file as **client_secrets.json** and put in main folder where **web.py** is placed), **login.html** (where sign-in button is placed, there is option called data-clientid which should be replaced). 
[Here](https://console.developers.google.com/apis) you can obtain your own secrets file with your own ClientID.
- Python 3

## Frameworks:

- SQLAlchemy (ORM)
- Flask

## Special endpoints:

- localhost:8000/category/new allows every logged user to create new game category
- localhost:8000/category/id/games.json where id is a game category id, if it exists then it will show you json output with every game created in the category

## How to run

- Go to the main catalog.
- Type: python3/python web.py
- To create new database please run model.py (python3/python model.py)

## Project structure

- web.py - main file, it contains definitions of every apis endpoints in applications. Also is responsible for backend implementation of Google OAuth2 backend solution.
- model.py - it's core model for application's database
- WebHelper.py - supporting class which provides generating random ids and json dumps
- DbOperations.py - supporting class which provides very generic operations on database
- login.html - template which contains frontend/ajax solution for OAuth2
- /templates - catalog containing all views
- /static - responsible for static files such as CSS

## Worth to know

- Project follows PEP8 Code style
- CSS files are stored in /static catalog
- Views are stored in /templates catalog



