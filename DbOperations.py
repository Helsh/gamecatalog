from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, User, Game, GameCategory

engine = create_engine('sqlite:///gamescatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

class DbOperations:
    def addRecord(self, item):
        session.add(item)
        session.commit()

    def removeRecord(self, game_id):
        game = session.query(Game).filter_by(id = game_id).first()
        session.delete(game)
        session.commit()

    # def showRecords(self, Type, filter=None, filter_data=None):
    #     if filter == None and filter_data == None:
    #         return session.query(Type).all()
    #     else:
    #         return session.query(Type).filter_by(filter = filter_data).all()
