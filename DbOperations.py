from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, User, Game, GameCategory

engine = create_engine('sqlite:///gamescatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class DbOperations:
    def addRecord(self, item):
        # Add any record
        session.add(item)
        session.commit()

    def removeRecordById(self, game_id):
        # Find game by id and remove
        game = session.query(Game).filter_by(id = game_id).first()
        session.delete(game)
        session.commit()

    def findUserByEmail(self, user_email):
        # Find and return user or None
        user = session.query(User).filter_by(email = user_email).first()
        return user

