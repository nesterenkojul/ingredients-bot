from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///recipes.db")
tracker_session = sessionmaker(bind=engine)


class Recipes(Base):
    __tablename__ = "recipe"
    id = Column(Integer, primary_key=True)
    recipe_page = Column(Integer)


Base.metadata.create_all(bind=engine)