# -*- coding: utf-8 -*-
import scrapy
import random, base64
import re
import os
import json
import sys
import csv
import proxylist
import useragent
from scrapy.http import Request, FormRequest
from ellimanspider.items import EllimanspiderItem

reload(sys)  
sys.setdefaultencoding('utf8')

class EllimanSpider(scrapy.Spider):
	name = "elliman"
	# allowed_domains = ["elliman.com"]
	start_urls = [
		'https://www.elliman.com/agents/new-york-city',
		'https://www.elliman.com/agents/long-island',
		'https://www.elliman.com/agents/the-hamptons-north-fork',
		'https://www.elliman.com/agents/westchester',
		'https://www.elliman.com/agents/florida',
		'https://www.elliman.com/agents/california',
		'https://www.elliman.com/agents/connecticut',
		'https://www.elliman.com/agents/colorado',
		'https://www.elliman.com/agents/new-jersey',
	]

	proxy_lists = proxylist.proxys
	useragent_lists = useragent.user_agent_list

	def set_proxies(self, url, callback, headers=None):
		if headers:
			req = Request(url=url, callback=callback,dont_filter=True, headers=headers)
		else:
			req = Request(url=url, callback=callback,dont_filter=True)

		proxy_url = random.choice(self.proxy_lists)
		user_pass=base64.encodestring('amagca:Vztgn8fJ').strip().decode('utf-8')
		req.meta['proxy'] = "http://" + proxy_url
		req.headers['Proxy-Authorization'] = 'Basic ' + user_pass

		user_agent = random.choice(self.useragent_lists)
		req.headers['User-Agent'] = user_agent
		return req

	def start_requests(self):
		letter_str = "abcdefghijklmnopqrstuvwxyz"
		letter_str_list = list(letter_str)
		for letter in letter_str_list:
			for start_url in self.start_urls:
				url = start_url + "/" + letter

				print url

				req = self.set_proxies(url, self.parse_url)
				yield req

				return

	def parse_url(self, response):
		div_list = response.xpath("//div[@class='w_table']/table/tbody/tr")
		if len(div_list) > 0:
			for div_item in div_list:
				href_link = response.urljoin(div_item.xpath("td[@class='first']/a/@href").extract_first())
				name_str = div_item.xpath("td[@class='first']/a/text()").extract_first().strip().encode("utf8")
				email = div_item.xpath("td[@class='last']/a/text()").extract_first().strip().encode("utf8")

				# href_link = "https://www.elliman.com/real-estate-agent/annie-azzo/12407"
				req = self.set_proxies(href_link, self.parse_detail)
				req.meta["name"] = name_str
				req.meta["email"] = email
				req.meta["root"] = response.url
				yield req
				# return

	def parse_detail_addition(self, response):
		print "************ Addition ************", response.url
		picture_url = response.xpath("//div[@class='photo']/img/@src").extract_first().strip().encode("utf8")

		contact_list = response.xpath("//div[@class='wysiwyg office-mobile _bigger']/p")
		
		office_phone_str = ""
		mobile_phone_str = ""
		fax_phone_str = ""
		address_info = ""
		city_info = ""

		# Get Contact Information as list ( address, phone no)
		# print contact_list
		office_index = 0
		for j, contact_div in enumerate(contact_list):
			try:
				contact_item = contact_div.xpath(".//text()").extract_first().strip().encode("utf8")
			except:
				print contact_div

			if "Office:" in contact_item:
				office_index = j
				office_phone_str = contact_item.replace("Office:", "").replace(".", "-")
			elif "Mobile:" in contact_item:
				mobile_phone_str = contact_item.replace("Mobile:", "").replace(".", "-")
			elif "Fax:" in contact_item:
				fax_phone_str = contact_item.replace("Fax:", "").replace(".", "-")

			
		if office_index > 2:
			address_info = contact_list[office_index - 2].xpath(".//text()").extract_first().strip().encode("utf8")
			city_info = contact_list[office_index - 1].xpath(".//text()").extract_first().strip().encode("utf8")

		item = EllimanspiderItem()

		name_str = response.meta["name"]
		
		item["full_name"] = name_str
		item["last_name"] = name_str.split(",")[0]
		item["first_name"] = name_str.split(",")[1]
		item["full_address"] = address_info + " " + city_info
		item["address1"] = address_info
		item["address2"] = city_info.split(",")[0].strip()

		city_info_str = city_info.split(",")[1].strip()
		item["address3"] = city_info_str.split(' ')[0].strip()
		item["address4"] = city_info_str.split(' ')[1].strip()
		item["office"] = office_phone_str
		item["mobile"] = mobile_phone_str
		item["fax"] = fax_phone_str
		item["email"] = response.meta["email"]
		item["picture"] = picture_url
		item["url"] = response.url

		yield item

	def parse_detail(self, response):
		print "************", response.meta["root"], response.url
		try:
			picture_url = response.xpath("//div[@class='w_img_inner']/img/@src").extract_first().strip().encode("utf8")
		except:
			req = self.set_proxies(response.url + "/about", self.parse_detail_addition)
			req.meta["name"] = response.meta["name"]
			req.meta["email"] = response.meta["email"]
			yield req
			return

		detail_p = response.xpath("//div[@class='wysiwyg _dark _with_padding']/p").extract_first()
		
		if len(detail_p) > 0:
			detail_p = detail_p.strip().encode("utf8")
			detail_p_list = detail_p.split("<br><br>")

			# there are detail information inside P Element and it is divided by <br><br>
			if len(detail_p_list) > 0:
				for i, detail_item in enumerate(detail_p_list):
					if i > 0:
						contact_list = detail_item.split("<br>")
						
						office_phone_str = ""
						mobile_phone_str = ""
						fax_phone_str = ""
						address_info = ""
						city_info = ""

						# Get Contact Information as list ( address, phone no)
						for j, contact_item in enumerate(contact_list):
							if "Office:" in contact_item:
								office_phone_str = contact_item.replace("Office:", "").replace("</p>", "").replace(".", "-")
							elif "Mobile:" in contact_item:
								mobile_phone_str = contact_item.replace("Mobile:", "").replace("</p>", "").replace(".", "-")
							elif "Fax:" in contact_item:
								fax_phone_str = contact_item.replace("Fax:", "").replace("</p>", "").replace(".", "-")

							if j == 0:
								address_info = contact_item
							elif j == 1:
								city_info = contact_item

						item = EllimanspiderItem()

						name_str = response.meta["name"]
						
						item["full_name"] = name_str
						item["last_name"] = name_str.split(",")[0]
						item["first_name"] = name_str.split(",")[1]
						item["full_address"] = address_info + " " + city_info
						item["address1"] = address_info
						item["address2"] = city_info.split(",")[0].strip()

						city_info_str = city_info.split(",")[1].strip()
						item["address3"] = city_info_str.split(' ')[0].strip()
						item["address4"] = city_info_str.split(' ')[1].strip()
						item["office"] = office_phone_str
						item["mobile"] = mobile_phone_str
						item["fax"] = fax_phone_str
						item["email"] = response.meta["email"]
						item["picture"] = picture_url
						item["url"] = response.url

						yield item
