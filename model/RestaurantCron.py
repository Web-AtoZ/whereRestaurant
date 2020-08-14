from datetime import datetime
from pytz import timezone
from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
UTC = timezone('UTC')


class RestaurantCron(Base):
    __tablename__ = 'restaurant_cron'

    id = Column('cron_id', Integer, primary_key=True, autoincrement=True)
    kwd = Column('keyword', String)
    now_count = Column('now_count', Integer)
    total_count = Column('total_count', Integer)
    creat_date = Column('created_date', TIMESTAMP, default=datetime.now(UTC))
    update_date = Column('updated_date', TIMESTAMP)

    def __init__(self, data):
        self.kwd = data.get('kwd')
        self.now_count = data.get('now_count')
        self.total_count = data.get('total_count')


    def __str__(self):
        return f"RestaurantCron : {self.id} {self.kwd} {self.now_count} {self.total_count}"