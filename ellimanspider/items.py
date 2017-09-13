# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EllimanspiderItem(scrapy.Item):
	# define the fields for your item here like:
	full_name = scrapy.Field()
	last_name = scrapy.Field()
	first_name = scrapy.Field()
	full_address = scrapy.Field()
	address1 = scrapy.Field()
	address2 = scrapy.Field()
	address3 = scrapy.Field()
	address4 = scrapy.Field()
	office = scrapy.Field()
	mobile = scrapy.Field()
	fax = scrapy.Field()
	email = scrapy.Field()
	picture = scrapy.Field()
	url = scrapy.Field()
	start = scrapy.Field()
	picture_file_name = scrapy.Field()
	
