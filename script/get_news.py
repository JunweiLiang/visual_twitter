# coding=utf-8
# given a list of new url, download to path

import sys,os,argparse,scrapy,io
from scrapy.crawler import CrawlerProcess
import logging


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("newslst")
	parser.add_argument("outpath")
	return parser.parse_args()


def process_news(response,newsname):
	proc = {
	# using xpath selector instead of css since need all children's text
		"cnn":'//div[contains(@class,"zn-body__paragraph")]//text()',
		"businessinsider": '//div[contains(@class,"slide-module")]/p//text()',
		"fox":'//div[contains(@class,"article-body")]/p//text()',
		"latimes":'//div[contains(@class,"trb_ar_page")]/p//text()',
		"huffingtonpost":'//div[contains(@class,"content-list-component bn-content-list-text yr-content-list-text text")]/p//text()',
		"reuters":'//div[contains(@class,"StandardArticleBody_body_1gnLA")]/p//text()',
		"usatoday":'//div[contains(@class,"asset-double-wide double-wide p402_premium")]/p[contains(@class,"p-text")]//text()',
		"bbc":'//div[contains(@class,"story-body__inner")]/p//text()',
		"billboard":'//div[contains(@class,"article__body js-fitvids-content")]/p//text()'
	}
	texts = []
	#for elem in response.css(proc[newsname]).extract():
	for elem in response.xpath(proc[newsname]).extract():
		#print elem
		texts.append(elem)
	return texts

class NewsSpider(scrapy.Spider):
	name = "news"
	def __init__(self,news=None,outpath=None,*args,**kwargs):
		# news should be a (name,url) tuple
		super(NewsSpider,self).__init__(*args,**kwargs)
		self.news = news
		self.outpath = outpath

	def start_requests(self):

		for name,url in self.news:
			yield scrapy.Request(url,callback=self.parse,meta={"name":name}) # use meta to pass args to parse function

	def parse(self,response):
		newsname = response.meta['name']
		texts = process_news(response,newsname)
		f = io.open(os.path.join(self.outpath,"%s.txt"%newsname),"w",encoding="utf-8")
		for text in texts:
			f.writelines("%s\n"%(text))
		f.close()
		



if __name__ == "__main__":
	args = get_args()
	news = [line.strip().split() for line in open(args.newslst,"r").readlines()]

	if not os.path.exists(args.outpath):
		os.makedirs(args.outpath)

	process = CrawlerProcess({
	    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
	})

	logging.getLogger('scrapy').setLevel(logging.ERROR)

	process.crawl(NewsSpider,news=news,outpath=args.outpath) # pass args for NewsSpider here, stupid scrapy
	process.start()
	
