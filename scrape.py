from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def extractListingURLs(baseURL,searchURL):
	nextLink = "bigpotato"
	startLink = searchURL
	count = 0
	listingURLs = []
	while nextLink != "":
		if count == 0:
			nextLink = startLink

		baseurl = baseURL
		url = baseurl+nextLink

		r  = requests.get(baseurl + nextLink)

		data = r.text

		soup = BeautifulSoup(data,"lxml")

		nextLink = ""

		for link in soup.find_all('a',text='next > '):
			# print link['href']
			# Take the next page link
			nextLink = link['href']
		result = soup.find_all('a',{'class':'result-title hdrlnk'})
		if len(result) == 0:
			nextLink = ""
		else:
			for a in result:
				listingURLs += [a['href']]
		count = count + 1
		# print listingURLs
	return listingURLs

def valueListing(listingURL):
	listingURL = "https://worcester.craigslist.org/cto/d/volvo-s40/6381711338.html"
	r = requests.get(listingURL)
	data = r.text
	soup = BeautifulSoup(data,"lxml")

	attrs = soup.find_all('p',{'class':'attrgroup'})
	if len(attrs) > 0:
		typeStr = (attrs[0].find('b').text).lower()
		splitStr = typeStr.split()
		year = splitStr[0]
		make = splitStr[1]
		model = splitStr[2]
		# Now we have a car to work with, we need to figure out what type it is to plug into KBB
		# This is tricky, so we're just going to use the base vehicle.
		KBBstyles = getKBBStyles(year,make,model)
		# These URLs are coming out with a little bad stuff on them, such as a vehicleid, and /options/
		# which if left unremidied will make KBB ask too many questions
		# let's fix that

		# Also, we take the first body style (cheapest option)
		finalURL = 'https://www.kbb.com/'+make+'/'+model+'/'+year+'/'+KBBstyles[0]+'/?intent=buy-used&pricetype=private-party&condition=good&persistedcondition=good'
		price = getKBBPrice(finalURL)

def getKBBPrice(vehicleURL):
	driver = webdriver.PhantomJS('phantomjs',service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
	driver.implicitly_wait(10) # seconds
	driver.get(vehicleURL)
	myDynamicElement = driver.find_element_by_id("RangeBox")
	print myDynamicElement

	html = driver.page_source

	# html = '<g xmlns="http://www.w3.org/2000/svg" id="RangeBox" transform="translate(180,113)" data-reactid="50"><path d="m 0,-40 l -87,0 l 0,-42 a 5,5 0 0,1 5,-5 l 164,0 a 5,5 0 0,1 5,5 l 0,42 z" fill="#559c56" stroke="#9BA6B3" stroke-width="1" data-reactid="51"/><path d="m 0,0 l -82,0 a 5,5 0 0,1 -5,-5 l 0,-35 l 174,0 l 0,35 a 5,5 0 0,1 -5,5 z" fill="#ffffff" stroke="#9BA6B3" stroke-width="1" data-reactid="52"/><text text-anchor="middle" font-size="14" font-weight="700" fill="#333333" y="-8" data-reactid="53"><!-- react-text: 54 -->$3,523<!-- /react-text --><tspan font-weight="400" data-reactid="55"> ($70/month)*</tspan></text><text text-anchor="middle" font-size="14" font-weight="400" fill="#333333" y="-26" data-reactid="56">Private Party Value</text><!-- react-text: 57 -->-48<!-- /react-text --><text text-anchor="middle" font-size="20" font-weight="700" fill="#ffffff" y="-48" data-reactid="58"><!-- react-text: 59 -->$3,166 - $4,280<!-- /react-text --></text><!-- react-text: 60 -->-50.8<!-- /react-text --><text text-anchor="middle" font-size="14" font-weight="400" fill="#ffffff" y="-68.8" data-reactid="61">Private Party Range</text></g>'
	print html
	print '$3,1' in html
	soup = BeautifulSoup(html, 'html.parser')
	g = soup.find_all('g',{'id':'RangeBox'})
	print g

def getKBBStyles(year,make,model):
	r = requests.get('https://www.kbb.com/'+make+'/'+model+'/'+year+'/styles/')
	data = r.text
	soup = BeautifulSoup(data,"lxml")
	styleElems = soup.find_all('a',{'class':'right btn-main-cta'})
	styles = []
	for style in styleElems:
		KBBURL = style['href']
		styles += [KBBURL.split('/')[4]]

	return styles

# listingURLs = extractListingURLs("https://worcester.craigslist.org","/search/cta?query=volvo&sort=date&searchNearby=2&nearbyArea=59&nearbyArea=4&nearbyArea=239&nearbyArea=451&nearbyArea=281&nearbyArea=686&nearbyArea=44&nearbyArea=249&nearbyArea=250&nearbyArea=169&nearbyArea=198&nearbyArea=168&nearbyArea=3&nearbyArea=354&nearbyArea=338&nearbyArea=38&nearbyArea=378&nearbyArea=93&nearbyArea=173&min_price=100&max_price=3000")
# print len(listingURLs)

valueListing('')
