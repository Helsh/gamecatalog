#!/usr/bin/python3
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from model import Base, User, Game, GameCategory


class DbOperations:
    def addRecord(self, item, session):
        # Add any record
        session.add(item)
        session.commit()

    def removeRecordById(self, game_id, session):
        # Find game by id and remove
        game = session.query(Game).filter_by(id=game_id).first()
        session.delete(game)
        session.commit()

    def findUserByEmail(self, user_email, session):
        # Find and return user or None
        user = session.query(User).filter_by(email=user_email).first()
        return user
