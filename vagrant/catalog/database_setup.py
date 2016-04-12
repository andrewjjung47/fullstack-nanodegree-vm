from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import flask.ext.login as flask_login
 
Base = declarative_base()

# UserMixin for functions required by Flask login
class User(flask_login.UserMixin, Base):
    __tablename__= 'user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    __tablename__ = 'category'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    items = relationship("Item")
    @property
    def serialize(self):
       return {
           'name'         : self.name,
           'id'         : self.id,
           'items': [i.serialize for i in self.items]
       }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category")
    user_id = Column(Integer, ForeignKey('user.id'))
    user_relationship = relationship("User")


    @property
    def serialize(self):
       return {
           'name'         : self.name,
           'description'         : self.description,
           'id'         : self.id,
           'category'         : self.category.name
       }



engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)
