# -*- coding: utf-8 -*-
import scrapy
import urllib.parse


class TtSpider(scrapy.Spider):
    name = 'tt'
    allowed_domains = ['hr.tencent.com']
    start_urls = ['https://hr.tencent.com/position.php?&start=#a0']

    def parse(self, response):
        # 1.提取当前页面数据
        tr_list = response.xpath("//table[@class='tablelist']/tr")[1:-1]
        for tr in tr_list:
            item = {}
            item["position_name"] = tr.xpath("./td[1]/a/text()").extract_first()
            item["position_href"] = tr.xpath("./td[1]/a/@href").extract_first()
            item["position_cate"] = tr.xpath("./td[2]/text()").extract_first()
            item["need_num"] = tr.xpath("./td[3]/text()").extract_first()
            item["location"] = tr.xpath("./td[4]/text()").extract_first()
            item["publish_date"] = tr.xpath("./td[5]/text()").extract_first()
            yield item

        # 2.翻页，请求下一页数据
        next_url = response.xpath("//a[@id='next']/@href").extract_first()
        # 判断是不是下一页，最后一页的href不一样
        if next_url != "javascript:;":
            # response.follow() 可以把url地址按照start_urls进行拼接
            yield response.follow(next_url, callback=self.parse)
