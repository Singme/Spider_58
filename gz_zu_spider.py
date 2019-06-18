# encoding:utf-8

import csv
import time
from lxml import etree
from selenium import webdriver
import chardet
from fontTools.ttLib import TTFont
import re
import base64
from io import BytesIO


class GzSpider(object):
	def __init__(self):
		print("[INFO] driver init...")
		self.driver = webdriver.PhantomJS(executable_path=r'D:/phantomjs-2.1.1-windows/bin/phantomjs.exe')  # 指定PhantomJS的路径
		self.item_list = []

	def _font(self, bin_data, font_str):
		"""
		加密字体转换
		"""
		# ByteIO 把一个二进制内存块生成文件来操作
		font = TTFont(BytesIO(bin_data))
		# 将编码字体保存为xml
		font.saveXML('anjuke_2.xml')

		utfList = font['cmap'].tables[0].ttFont.tables['cmap'].tables[0].cmap
		retList = []
		getText2 = font_str

		for i in getText2:
			if ord(i) in utfList:
				text = int(utfList[ord(i)][-2:]) - 1
			else:
				text = i
			retList.append(text)

		crackText = ''.join([str(i) for i in retList])
		return crackText

	def save_data(self):
		with open('gz_zu.csv', 'w', encoding='utf-8') as f:
			sheet_name = self.item_list[0].keys()
			value_data = [data.values() for data in self.item_list]
			csv_writer = csv.writer(f)
			csv_writer.writerow(sheet_name)
			csv_writer.writerows(value_data)

	def main(self):
		self.driver.get("https://sz.zu.anjuke.com/")
		num = 0

		while num <= 0:
			html = self.driver.page_source
			pattern = re.compile(r"'.*;base64,(.*?)'")
			ret_list = pattern.findall(html)
			# 将base64编码的字体字符串解码成二进制编码
			binData = base64.decodebytes(ret_list[0].encode())
			with open('anjuke_2.otf', 'wb') as f:
				f.write(binData)

			html_obj = etree.HTML(html)

			node_list = html_obj.xpath("//div[@class='zu-itemmod']")
			for node in node_list:
				item = {}
				item["house_name"] = node.xpath(".//div[@class='zu-info']//address//a/text()")[0].strip()
				item["address"] = node.xpath(".//div[@class='zu-info']//address/text()")[1].strip()
				house_detail_list = node.xpath(".//div[@class='zu-info']//p[@class='details-item tag']")
				for detail in house_detail_list:
					data_list = detail.xpath(".//b/text()")
					try:
						room = self._font(binData, data_list[0])
					except:
						room = ''
					try:
						hall = self._font(binData, data_list[1])
					except:
						hall = ''
					try:
						square = self._font(binData, data_list[2])
					except:
						square = ''
					item["house_detail"] = u"{}室{}厅 {}平米".format(room, hall, square)
				money = node.xpath(".//div[@class='zu-side']//p//b/text()")[0].strip()
				money = self._font(binData, money)
				item["money"] = u"{}元/月".format(money)
				self.item_list.append(item)

			# if html.find("iNxt") != -1:
			# print("[INFO] over...")
			# 	break
			# print("[INFO] save img...")
			self.driver.save_screenshot('sz_zu_2.png')
			num += 1
			# self.driver.find_element_by_class_name('aNxt').click()
			# print("[INFO] cilck next page...")
			time.sleep(5)
		self.save_data()

	def __del__(self):
		print("[INFO] driver quit...")
		self.driver.quit()


if __name__ == '__main__':
	gz_spider = GzSpider()
	gz_spider.main()
