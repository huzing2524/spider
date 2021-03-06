# -*- coding: utf-8 -*-
import re
from copy import deepcopy

import scrapy


class SuningSpider(scrapy.Spider):
    name = 'suning'
    allowed_domains = ['suning.com']
    start_urls = ['https://book.suning.com/']

    def parse(self, response):
        """获取大分类的分组"""
        # 大分类
        div_list = response.xpath("//div[@class='menu-list']/div[@class='menu-item']")
        # 子菜单分类
        div_sub_list = response.xpath("//div[@class='menu-list']/div[@class='menu-sub']")
        for div in div_list:
            item = dict()
            # 大分类的名字
            item["b_cate"] = div.xpath(".//h3/a/text()").extract_first()
            # 当前大分类的所有的中间分类的位置
            current_sub_div = div_sub_list[div_list.index(div)]
            # 获取中间分类的分组
            p_list = current_sub_div.xpath(".//div[@class='submenu-left']/p[@class='submenu-item']")
            for p in p_list:
                # 中间分类的名字
                item["m_cate"] = p.xpath("./a/text()").extract_first()  # 小说
                # 获取小分组的分组
                li_list = p.xpath("./following-sibling::ul[1]/li")
                for li in li_list:
                    # 小分类的名字
                    item["s_cate"] = li.xpath("./a/text()").extract_first()
                    item["s_href"] = li.xpath("./a/@href").extract_first()
                    # 请求图书的列表页
                    yield scrapy.Request(
                        item["s_href"],
                        callback=self.parse_book_list,
                        meta={"item": deepcopy(item)}
                    )

                    # 发送请求，获取列表页第一页后一部分的数据
                    next_part_url_temp = "https://list.suning.com/emall/showProductList.do?ci={}&pg=03&cp=0&il=0&iy=0&adNumber=0&n=1&ch=4&sesab=ABBAAA&id=IDENTIFYING&cc=010&paging=1&sub=0"
                    ci = item["s_href"].split("-")[1]
                    next_part_url = next_part_url_temp.format(ci)
                    yield scrapy.Request(
                        next_part_url,
                        callback=self.parse_book_list,
                        meta={"item": deepcopy(item)}
                    )

    def parse_book_list(self, response):
        """处理图书列表页的内容"""
        item = response.meta["item"]
        # 获取图书列表页的分组
        li_list = response.xpath("//li[contains(@class, 'product      book')]")
        for li in li_list:
            # 书名
            item["book_name"] = li.xpath(".//p[@class='sell-point']/a/text()").extract_first().strip()
            # 书的url地址，不完整
            item["book_href"] = li.xpath(".//p[@class='sell-point']/a/@href").extract_first()
            # 书店名
            item["book_store_name"] = li.xpath(".//p[contains(@class, 'seller oh no-more')]/a/text()").extract_first()
            # 发送详情页的请求
            yield response.follow(
                item["book_href"],
                callback=self.parse_book_detail,
                meta={"item": deepcopy(item)}
            )

    def parse_book_detail(self, response):
        """处理图书详情页内容"""
        item = response.meta["item"]
        price_temp_url = "https://pas.suning.com/nspcsale_0_000000000{}_000000000{}_{}_10_010_0100101_226503_1000000_9017_10106____{}_{}.html"
        p1 = response.url.split("/")[-1].split(".")[0]
        p3 = response.url.split("/")[-2]
        p4 = re.findall('"catenIds":"(.*?)",', response.body.decode())
        if len(p4) > 0:
            p4 = p4[0]
            p5 = re.findall('"weight":"(.*?)",', response.body.decode())[0]
            price_url = price_temp_url.format(p1, p1, p3, p4, p5)

            yield scrapy.Request(
                price_url,
                callback=self.parse_book_price,
                meta={"item": item}
            )

    def parse_book_price(self, response):
        # 请求图书价格
        item = response.meta["item"]
        item["book_price"] = re.findall('"netPrice":"(.*?)"', response.body.decode())[0]
        yield item
