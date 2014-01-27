import datetime, time, random, feedparser, unicodedata, urllib2, twitter 
from collections import OrderedDict
feeds = []
class Twitterbot:
	def __init__(self):
		self.msgqueue = []
		self.postedMsgs = []
		self.api = twitter.Api(consumer_key='', consumer_secret='', access_token_key='', access_token_secret='')
		self.nextTweet = datetime.datetime.now() + datetime.timedelta(minutes=-1)
		self.queueAge = datetime.datetime.now() 
	def queueStatus(self, status, url):
		fullstatus = status + " - " + url
		if status not in self.postedMsgs:
			truncatePnt = len(fullstatus)
			while(len(fullstatus) > 140):
				fullstatus = status[:truncatePnt] + " - " + url
				truncatePnt -= 1
			self.msgqueue.append(fullstatus)
			self.postedMsgs.append(status)
			self.queueAge = datetime.datetime.now() 
	def postStatus(self):
		#{TWITTER API/LIBRARY CODE INSTEAD OF THIS MSG}
		td = datetime.datetime.now() - self.queueAge
		if(td.seconds > 7200):
			self.queueAge = []
			self.msgqueue = []
		else:
			while(datetime.datetime.now() < self.nextTweet):
				time.sleep(0.2)
			try:
				self.api.PostUpdate(self.msgqueue[0])
				print self.msgqueue[0] + " tweeted!"
			except:
				print self.msgqueue[0] + " FAILED!"
			self.msgqueue.pop(0)
			self.nextTweet = datetime.datetime.now() + datetime.timedelta(seconds=random.randint(37,300))
	def readyForMore(self):
		if(len(self.msgqueue) > 1):
			return False
		else:
			return True
class feedreader:
	def __init__(self, feeds):
		self.feedlist = feeds
		self.feedupdate = {}
		self.knownarticles = []
		for feed in feeds:
			self.feedupdate[feed] = datetime.datetime.now() + datetime.timedelta(minutes=-1)
	def createRefLink(self, url):

		r = urllib2.urlopen('http://api.adf.ly/api.php?key=[api]&uid=702569&advert_type=int&domain=[url]&url=' + url)
		return r.read()
	def getArticles(self, url):
		digestedArticles = {}
		articles = feedparser.parse(url)
		for article in articles.entries:
			if self.convertUnicode(article.title) not in self.knownarticles:
				digestedArticles[self.convertUnicode(article.title)] = self.createRefLink(self.convertUnicode(article.link).split('#')[0])
				self.knownarticles.append(self.convertUnicode(article.title))
		return digestedArticles
	def convertUnicode(self, text):
		if(type(text) is unicode):
			return unicodedata.normalize('NFKD', text).encode('ascii','ignore')
		else:
			return str(text)
	def getFeeds(self):
		articles = {}
		for feed in self.feedlist:
			if(datetime.datetime.now() > self.feedupdate[feed]):
				articles = dict(articles.items() + self.getArticles(feed).items())
				self.feedupdate[feed] = datetime.datetime.now() + datetime.timedelta(hours=1)
		oddarticles = articles.items()
		random.shuffle(oddarticles)
		return OrderedDict(oddarticles)
	def checkFeed(self):
		for feed in self.feedupdate:
			if(datetime.datetime.now() > self.feedupdate[feed]):
				return True
			return False
def mainLoop():
	while True:
		articles = {}
		if(tbot.readyForMore() == True):
			if(fd.checkFeed() == True):
				articles = fd.getFeeds()
				#print "got %s articles" % (len(articles))
				for article in articles.keys():
					tbot.queueStatus(article, articles[article])
		else:
			tbot.postStatus()
			#time.sleep(1)
		time.sleep(0.2)
		
		
tbot = Twitterbot()
fd = feedreader(feeds)
mainLoop()