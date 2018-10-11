# ScrapyVideoSpider

***
Scrape the webpage [xinpianchang](xinpianchang.com) according to the increasing of the id number, likes "/a{num}?from=ArticleList".
	This project takes advantage of the python web scraping framework `scrapy`. Besides that, due to the framework don't support multithreading, I also add a video downloader which can download the video faster. At the end of the process, the module in DB_IN.py will insert the data into mysql database that were scraped and processed by scrapy and the downloader sequentially.
	
