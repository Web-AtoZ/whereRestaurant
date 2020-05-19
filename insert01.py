import json
import urllib.parse as parse
import urllib.request
from datetime import datetime

from pytz import timezone
from sqlalchemy import Column, String, Integer, TIMESTAMP, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
UTC = timezone('UTC')


def 중복_chk(name, mapx, mapy) :
  return session.query(Restaurant).filter_by(name=name, mapx=mapx, mapy=mapy).scalar() is None


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


  def __init__(self, data):
    self.name = data.get('name')
    self.road_address = data.get('road_address')
    self.address = data.get('address')
    self.option = data.get('option')
    self.phone = data.get('phone')
    self.mapx = data.get('mapx')
    self.mapy = data.get('mapy')



SQLALCHEMY_DATABASE_URI = f"postgresql://usrname:passwd@34.64.77.138:5432/db명"
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# https://developers.naver.com/docs/search/blog/
client_id = ""
client_secret = ""
keyword = "압구정 맛집"
display = 30
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

  for r in restaurant :
    if 중복_chk(r['title'], r['mapx'], r['mapy']) :
      data = {
        'name':r['title'],
        'road_address': r['roadAddress'],
        'address': r['address'],
        'option': r['category'],
        'phone': r['telephone'],
        'mapx': r['mapx'],
        'mapy': r['mapy'],
      }
      session.add(Restaurant(data))
  session.commit()
else:
  print("Error Code:" + response.getcode())
