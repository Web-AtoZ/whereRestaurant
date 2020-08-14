from datetime import datetime
from pytz import timezone
from sqlalchemy import Column, String, Integer, TIMESTAMP
from base import Base

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
    option_id = Column('option_id', Integer)
    place_id = Column('place_id', String)


    def __init__(self, data):
        self.name = data.get('name')
        self.road_address = data.get('road_address')
        self.address = data.get('address')
        self.option_id = data.get('option_id')
        self.phone = data.get('phone')
        self.mapx = data.get('mapx')
        self.mapy = data.get('mapy')
        self.lng = data.get('lng')
        self.lat = data.get('lat')
        self.place_id = data.get('place_id')


    @classmethod
    def exist_chk(cls, session, place_id):
        return session.query(cls).filter_by(place_id=place_id).scalar() is None


    @classmethod
    def get_by_place_id(cls, session, place_id):
        return session.query(cls).filter_by(place_id=place_id).scalar()