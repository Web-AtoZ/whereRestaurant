from datetime import datetime
from pytz import timezone
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from base import Base

UTC = timezone('UTC')


class Menu(Base):
    __tablename__ = 'menu'

    id = Column('menu_id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    price = Column('price', String)
    restaurant_id = Column('restaurant_id', Integer, ForeignKey('restaurant.restaurant_id'))


    restaurant = relationship('Restaurant', backref=backref('restaurant'))

    def __init(self, data):
        self.name = data.get('name')
        self.price = data.get('price')
        self.restaurant_id = data.get('restaurant_id')
