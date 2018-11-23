# -*- coding: utf-8 -*-
import scrapy

from ..items import YangguangItem


class YgSpider(scrapy.Spider):
    name = 'yg'
    allowed_domains = ['wz.sun0769.com']
    start_urls = ['http://wz.sun0769.com/index.php/question/questionType?type=4&page=0']

    def parse(self, response):
        """提取列表页的数据"""
        # 1.提取当前页的数据，先分组，再提取
        tr_list = response.xpath("//div[@class='greyframe']/table[2]/tr/td/table/tr")
        for tr in tr_list:
            item = YangguangItem()
            item["num"] = tr.xpath("./td[1]/text()").extract_first()
            item["title"] = tr.xpath("./td[2]/a[2]/text()").extract_first()
            item["href"] = tr.xpath("./td[2]/a[2]/@href").extract_first()
            item["status"] = tr.xpath("./td[3]/span/text()").extract_first()
            item["name"] = tr.xpath("./td[4]/text()").extract_first()
            item["publish_date"] = tr.xpath("td[5]/text()").extract_first()
            # 构建Request对象，每次遍历时候把主页的每条数据生成request，获得response后传递到parse_detail()接收，继续请求获取对应详情页的数据
            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail,
                meta={"key": item}
            )

        # 2.构造下一页的请求，翻页
        next_url = response.xpath("//a[text()='>']/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_detail(self, response):
        """提取详情页的数据"""
        item = response.meta["key"]
        item["img"] = response.xpath("//div[@class='textpic']/img/@src").extract_first()
        # 文本内容有多个换行，结果有多个
        item["content"] = response.xpath("//div[@class='c1 text14_2']//text()").extract()
        yield item
