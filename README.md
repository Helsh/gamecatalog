## About project:
Games Catalog is a project developed for Udacity course. This project is a simple CRUD with very minimalistic frontend with raw HTML and CSS. It provides managing of games catalog with other users. Every user with Google account can participate in adding/delete/editing games in this application, but it's all restricted to managing your created games, you are not authorized to delete or edit others games in categories!

## Requirements:

- Vagrant (+ download Vagrantfile from [Github](https://github.com/udacity/fullstack-nanodegree-vm/tree/master/vagrant))
- Google account (for purpose of testing OAuth2 authentication)

## Frameworks:

- SQLAlchemy (ORM)
- Flask

## Special endpoints:

- localhost:8000/category/new allows every logged user to create new game category
- localhost:8000/category/id/games.json where id is a game category id, if it exists then it will show you json output with every game created in the category


