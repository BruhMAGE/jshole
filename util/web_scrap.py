"""
OWASP Maryam!

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import concurrent.futures
from util import page_parse,urlib
import requests
# Web Scraper v5.1

class main:

	def __init__(self, url, debug=False, limit=1, thread_count=1):
		""" web scraper with thread support

			url		  	 : first page address
			debug	  	 : show the result at moment
			limit	  	 : web scrap level(if it's 1 that's mean just search in first page)
			thread_count : count of links for open at per lap
		"""
		# ADD http:// 
		self.url = urlib.main(url).sub_service(serv='http')
		self.urlib = urlib.main
		self.debug = debug
		self.limit = limit
		self.thread_count = thread_count
		self._CATEGORY_PAGES = {}
		self._PAGES = ''
		self._LINKS = []
		self._OUT_SCOPE_LINKS = []
		self._QUERY_LINKS = []
		self._PHONES = []
		self._CSS = []
		self._JS = []
		self._CDNs = []
		self._MEDIA = []
		self._COMMENTS = []
		self._EMAILS = []
		self._DNS = []
		self._CREDIT_CARDS = []
		self._NETWORKS = {}
		self.numerator = 0
		self.media_exts = ('aa', 'aac', 'aif', 'aiff', 'amr', 'amv', 'amz', 'ape', 'asf', 'au', 'bash', 'bat', 'bmp', 'c',
			'cfa', 'cpp', 'cs', 'csv', 'doc', 'docx', 'f4a', 'f4b', 'f4p', 'f4v', 'flac', 'flv', 'gif', 'gif', 'gifv', 'gz',
			'ico', 'java', 'jfif', 'jpeg', 'jpg', 'm2v', 'm4a', 'm4p', 'm4v', 'md', 'mkv', 'mng', 'mov', 'mp2', 'mp3',
			'mp4', 'mpeg', 'mpg', 'mpv', 'pdf', 'pl', 'png', 'ppt', 'pptx', 'pptx', 'py', 'rar', 'rm', 'roq', 'svg', 'svi',
			'tar.gz', 'tiff', 'vmo', 'vob', 'w64', 'wav', 'webm', 'wma', 'wmv', 'wmv', 'woff2', 'wrk', 'wvavi', 'xlsx',
			'yaml', 'yml', 'zip')
		self.passed = []

	# If key not in links append it
	def rept(self, key, _list):
		if type(key) is list:
			for i in key:
				i = str(i)
				if i not in _list:
					_list.append(i)
		else:
			if key not in _list:
				_list.append(key)
		return _list

	def debuger(self, val):
		if self.debug:
			print(f"[*] {val}")

	def add_networks(self, data):
		# Add social nets
		for i in data:
			if i not in self._NETWORKS:
				self._NETWORKS[i] = data[i]
			else:
				self._NETWORKS[i] = self.rept(data[i], self._NETWORKS[i])

	def add_cdn(self, link):
		cond = link[:2] == '//' and '.' in link and link not in self._CDNs
		if cond:
			self.debuger(f'cdn: {link}')
			self.rept(link, self._CDNs)
			return True

	def add_phone(self, link):
		cond = link[:6] == "tel://"
		if cond:
			self.debuger(f'phone: {link}')
			self.rept(link, self._PHONES)
			return True

	def add_email(self, link):
		cond = link.startswith("mailto:")
		if cond:
			self.debuger(f'email: {link[6:]}')
			self.rept(link[6:], self._EMAILS)
			return True

	def joiner(self, url):
		urparse = self.urlib(url)
		urparse.url = urparse.quote if '%' not in url else url
		urparse2 = self.urlib(self.url)
		cond1 = url.lower() in ('%20', '', '/', '%23', '#', 'https:', 'http:')
		cond12 = url.endswith(':')
		cond2 = len(
			urparse.url) > 1 and '%3a//' not in urparse.url and urparse.url[:2] != '//'
		cond3 = urparse.url[:2] == '//'
		if cond1 or cond12:
			return False
		elif cond2:
			urparse.url = urparse2.join(url)
		elif cond3:
			urparse.url = url
		else:
			urparse.url = urparse2.join(url)
		return urparse.url

	def link_category(self, urls):
		links = []
		for url in urls:
			join = self.joiner(url)
			urlparse2 = self.urlib(join)
			##########################
			# ADD CDN, PHONE and EMAIL
			##########################
			cond1 = not join or (self.add_cdn(url) or self.add_phone(url) or self.add_email(url))
			if cond1:
				continue
			##########################
			# ADD MEDIA FILES
			##########################
			broke = 0
			for ext in self.media_exts:
				if urlparse2.check_urlfile(ext):
					self._MEDIA = self.rept(join, self._MEDIA)
					broke = 1
					break

			if broke:
				continue
			##############################
			# ADD JavaScript and CSS files
			##############################
			if urlparse2.check_urlfile('js'):
				self.debuger(f'js: {join}')
				self._JS = self.rept(join, self._JS)
				continue
			elif urlparse2.check_urlfile('css'):
				self.debuger(f'css: {join}')
				self._CSS = self.rept(join, self._CSS)
				continue
			join = str(join).replace('\/', '/')
			##########################
			# ADD OUT SCOPE
			##########################
			urparse = self.urlib(url)
			if urparse.netroot.lower() not in self.url.lower():
				self._OUT_SCOPE_LINKS = self.rept(join, self._OUT_SCOPE_LINKS)
				continue

			##########################
			# ADD QUERY
			##########################
			if urparse.query != '':
				self._QUERY_LINKS = self.rept(join, self._QUERY_LINKS)

			self._LINKS.append(join)
			links.append(join)
			self.debuger(join)
		return links

	def get_source(self, url):
		self.numerator += 1
		if url in self.passed:
			return []
		self.passed.append(url)
		# Send Request
		try:
			req = requests.get(url)
		except:
			return False
		else:
			resp = req.text

		pp = page_parse.main(resp)

		self.add_networks(pp.get_networks)
		self._EMAILS = self.rept(pp.all_emails, self._EMAILS)
		self._COMMENTS = self.rept(pp.get_html_comments, self._COMMENTS)

		# Get all links
		get_links_params = list(set(pp.get_links))

		links = self.link_category(get_links_params)
		self._PAGES += resp
		self._CATEGORY_PAGES[url] = resp
		return links

	def crawl_robots(self):
		print('Crawling robots.txt file...')
		try:
			robots = requests.get(f'http://www.{self.urlib(self.url).netroot}/robots.txt')
		except:
			return []
		if robots.status_code == 200:
			links = re.findall(r'Disallow: (.*)?', robots.text)
			links.extend(re.findall(r'Allow: (.*)?', robots.text))
			links.extend(re.findall(r'Sitemap: (.*)?', robots.text))
			makers = []
			for link in links:
				link = self.joiner(link)
				if link:
					makers.append(link)
			return makers
		return []

	def crawl_sitemap(self):
		print('Crawling sitemap.xml file...')
		try:
			sitemap = requests.get(f'http://www.{self.urlib(self.url).netroot}/sitemap.xml')
		except:
			return []
		if sitemap.status_code == 200:
			links = re.findall(r'<loc>(.*?)</loc>', sitemap.text) or []
			makers = []
			for link in links:
				if '*' not in link:
					link = self.joiner(link)
					if link:
						makers.append(link)
			return makers
		return []

	# attack function source : https://github.com/s0md3v/Photon
	def attack(self, function, links, thread_count):
		links = list(links)
		threadpool = concurrent.futures.ThreadPoolExecutor(
				max_workers=thread_count)
		futures = (threadpool.submit(function, link) for link in links if link not in self.passed)
		for i, _ in enumerate(concurrent.futures.as_completed(futures)):
			if i + 1 == len(links) or (i + 1) % thread_count == 0:
				print(f'Progress: {i+1}/{len(links)}',
						end='\r')
		print('')

	def run_crawl(self):
		links = self.get_source(self.url)
		if not links:
			return
		if self.limit == 1:
			return
		robmap = []
		print("[*] Checking robots.txt...")
		robmap.extend(self.crawl_robots())
		print("[*] Checking sitemap.xml...")
		robmap.extend(self.crawl_sitemap())
		robmap = list(set(links))
		links = self.link_category(robmap)
		links.extend(robmap)
		del robmap
		for depth in range(self.limit):
			if not links:
				break

			print(f"{self.limit} Level {depth+1}: {len(links)} URLs", end='\r')
			try:
				self.attack(self.get_source, list(set(self._LINKS)), self.thread_count)
			except KeyboardInterrupt:
				print('')
				break
		self._LINKS = list(set(self._LINKS))


	@property
	def pages(self):
		return self._PAGES

	@property
	def category_pages(self):
		return self._CATEGORY_PAGES

	@property
	def links(self):
		return self._LINKS

	@property
	def external_links(self):
		return self._OUT_SCOPE_LINKS

	@property
	def query_links(self):
		return self._QUERY_LINKS

	@property
	def js(self):
		return self._JS

	@property
	def css(self):
		return self._CSS

	@property
	def cdn(self):
		return self._CDNs

	@property
	def phones(self):
		return self._PHONES

	@property
	def comments(self):
		return self._COMMENTS

	@property
	def emails(self):
		return self._EMAILS

	@property
	def networks(self):
		return self._NETWORKS

	@property
	def media(self):
		return self._MEDIA
