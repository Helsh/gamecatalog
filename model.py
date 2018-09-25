#!/usr/bin/python3
from sqlalchemy import Column,Integer,String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(20), nullable = False)
    email = Column(String(80), nullable = False)

class GameCategory(Base):
    __tablename__ = 'gamecategory'

    id = Column(Integer, primary_key = True)
    name = Column(String(20), nullable = False)

class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    description = Column(String(255))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    gamecategory_id = Column(Integer, ForeignKey('gamecategory.id'))
    gamecategory = relationship(GameCategory)



engine = create_engine('sqlite:///gamescatalog.db')

Base.metadata.create_all(engine)
