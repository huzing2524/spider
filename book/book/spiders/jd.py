# -*- coding: utf-8 -*-

import scrapy
import json

from copy import deepcopy
# from ..items import JDItem


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com', 'p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        """提取所有的大分类和对应的小分类"""
        dt_list = response.xpath("//div[@class='mc']/dl/dt")
        for dt in dt_list:
            # item = JDItem()
            item = dict()
            # 大分类的名字：小说、文学
            item["b_cate"] = dt.xpath("./a/text()").extract_first()
            # 获取小分类的分组：小说(中国当代小说/中国近现代小说)
            em_list = dt.xpath("./following-sibling::*[1]/em")
            for em in em_list:
                # 小分类的地址
                item["s_href"] = "https:" + em.xpath("./a/@href").extract_first()
                # 小分类的名字
                item["s_cate"] = em.xpath("./a/text()").extract_first()
                # 进入图书列表页
                yield scrapy.Request(
                    item["s_href"],
                    callback=self.parse_book_list,
                    meta={"item": deepcopy(item)}
                )

    def parse_book_list(self, response):
        """提取图书列表页数据"""
        item = response.meta["item"]
        # 所有图书的列表
        li_list = response.xpath("//div[@id='plist']/ul/li")
        for li in li_list:
            item["book_name"] = li.xpath(".//div[@class='p-name']/a/em/text()").extract_first().strip()
            item["book_author"] = li.xpath(".//span[@class='p-bi-name']/span/a/text()").extract()
            item["book_press"] = li.xpath(".//span[@class='p-bi-store']/a/text()").extract_first()
            item["book_publisth_date"] = li.xpath(".//span[@class='p-bi-date']/text()").extract_first().strip()
            item["book_sku"] = li.xpath("./div/@data-sku").extract_first()
            # 发送价格的请求，获取价格
            price_url_temp = "https://p.3.cn/prices/mgets?ext=11000000&pin=&type=1&area=1_72_4137_0&skuIds=J_{}"
            price_url = price_url_temp.format(item["book_sku"])

            yield scrapy.Request(
                price_url,
                callback=self.parse_book_price,
                meta={"item": deepcopy(item)}
            )

        # 翻页
        next_url = response.xpath("//a[@class='pn-next']/@href").extract_first()
        if next_url is not None:
            yield response.follow(
                next_url,
                callback=self.parse_book_list,
                meta={"item": item}
            )

    def parse_book_price(self, response):
        """请求获取图书价格"""
        item = response.meta["item"]
        item["book_price"] = json.loads(response.body.decode())[0]["op"]
        # print(item)
        yield item
