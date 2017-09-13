# -*- coding: utf-8 -*-
import scrapy


class EllimanSpider(scrapy.Spider):
    name = "elliman"
    allowed_domains = ["elliman.com"]
    start_urls = (
        'http://www.elliman.com/',
    )

    def parse(self, response):
        pass
