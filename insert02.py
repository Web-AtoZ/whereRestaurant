import json
import urllib.parse as parse
import urllib.request
from datetime import datetime

from pytz import timezone
from sqlalchemy import create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from key import real, local
from model.menu import Menu
from model.option import Option
from model.restaurant import Restaurant
from model.restaurantcron import RestaurantCron

Base = declarative_base()
UTC = timezone('UTC')
_DISPLAY = 10  # max = 30
keyword = "신림" + "맛집"

mode = 'DEV'

SQLALCHEMY_DATABASE_URI = real if mode is 'REAL' else local

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

display = _DISPLAY

restaurant_cron = session.query(RestaurantCron).filter_by(kwd=keyword).first()

if restaurant_cron:
    if restaurant_cron.now_count == restaurant_cron.total_count:
        print("===============================\n")
        print("=== 모든 정보를 수집 했습니다 ===\n")
        print("===============================\n")
        quit()

page = 1 if restaurant_cron is None else int(restaurant_cron.now_count / display) + 1
encText = parse.quote(keyword)
url = "https://map.naver.com/v5/api/search?query=" + encText
url = f"{url}&type=all&page={page}&displayCount={display}"
request = urllib.request.Request(url)
response = urllib.request.urlopen(request)

if response.getcode() == 200:
    response_body = response.read().decode('utf-8')
    response_body = json.loads(response_body)
    result = response_body['result']

    if result['type'] != 'place':
        print("---------------ERR API")
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
                                                                               RestaurantCron.update_date: datetime.now(
                                                                                   UTC)
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

        now_restaurant = Restaurant.get_by_place_id(session, r['id'])

        if now_restaurant is None:
            now_restaurant = Restaurant({
                'name': r['name'],
                'road_address': r['roadAddress'],
                'address': r['address'],
                'option_id': option.id,
                'phone': r['telDisplay'] if r['telDisplay'] else r['tel'],
                'lng': r['x'],
                'lat': r['y'],
                'place_id': r['id']
            })
            session.add(now_restaurant)
            session.flush()
            print(f"=====> insert {r['name']}\n")

        elif session.query(Menu).filter_by(restaurant_id=now_restaurant.id) is not None:
            continue

        menus = []
        menu_arr = r['menuInfo'].split('|')
        for m in menu_arr:
            m = m.strip()
            m_arr = m.rsplit(' ', 1)
            if len(m_arr) is 2:
                menus.append({
                    'name': m_arr[0],
                    'price': m_arr[1],
                    'restaurant_id': now_restaurant.id
                })

        session.bulk_insert_mappings(Menu, menus)

    # session.commit()
    session.rollback()
else:
    print(f"Error Code:{response.getcode()}")
