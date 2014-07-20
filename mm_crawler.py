#!/etc/python2.7
#! -*- coding:utf-8 -*-
import sys
import os
import urllib2
import Queue
import threading
from BeautifulSoup import BeautifulSoup

"""

author : sooshian
date   : 2014.7.20

"""

class PageFinder(object):
	def __init__(self,):
		self.pages_queue = []

	def start_from_here(self,url):
		#load html
		r = urllib2.urlopen(url)
		res = r.read()
		
		#analysis
		soup = BeautifulSoup(res)

		rows = soup.find('div',attrs={'class':'ShowPage'}).nextSibling.contents
		count = 0
		pages = {}

		for row in range(len(rows)):
			cols = rows[row].contents
			if count == 5:
				break
			for col in range(len(cols)):
				key = cols[col].contents[0]['title']
				value = u'http://www.22mm.cc' + cols[col].contents[0]['href']
				pages[key] = value
			count += 1
		return pages


		

class ResourcesAnalysiser(object):
	def __init__(self,):
		pass

	def analysis(self,url):
		r = urllib2.urlopen(url)
		res = r.read()
		soup = BeautifulSoup(res)

		#find number of pictures
		temp = soup.find('div',attrs={'class':'ShowPage'}).contents[0].contents[1]
		num = int(temp[1:])
	
		return self.get(url.replace(".html","-%d.html" % num))


	def get(self,url):
		r = urllib2.urlopen(url)
		res = r.read()
		soup = BeautifulSoup(res)
		temp = soup.find('div',attrs={'id':'imgString'}).nextSibling.contents[0]
		spos = temp.find("http")
		epos = temp.find('";getImgString')

		return temp[spos:epos].replace("big","pic").split('";arrayImg[0]="')

class Downloader(threading.Thread):
	def __init__(self,queue,over):
		threading.Thread.__init__(self)
		self.queue = queue
		self.over = over

	def run(self):
		while not self.over:
			#wait for task
			if self.queue.empty():continue
			task = self.queue.get()

			path,url = task.items()[0]
			#print "downloading the file : ",url

			if path[-1] != '/':path=path+'/'
			res = ""
			try:
				#deal with chinese characters
				url_ = url[:5] + urllib2.quote(url[5:].encode('gbk'))
				r = urllib2.urlopen(url_)
				res = r.read()
			except urllib2.HTTPError:
				print "file does not exist ",url
			else:
				fn = url.replace(u'/','')
				fn = fn.replace(u'-','')
				f = open(path + fn[len(fn)-10:],'wb+')
				f.write(res)
				f.close()
			self.queue.task_done()


class mm_crawler():
	def __init__(self,path,numberOfThreads):
		self.path = path
		self.resources = Queue.Queue()
		self.numOfthread = numberOfThreads

	def crawl(self,url):
		work_path = self.path
		pf = PageFinder()
		ra = ResourcesAnalysiser()
		pages = pf.start_from_here(url)
		count = 1
		length = len(pages)
		
		self.over = False
		for i in range(self.numOfthread):
			t = Downloader(self.resources,self.over)
			t.setDaemon(True)
			t.start()

		for key in pages:
			print "[", count, "/", length, "] 正在下载 ", key, 
			new_path = os.path.join(work_path,key)
			if not os.path.isdir(new_path):
				os.makedirs(new_path)
				
				rs = ra.analysis(pages[key])
				print "(",len(rs),")"
				for item in rs:
					self.resources.put({new_path:item})
			else:
				print "略过"
			count+=1
			self.resources.join()
		self.over = True
		
path = './pics'
num_of_pages = 1
limit_of_pic = 0
num_of_threads = 10
type_of_pic = 'qingliang'
typename = '清凉'
for i in range(len(sys.argv)):
	if sys.argv[i].startswith('-'):
		opt = sys.argv[i][1:]
		if i != len(sys.argv) - 1:val = sys.argv[i+1]
		
		if opt == 'h':
			print "用法：mm_crawler.py [-t typeOfPictures ][-p numberOfPages ][-o path ][-n numberOfThreads ][-l limitOfPictures]"
			print "typeOfPictures\tql 清凉\n\t\tjy 惊艳"
			print "numberOfPages\t[1,2...] 页数"
			sys.exit(0)
		if opt == 'n':
			num_of_threads = int(val)
		if opt == 'o':
			path = val
		if opt == 'l':
			limit_of_pic = int(val)
		if opt == 'p':
			num_of_pages = int(val)
		if opt == 't':
			if val == 'jy':
				type_of_pic = 'jingyan'
				typename = '惊艳'
			elif val == 'ql':pass
			else:sys.exit(1)

cl = mm_crawler(path,num_of_threads)
print '当前分类',typename,'页数',num_of_pages
cl.crawl("http://www.22mm.cc/mm/%s/index_%d.html" % (type_of_pic,num_of_pages))
