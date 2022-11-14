from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


"""
Database to store ids of recipes, 
ingredients from which have already been extracted,
in order to not visit them again.
"""
Base = declarative_base()
engine = create_engine("sqlite:///recipes.db")
tracker_session = sessionmaker(bind=engine)


class Recipes(Base):
    __tablename__ = "recipe"
    id = Column(Integer, primary_key=True)
    recipe_page = Column(Integer)


Base.metadata.create_all(bind=engine)