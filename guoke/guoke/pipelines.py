# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from pprint import pprint


class GuokePipeline(object):
    def open_spider(self, spider):
        # 只在爬虫启动时执行一次
        client = MongoClient()
        self.collection = client["guoke"]["gk"]
        # self.f = open("guoke.txt", "a")

    def process_item(self, item, spider):
        pprint(item)
        self.collection.insert_one(item)
        return item

    def close_spider(self, spider):
        """只在爬虫结束时执行一次"""
        # self.f.close()
        pass
