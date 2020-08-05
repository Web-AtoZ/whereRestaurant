import json
import urllib.request
from urllib import parse


from sqlalchemy import Column, String, Integer, TIMESTAMP, create_engine, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pytz import timezone


Base = declarative_base()
UTC = timezone('UTC')


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column('restaurant_id', Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    road_address = Column(String)
    address = Column(String)
    phone = Column(String)
    mapx = Column(Integer)
    mapy = Column(Integer)
    lng = Column(Integer)
    lat = Column(Integer)
    creat_date = Column('created_date', TIMESTAMP, default=datetime.now(UTC))
    update_date = Column('updated_date', TIMESTAMP)
    option = Column('option_name', String)
    option_id = Column('option_id', Integer)
    place_id = Column('place_id', String)

    def __init__(self, data):
        self.name = data.get('name')
        self.road_address = data.get('road_address')
        self.address = data.get('address')
        self.option = data.get('option')
        self.option_id = data.get('option_id')
        self.phone = data.get('phone')
        self.mapx = data.get('mapx')
        self.mapy = data.get('mapy')
        self.lng = data.get('lng')
        self.lat = data.get('lat')
        self.place_id = data.get('place_id')


SQLALCHEMY_DATABASE_URI = f"postgresql://"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()



place_url = 'https://map.naver.com/v5/api/search?query='



for restaurant in session.query(Restaurant).all() :
    url = place_url + parse.quote(restaurant.name)
    request = urllib.request.Request(url)
    res = urllib.request.urlopen(request)


    if res.getcode() != 200:
        continue

    response = json.loads(res.read().decode('utf-8'))

    if response['result']['type'] != 'place' :
        continue

    places = response['result']['place']['list']

    for place in places :
        print (f"==> {restaurant.name}  {restaurant.address}  {restaurant.road_address}  {restaurant.phone}")
        print (f"==> {place['name']} {place['address']}  {place['roadAddress']}  {place['telDisplay']}\n")

        if place['address'] == restaurant.address :
            session.query(Restaurant).filter_by(id=restaurant.id).update({Restaurant.place_id: place['id'],
                                                                          Restaurant.lng : place['x'],
                                                                          Restaurant.lat : place['y'],
                                                                          Restaurant.update_date: datetime.now(UTC)
                                                                          })
            break

        if place['roadAddress'] ==  restaurant.road_address :
            session.query(Restaurant).filter_by(id=restaurant.id).update({Restaurant.place_id: place['id'],
                                                                          Restaurant.lng : place['x'],
                                                                          Restaurant.lat : place['y'],
                                                                          Restaurant.update_date: datetime.now(UTC)
                                                                          })
            break

        if place['telDisplay'] ==  restaurant.phone :
            session.query(Restaurant).filter_by(id=restaurant.id).update({Restaurant.place_id: place['id'],
                                                                          Restaurant.lng : place['x'],
                                                                          Restaurant.lat : place['y'],
                                                                          Restaurant.update_date: datetime.now(UTC)
                                                                          })
            break


session.commit()
