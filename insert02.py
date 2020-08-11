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
_DISPLAY = 30 # max = 30
keyword = "당곡사거리" + "맛집"



def chk(place_id):
    return session.query(Restaurant).filter_by(place_id=place_id).scalar() is None


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


SQLALCHEMY_DATABASE_URI = f"postgresql://usrname:passwd@34.64.77.138:5432/db명"

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

display = _DISPLAY

restaurant_cron = session.query(RestaurantCron).filter_by(kwd=keyword).first()


if restaurant_cron :
    if restaurant_cron.now_count == restaurant_cron.total_count :
        print ("===============================\n")
        print ("=== 모든 정보를 수집 했습니다 ===\n")
        print ("===============================\n")
        quit()

page = 1 if restaurant_cron is None else int(restaurant_cron.now_count/display) + 1
encText = parse.quote(keyword)
url = "https://map.naver.com/v5/api/search?query=" + encText
url = f"{url}&type=all&page={page}&displayCount={display}"
request = urllib.request.Request(url)
response = urllib.request.urlopen(request)


print (f"{url}\n")

if response.getcode() == 200:
    response_body = response.read().decode('utf-8')
    response_body = json.loads(response_body)
    result = response_body['result']

    if result['type'] != 'place' :
        print ("---------------ERR API")
        quit()


    total = result['place']['totalCount']
    new_counet = len(result['place']['list'])


    if restaurant_cron is None:  # insert
        restaurant_cron = RestaurantCron({
            'kwd': keyword,
            'total_count': total,
            'now_count': new_counet,
        })
        session.add(restaurant_cron)
    else:  # update
        session.query(RestaurantCron).filter_by(id=restaurant_cron.id).update({RestaurantCron.total_count: total,
                                                                               RestaurantCron.now_count: restaurant_cron.now_count + new_counet,
                                                                               RestaurantCron.update_date: datetime.now(UTC)
                                                                               })

    restaurant = result['place']['list']

    for r in restaurant:
        opt_nm_arr = r['category']

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



        if chk( r['id']):
            data = {
                'name': r['name'],
                'road_address': r['roadAddress'],
                'address': r['address'],
                'option_id': option.id,
                'phone':  r['telDisplay'] if r['telDisplay'] else r['tel'],
                'lng': r['x'],
                'lat': r['y'],
                'place_id' : r['id']
            }
            session.add(Restaurant(data))
            print (f"=====> insert {r['name']}\n")
    session.commit()
    # session.rollback()
else:
    print("Error Code:" + response.getcode())
