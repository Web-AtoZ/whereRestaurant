import json
import urllib.parse as parse
import urllib.request
from datetime import datetime

from pytz import timezone
from sqlalchemy import Column, String, Integer, TIMESTAMP, create_engine, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
UTC = timezone('UTC')


def 중복_chk(name, mapx, mapy):
    return session.query(Restaurant).filter_by(name=name, mapx=mapx, mapy=mapy).scalar() is None




class Option(Base):
    __tablename__ = 'option'

    id = Column('option_id', Integer, primary_key=True, autoincrement=True)
    level = Column('level', Integer)
    order = Column('order', Integer)
    des = Column('description', Integer)
    p_id = Column('p_option_id', Integer, ForeignKey('option.option_id'), nullable=True)
    creat_date = Column('created_date', TIMESTAMP, default=datetime.now(UTC))

    p = relationship('Option', remote_side = [id])


    def __init__(self, data):
        self.level = data.get('level')
        self.order = data.get('order')
        self.des = data.get('des')
        self.p_id = data.get('p_id')



class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column('restaurant_id', Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    road_address = Column(String)
    address = Column(String)
    phone = Column(String)
    mapx = Column(Integer)
    mapy = Column(Integer)
    creat_date = Column('created_date', TIMESTAMP, default=datetime.now(UTC))
    option = Column('option_name', String)
    option_id = Column('option_id', Integer)

    def __init__(self, data):
        self.name = data.get('name')
        self.road_address = data.get('road_address')
        self.address = data.get('address')
        self.option = data.get('option')
        self.option_id = data.get('option_id')
        self.phone = data.get('phone')
        self.mapx = data.get('mapx')
        self.mapy = data.get('mapy')


SQLALCHEMY_DATABASE_URI = f"postgresql://usrname:passwd@34.64.77.138:5432/db명"

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

client_id = ""
client_secret = ""
keyword = "샤로수길 맛집"
display = 10
start = 1
sort = "comment"
encText = parse.quote(keyword)
url = "https://openapi.naver.com/v1/search/local.json?query=" + encText
url = f"{url}&display={display}&start={start}&sort={sort}"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)
response = urllib.request.urlopen(request)
if (response.getcode() == 200):
    response_body = response.read().decode('utf-8')
    response_body = json.loads(response_body)
    restaurant = response_body['items']


    for r in restaurant:
        print (r)

        opt_nm_arr = r['category'].split('>')

        for index, opt_nm in enumerate(opt_nm_arr):
            if index == 0:
                p_option = session.query(Option).filter_by(des=opt_nm).first()

                if p_option is None:
                    last_option = session.query(Option).filter_by(level=0).order_by(desc(Option.order)).first()
                    order = last_option.order if last_option else 0
                    p_option = Option({
                        'level': 0,
                        'order': order + 10,
                        'des': opt_nm
                    })

                    session.add(p_option)
                    session.flush()

            else:
                option = session.query(Option).filter_by(des=opt_nm).first()

                if option is None:
                    last_option = session.query(Option).filter_by(p_id=p_option.id).order_by(desc(Option.order)).first()
                    order = last_option.order if last_option else 0
                    option = Option({
                        'level': p_option.level + 1,
                        'order': order + 10,
                        'des': opt_nm,
                        'p_id': p_option.id
                    })
                    session.add(option)
                    session.flush()

        if 중복_chk(r['title'], r['mapx'], r['mapy']):
            data = {
                'name': r['title'].replace('<b>', '').replace('</b>', ''),
                'road_address': r['roadAddress'],
                'address': r['address'],
                'option': r['category'],
                'option_id' : option.id,
                'phone': r['telephone'],
                'mapx': r['mapx'],
                'mapy': r['mapy'],
            }
            session.add(Restaurant(data))
    session.commit()
else:
    print("Error Code:" + response.getcode())
