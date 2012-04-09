from pymongo import Connection
import requests
import json

import gevent
import gevent.monkey ; gevent.monkey.patch_all()
import gevent.pool

from hashlib import sha1

CONFIG = {
    'KEY': 'd24dd9c4e83213b5722c92ff5a77777f',
    'MAPPING': {
        'movie': 'http://tu.video.qiyi.com/tvx/mcategory/_E7_94_B5_E5_BD_B1/1/2/%s/%s/1,2,3/%s/',
        'teleplay': 'http://tu.video.qiyi.com/tvx/mcategory/_E7_94_B5_E8_A7_86_E5_89_A7/1/2/%s/%s/1,2,3/%s/',
        'comic': 'http://tu.video.qiyi.com/tvx/mcategory/_E5_8A_A8_E6_BC_AB/1/2/%s/%s/1,2,3/%s/',
        'variety': 'http://tu.video.qiyi.com/tvx/mcategory/_E7_BB_BC_E8_89_BA/1/2/%s/%s/1,2,3/%s/', 
        'documentary': 'http://tu.video.qiyi.com/tvx/mcategory/_E7_BA_AA_E5_BD_95_E7_89_87/1/2/%s/%s/1,2,3/%s/',
        'music': 'http://tu.video.qiyi.com/tvx/mcategory/_E9_9F_B3_E4_B9_90/1/2/%s/%s/1,2,3/%s/',
        'entertainment': 'http://tu.video.qiyi.com/tvx/mcategory/_E5_A8_B1_E4_B9_90/1/2/%s/%s/1,2,3/%s/',
        'trailer_movie': 'http://tu.video.qiyi.com/tvx/mcategory/_E7_89_87_E8_8A_B1_2C_E7_94_B5_E5_BD_B1/1/2/%s/%s/1,2,3/%s/',
        'trailer_teleplay': 'http://tu.video.qiyi.com/tvx/mcategory/_E7_89_87_E8_8A_B1_2C_E7_94_B5_E8_A7_86_E5_89_A7/1/2/%s/%s/1,2,3/%s/',
        'shiyun': 'http://tu.video.qiyi.com/tbox/mcategory/_E8_81_94_E6_83_B3_E5_90_88_E4_BD_9C_2C/1/2/%s/%s/1,2,3/%s/',
        },
    'SUBMAPPING': 'http://tu.video.qiyi.com/tbox/album/%s/%s/',
}

def fetch_channel(channel):
    page = 1
    limit = 1000
    items = []

    url = CONFIG["MAPPING"][channel] % (page, limit, CONFIG["KEY"])
    r = requests.get(url)
    obj = json.loads(r.content)

    items.extend(obj['data'])
    total = int(obj['total'])

    while len(items) < total:
        page += 1
        url = CONFIG["MAPPING"][channel] % (page, limit, CONFIG["KEY"])
        r = requests.get(url)
        obj = json.loads(r.content)
        items.extend(obj['data'])

    return channel, items


def fetch_all_channels(db, pool):
    jobs = [pool.spawn(fetch_channel, channel) 
            for channel in CONFIG["MAPPING"]]
    pool.join()

    for job in jobs:
        channel, items = job.value
        collection = db[channel]
        collection.insert(items, save=True)

def fetch_subitems(item):
    albumId = item["albumId"]
    url = CONFIG["SUBMAPPING"] % (albumId, CONFIG["KEY"])
    r = requests.get(url)
    obj = json.loads(r.content)
    subitems = obj["data"]
    item["ismartv_subitems"] = subitems
    return item

def fetch_all_subitems(db, pool):
    for channel in ('teleplay', 'documentary', 'comic'):
        collection = db[channel]
        jobs = [pool.spawn(fetch_subitems, item) for item in collection.find()]
        pool.join()
        for job in jobs:
            item = job.value 
            collection.save(item, save=True)



if __name__ == '__main__':
    conn = Connection()
    db = conn.media_qiyi_1
    fetch_all_channels(db, gevent.pool.Pool(20))
    fetch_all_subitems(db, gevent.pool.Pool(20))
