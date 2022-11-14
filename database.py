from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


"""
Database to store ingredient pairs and a number of their occurrences
"""
Base = declarative_base()
engine = create_engine("sqlite:///ingredients.db")
session = sessionmaker(bind=engine)


class Ingredients(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True)
    ingredient = Column(String)
    pairing = Column(String)
    count = Column(Integer)


Base.metadata.create_all(bind=engine)