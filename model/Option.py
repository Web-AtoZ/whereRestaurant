from datetime import datetime
from pytz import timezone
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()
UTC = timezone('UTC')


class Option(Base):
    __tablename__ = 'option'

    id = Column('option_id', Integer, primary_key=True, autoincrement=True)
    level = Column('level', Integer)
    order = Column('order', Integer)
    des = Column('description', Integer)
    p_id = Column('p_option_id', Integer, ForeignKey('option.option_id'), nullable=True)
    creat_date = Column('created_date', TIMESTAMP, default=datetime.now(UTC))

    p = relationship('Option', remote_side=[id])

    def __init__(self, data):
        self.level = data.get('level')
        self.order = data.get('order')
        self.des = data.get('des')
        self.p_id = data.get('p_id')