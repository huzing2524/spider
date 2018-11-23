# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
from pymongo import MongoClient

client = MongoClient()
# collection = client["book"]["suning"]
collection = client["book"]["jingdong"]


class DangDangPipeline(object):
    def process_item(self, item, spider):
        if spider.name == "dangdang":
            item["b_cate"] = "".join([i.strip() for i in item["b_cate"]])
            item["m_cate"] = "".join([i.strip() for i in item["m_cate"]])
            print(item)
        return item


class AmazonPipline:
    def process_item(self, item, spider):
        if spider.name == "amazon":
            item["book_cate"] = [i.strip() for i in item["book_cate"]]
            item["book_desc"] = item["book_desc"].split("<br><br>")[0].split("<br>")
            item["book_desc"] = [re.sub("<div>|</div>|<em>|</em>|\s+|\xa0|<p>|</p>", "", i) for i in item["book_desc"]]
            print(item)
        return item


class JDPipline:
    def process_item(self, item, spider):
        if spider.name == "jd":
            # print(type(item))  # dict
            item['_id'] = item['book_sku']
            collection.insert(item)
        return item
