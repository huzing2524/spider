# -*- coding: utf-8 -*-
from pprint import pprint
import scrapy


class GkSpider(scrapy.Spider):
    name = 'gk'
    allowed_domains = ['guokr.com']
    start_urls = ['https://www.guokr.com/ask/highlight/']

    def parse(self, response):
        li_list = response.xpath("//ul[@class='ask-list-cp']/li")
        for li in li_list:
            item = dict()
            item["focus_nums"] = li.xpath(".//p[@class='ask-focus-nums']/span/text()").extract_first()
            item["answer_nums"] = li.xpath(".//p[@class='ask-answer-nums']/span/text()").extract_first()
            item["title"] = li.xpath(".//h2/a/text()").extract_first()
            item["href"] = li.xpath(".//h2/a/@href").extract_first()
            item["summary"] = li.xpath(".//p[@class='ask-list-summary']/text()").extract_first().strip()
            item["tag"] = li.xpath(".//a[@class='tag']/text()").extract()
            # 进入详情页
            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail,
                meta={"item": item}
            )

        # 请求下一页
        next_url = response.xpath("//a[text()='下一页']/@href").extract_first()
        if next_url is not None:
            yield response.follow(next_url, callback=self.parse)

    def parse_detail(self, response):
        item = response.meta["item"]
        # 对回答进行分组，每组进行数据提取
        div_list = response.xpath("//div[contains(@class, 'answer gclear')]")
        answer_list = []
        for div in div_list:
            one_answer = dict()
            one_answer["user_name"] = div.xpath(".//a[@class='answer-usr-name']").extract_first()
            one_answer["support_num"] = div.xpath(".//span[@class='answer-digg-num']/text()").extract_first()
            one_answer["content"] = div.xpath(".//div[@class='answer-txt answerTxt gbbcode-content']//text()").extract()
            answer_list.append(one_answer)

        item["answer_list"] = answer_list
        # pprint(item)
        yield item
